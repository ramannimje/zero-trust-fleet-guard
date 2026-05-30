import { AlertRecord } from '../App'

interface ThreatFeedProps {
  alerts: AlertRecord[]
  onSelectDevice: (deviceId: string) => void
}

export default function ThreatFeed({ alerts, onSelectDevice }: ThreatFeedProps) {
  return (
    <div>
      <h2>Active Compliance Alerts</h2>
      <p>Automated audit trail diagnostics and active sequence for non-compliant endpoints.</p>
      <ul className="alert-list">
        {alerts.map((alert) => (
          <li
            key={`${alert.device_id}-${alert.alerted_at}`}
            className="alert-item"
            onClick={() => onSelectDevice(alert.device_id)}
          >
            <strong>{alert.device_id}</strong>
            <span className={`alert-pill ${alert.status === 'NON_COMPLIANT' ? 'danger' : 'warning'}`}>
              {alert.status}
            </span>
            <div className="alert-copy">Risk score {alert.risk_score} — {alert.breached_policies.join(', ')}</div>
            <small>{new Date(alert.alerted_at).toLocaleTimeString()}</small>
          </li>
        ))}
      </ul>
    </div>
  )
}
