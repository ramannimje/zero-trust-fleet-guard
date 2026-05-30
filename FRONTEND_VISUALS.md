# FRONTEND_VISUALS.md

## Screenshot Strategy for Enterprise Portfolio

This document describes how to capture the key UI flows that show AirShield Compliance as a polished enterprise mobility solution.

### Screenshot 1: The Zero-Trust Security Perimeter View

- Show the main dashboard with the Leaflet map view prominently displayed.
- Include the green geofence boundary overlay around the corporate campus perimeter.
- Display device markers inside the perimeter in green and at least one red alert marker outside the boundary.
- Ensure the title `AirShield Compliance` and the top status pill are visible.
- Capture the alert feed panel on the right with a red `NON_COMPLIANT` alert entry.

### Screenshot 2: Structured AI Audit Trail Panel

- Click a flagged device marker or an alert feed item to reveal the audit pane.
- Show the `Device Audit Trail & Payload` section with the left box containing the raw JSON payload and the right box containing the structured AI evaluation.
- Make sure the AI output includes `risk_score`, `breached_policies`, `recommended_actions`, and `justification_audit_trail`.
- The screenshot should emphasize the clean dual-pane presentation and the enterprise-style JSON audit support.

### Screenshot 3: Automated Isolation Vector

- Highlight a device with `NON_COMPLIANT` status in the alert feed.
- Ensure the `compliance_status` or action tags show a lockdown event, such as active `revoke_corporate_email_certificates` and `push_kiosk_mode_lockdown` responses.
- Capture the audit pane text showing a mitigation decision and the alert entry describing a perimeter breach or forbidden application.
- Use the device marker popup or selected side panel to convey the automated remediation sequence.

### Screenshot 4: Continuous Fleet Monitoring Story

- Display a time-series of multiple alerts in the feed panel to show ongoing monitoring.
- Include devices both inside and outside the secure perimeter.
- Show the dashboard header and summary count of non-compliant devices.
- Use this screenshot to demonstrate how the platform scales from perimeter awareness to active incident response.

## Styling Notes for Marketing

- Use a dark, premium visual palette with neon highlights for compliant vs. non-compliant status.
- Keep the map interface clear and uncluttered, with the enterprise campus polygon visible.
- Use the alert feed typography to present incident details as concise, high-value executive risk statements.
- The audit trail panel should look like a polished compliance console, not raw developer logs.

## Capture Guidance

- Use browser dev tools or full-screen mode to capture the web app at 1440x900 or higher.
- Zoom the map area slightly if needed to show both the perimeter and the alerted device.
- For the audit trail view, make sure the JSON panels are sized evenly.
- Save screenshots with descriptive filenames such as:
  - `01_zero_trust_perimeter.png`
  - `02_structured_audit_trail.png`
  - `03_automated_isolation.png`
  - `04_continuous_fleet_monitoring.png`
