import asyncio
from datetime import datetime


async def revoke_corporate_email_certificates(device_id: str) -> dict:
    await asyncio.sleep(0.1)
    action = {
        "device_id": device_id,
        "action": "revoke_corporate_email_certificates",
        "status": "executed",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    print("[Mitigation] revoked corporate email certificates for", device_id)
    return action


async def push_kiosk_mode_lockdown(device_id: str) -> dict:
    await asyncio.sleep(0.1)
    action = {
        "device_id": device_id,
        "action": "push_kiosk_mode_lockdown",
        "status": "executed",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    print("[Mitigation] pushed kiosk mode lockdown for", device_id)
    return action


async def trigger_admin_security_pager(device_id: str, reasons: list[str]) -> dict:
    await asyncio.sleep(0.1)
    action = {
        "device_id": device_id,
        "action": "trigger_admin_security_pager",
        "status": "executed",
        "reasons": reasons,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    print("[Mitigation] triggered admin pager for", device_id, "reasons=", reasons)
    return action


MITIGATION_ACTIONS = {
    "revoke_corporate_email_certificates": revoke_corporate_email_certificates,
    "push_kiosk_mode_lockdown": push_kiosk_mode_lockdown,
    "trigger_admin_security_pager": trigger_admin_security_pager,
}
