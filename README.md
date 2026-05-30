# AirShield-Compliance

AirShield-Compliance is a production-ready reference implementation for enterprise-grade zero-trust fleet security, compliance, and automated isolation. It demonstrates a defensive asynchronous backend, structured AI governance with Pydantic v2, deterministic mitigation hooks, geofencing trust evaluation, and a React dashboard with real-time risk telemetry.

## Architecture

- `backend/` — FastAPI async ingestion service, structured policy evaluation, mitigation execution, and SQLite audit logging.
- `frontend/` — Vite + React TypeScript dashboard with Leaflet mapping, alert feed, and audit trail inspection.
- `FRONTEND_VISUALS.md` — portfolio screenshot guidance for enterprise hiring managers.

## Backend Overview

- `backend/app/schemas.py` defines `DeviceStatePayload` and `AgentSecurityEvaluation`.
- `backend/app/main.py` receives telemetry via `/ingest`, enqueues it, evaluates asynchronously, and logs actions.
- `backend/app/policy_agent.py` implements a strict governance layer and deterministic compliance scoring.
- `backend/app/mitigation_tools.py` contains mock endpoint hooks for certificate revocation, kiosk lockdown, and pager escalation.
- `backend/device_security_simulator.py` simulates 50 devices sending telemetry to the ingestion API.

## Frontend Overview

- `frontend/src/components/SecurityMap.tsx` visualizes device markers and the corporate perimeter.
- `frontend/src/components/ThreatFeed.tsx` displays live non-compliant alerts.
- `frontend/src/components/ComplianceAuditor.tsx` surfaces raw payloads and structured justification.

## Getting Started

### Backend

1. Navigate to `airshield-compliance/backend`
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Start the backend:
   ```bash
   uvicorn app.main:app --reload
   ```
4. In another terminal, run the simulator:
   ```bash
   python device_security_simulator.py
   ```

### Frontend

1. Navigate to `airshield-compliance/frontend`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dashboard:
   ```bash
   npm run dev
   ```
4. Open the local development URL and watch devices, alerts, and audit trails update in real time.

## Notes

- The AI governance layer is built for structured JSON outputs using Pydantic validation.
- The app uses a geospatial trust matrix to compare GPS coordinates against the corporate perimeter.
- Mitigation actions are intentionally deterministic and mock enterprise enforcement hooks.
