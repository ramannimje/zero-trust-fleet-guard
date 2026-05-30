from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ActionName = Literal[
    "revoke_corporate_email_certificates",
    "push_kiosk_mode_lockdown",
    "trigger_admin_security_pager",
]
ComplianceStatus = Literal["COMPLIANT", "WARNING", "NON_COMPLIANT"]


class DeviceStatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: str
    latitude: float
    longitude: float
    installed_applications: list[str]
    is_rooted_or_jailbroken: bool
    os_patch_level: str


class AgentSecurityEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: str
    risk_score: int = Field(0, ge=0, le=100)
    compliance_status: ComplianceStatus
    breached_policies: list[str]
    recommended_actions: list[ActionName]
    justification_audit_trail: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class Geofence(BaseModel):
    name: str
    polygon: list[tuple[float, float]]
