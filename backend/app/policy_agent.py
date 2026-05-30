import json
import os
from typing import Any

from pydantic import ValidationError

from .schemas import AgentSecurityEvaluation, DeviceStatePayload, Geofence

FORBIDDEN_APPLICATIONS = [
    "spoofed-vpn",
    "shadow-admin",
    "credential-extractor",
    "enterprise-spoof",
]


def _is_inside_geofence(latitude: float, longitude: float, polygon: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        yi, xi = polygon[i]
        yj, xj = polygon[j]
        intersect = ((xi > longitude) != (xj > longitude)) and (
            latitude < (yj - yi) * (longitude - xi) / (xj - xi + 1e-9) + yi
        )
        if intersect:
            inside = not inside
        j = i
    return inside


class PolicyAgent:
    def __init__(self) -> None:
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.use_llm = bool(self.openai_api_key or self.anthropic_api_key)

    def evaluate(self, payload: DeviceStatePayload, geofence: Geofence) -> AgentSecurityEvaluation:
        if self.use_llm:
            return self._evaluate_with_llm(payload, geofence)
        return self._evaluate_locally(payload, geofence)

    def _evaluate_locally(self, payload: DeviceStatePayload, geofence: Geofence) -> AgentSecurityEvaluation:
        risk_score = 0
        breached_policies: list[str] = []
        recommended_actions: list[str] = []
        reasons: list[str] = []

        inside_geofence = _is_inside_geofence(payload.latitude, payload.longitude, geofence.polygon)
        if not inside_geofence:
            breached_policies.append("geofence_breach")
            risk_score += 30
            reasons.append("Device is outside the protected perimeter")

        forbidden_apps = [app for app in payload.installed_applications if app in FORBIDDEN_APPLICATIONS]
        if forbidden_apps:
            breached_policies.append("forbidden_application_installed")
            risk_score += 30
            reasons.append(f"Forbidden application installed: {', '.join(forbidden_apps)}")

        if payload.is_rooted_or_jailbroken:
            breached_policies.append("rooted_or_jailbroken_device")
            risk_score += 30
            reasons.append("Device has root or jailbreak status")

        if payload.os_patch_level < "2024-01" or payload.os_patch_level.startswith("2023"):
            breached_policies.append("outdated_os_patch")
            risk_score += 10
            reasons.append("Device patch level is stale relative to enterprise policy")

        if risk_score >= 70:
            recommended_actions = [
                "revoke_corporate_email_certificates",
                "push_kiosk_mode_lockdown",
                "trigger_admin_security_pager",
            ]
        elif risk_score >= 40:
            recommended_actions = ["trigger_admin_security_pager"]
        else:
            recommended_actions = []

        compliance_status = (
            "NON_COMPLIANT"
            if risk_score >= 70
            else "WARNING"
            if risk_score >= 40
            else "COMPLIANT"
        )

        justification = (
            " | ".join(reasons)
            or "Device state is fully compliant with the zero-trust baseline policy."
        )

        evaluation = {
            "device_id": payload.device_id,
            "risk_score": min(risk_score, 100),
            "compliance_status": compliance_status,
            "breached_policies": breached_policies,
            "recommended_actions": recommended_actions,
            "justification_audit_trail": justification,
        }

        try:
            return AgentSecurityEvaluation.model_validate(evaluation)
        except ValidationError as exc:
            raise RuntimeError("Policy evaluation produced invalid structured output") from exc

    def _evaluate_with_llm(self, payload: DeviceStatePayload, geofence: Geofence) -> AgentSecurityEvaluation:
        prompt = self._build_prompt(payload, geofence)
        if self.openai_api_key:
            return self._evaluate_with_openai(prompt)
        if self.anthropic_api_key:
            return self._evaluate_with_anthropic(prompt)
        return self._evaluate_locally(payload, geofence)

    def _build_prompt(self, payload: DeviceStatePayload, geofence: Geofence) -> str:
        return (
            "You are a strict security evaluation engine. Respond only with valid JSON matching the schema keys: "
            "device_id, risk_score, compliance_status, breached_policies, recommended_actions, justification_audit_trail. "
            "Do not output any additional prose. Evaluate the provided telemetry against the enterprise geofence and policy definitions.\n"
            f"Geofence polygon: {geofence.polygon}\n"
            f"Telemetry: {json.dumps(payload.model_dump())}\n"
            "Use compliance_status values COMPLIANT, WARNING, or NON_COMPLIANT. "
            "Actions must be selected from revoke_corporate_email_certificates, push_kiosk_mode_lockdown, trigger_admin_security_pager."
        )

    def _evaluate_with_openai(self, prompt: str) -> AgentSecurityEvaluation:
        try:
            import openai
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is not installed") from exc
        openai.api_key = self.openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        text = response.choices[0].message["content"]
        return self._parse_llm_output(text)

    def _evaluate_with_anthropic(self, prompt: str) -> AgentSecurityEvaluation:
        try:
            from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
        except Exception as exc:
            raise RuntimeError("Anthropic SDK is not installed") from exc
        client = Anthropic(api_key=self.anthropic_api_key)
        payload = f"{HUMAN_PROMPT}{prompt}{AI_PROMPT}"
        response = client.completions.create(
            model="claude-3.5-opus",
            prompt=payload,
            max_tokens_to_sample=500,
            temperature=0,
        )
        text = response.completion
        return self._parse_llm_output(text)

    def _parse_llm_output(self, text: str) -> AgentSecurityEvaluation:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM output was not valid JSON") from exc
        try:
            return AgentSecurityEvaluation.model_validate(parsed)
        except ValidationError as exc:
            raise RuntimeError("LLM structured response did not validate") from exc
