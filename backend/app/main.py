import asyncio
import json
from datetime import datetime
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .database import AuditDatabase
from .mitigation_tools import MITIGATION_ACTIONS, trigger_admin_security_pager
from .policy_agent import PolicyAgent
from .schemas import DeviceStatePayload, Geofence

app = FastAPI(title="AirShield Compliance Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

queue: asyncio.Queue[DeviceStatePayload] = asyncio.Queue()
audit_db: AuditDatabase = AuditDatabase()
policy_agent = PolicyAgent()

HIGH_SECURITY_GEOFENCE = Geofence(
    name="AirShield Corporate Campus",
    polygon=[
        (37.7855, -122.4010),
        (37.7855, -122.3930),
        (37.7800, -122.3930),
        (37.7800, -122.4010),
    ],
)

latest_device_states: dict[str, dict[str, Any]] = {}
recent_alerts: list[dict[str, Any]] = []


@app.on_event("startup")
async def startup_event() -> None:
    await audit_db.initialize()
    asyncio.create_task(_worker_loop())


@app.post("/ingest")
async def ingest_device_state(payload: DeviceStatePayload) -> dict:
    await queue.put(payload)
    return {"status": "accepted", "device_id": payload.device_id}


@app.get("/status")
async def get_status() -> dict:
    return {
        "geofence": HIGH_SECURITY_GEOFENCE.model_dump(),
        "devices": list(latest_device_states.values()),
        "alerts": recent_alerts[-50:],
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "queue_size": queue.qsize()}


async def _execute_actions(payload: DeviceStatePayload, evaluation: Any) -> list[dict[str, Any]]:
    executed: list[dict[str, Any]] = []
    if evaluation.recommended_actions:
        reasons = evaluation.breached_policies
        for action_name in evaluation.recommended_actions:
            action = MITIGATION_ACTIONS.get(action_name)
            if action is None:
                continue
            if action_name == "trigger_admin_security_pager":
                result = await action(payload.device_id, reasons)
            else:
                result = await action(payload.device_id)
            executed.append(result)
            await audit_db.log_event(
                payload.device_id,
                "mitigation_action",
                json.dumps(result),
                datetime.utcnow().isoformat() + "Z",
            )
    return executed


async def _worker_loop() -> None:
    while True:
        payload = await queue.get()
        try:
            evaluation = policy_agent.evaluate(payload, HIGH_SECURITY_GEOFENCE)
        except (RuntimeError, ValidationError) as exc:
            raise HTTPException(status_code=500, detail=str(exc))

        latest_device_states[payload.device_id] = {
            "device_id": payload.device_id,
            "payload": payload.model_dump(),
            "evaluation": evaluation.model_dump(),
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }

        await audit_db.upsert_device_status(
            payload.device_id,
            json.dumps(payload.model_dump()),
            json.dumps(evaluation.model_dump()),
            datetime.utcnow().isoformat() + "Z",
        )

        event = {
            "device_id": payload.device_id,
            "event_type": "evaluation",
            "payload": json.dumps(evaluation.model_dump()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await audit_db.log_event(
            payload.device_id,
            "evaluation",
            event["payload"],
            event["timestamp"],
        )

        if evaluation.compliance_status != "COMPLIANT":
            alert = {
                "device_id": payload.device_id,
                "status": evaluation.compliance_status,
                "risk_score": evaluation.risk_score,
                "breached_policies": evaluation.breached_policies,
                "justification_audit_trail": evaluation.justification_audit_trail,
                "alerted_at": datetime.utcnow().isoformat() + "Z",
            }
            recent_alerts.append(alert)
            await audit_db.log_event(
                payload.device_id,
                "alert",
                json.dumps(alert),
                alert["alerted_at"],
            )
        actions = await _execute_actions(payload, evaluation)
        if actions:
            latest_device_states[payload.device_id]["actions"] = actions
        queue.task_done()
