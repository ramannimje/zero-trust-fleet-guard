import { DeviceStatus } from '../App'

interface ComplianceAuditorProps {
  device: DeviceStatus | null
}

export default function ComplianceAuditor({ device }: ComplianceAuditorProps) {
  if (!device) {
    return (
      <section className="audit-panel">
        <h2 className="audit-title">Select a device to inspect</h2>
        <p>Click a flagged marker or alert to reveal the JSON payload and structured AI audit trail.</p>
      </section>
    )
  }

  return (
    <section className="audit-panel">
      <h2 className="audit-title">Device Audit Trail & Payload</h2>
      <div className="audit-row">
        <div className="audit-box">
          <strong>Payload</strong>
          <pre>{JSON.stringify(device.payload, null, 2)}</pre>
        </div>
        <div className="audit-box">
          <strong>AI Structured Evaluation</strong>
          <pre>{JSON.stringify(device.evaluation, null, 2)}</pre>
        </div>
      </div>
    </section>
  )
}
