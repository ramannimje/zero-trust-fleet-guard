import { useEffect, useMemo, useState } from 'react'
import SecurityMap from './components/SecurityMap'
import ThreatFeed from './components/ThreatFeed'
import ComplianceAuditor from './components/ComplianceAuditor'

export interface DeviceStatus {
  device_id: string
  payload: Record<string, any>
  evaluation: Record<string, any>
  updated_at: string
  actions?: any[]
}

export interface AlertRecord {
  device_id: string
  status: string
  risk_score: number
  breached_policies: string[]
  justification_audit_trail: string
  alerted_at: string
}

export interface GeofenceData {
  name: string
  polygon: [number, number][]
}

function App() {
  const [devices, setDevices] = useState<DeviceStatus[]>([])
  const [alerts, setAlerts] = useState<AlertRecord[]>([])
  const [geofence, setGeofence] = useState<GeofenceData | null>(null)
  const [selectedDevice, setSelectedDevice] = useState<DeviceStatus | null>(null)

  useEffect(() => {
    const polling = async () => {
      try {
        const response = await fetch('/api/status')
        const data = await response.json()
        setDevices(data.devices || [])
        setAlerts(data.alerts || [])
        setGeofence(data.geofence || null)
      } catch (error) {
        console.error('Failed to fetch status:', error)
      }
    }
    polling()
    const interval = window.setInterval(polling, 2500)
    return () => window.clearInterval(interval)
  }, [])

  const highRiskDevices = useMemo(
    () => devices.filter((device) => device.evaluation?.compliance_status !== 'COMPLIANT'),
    [devices],
  )

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>AirShield Compliance</h1>
          <p>Real-time zero-trust fleet perimeter monitoring and automated isolation.</p>
        </div>
        <div className="status-pill">{highRiskDevices.length} non-compliant devices</div>
      </header>

      <main className="dashboard-grid">
        <section className="map-panel">
          <SecurityMap
            devices={devices}
            geofence={geofence}
            onSelectDevice={(device) => setSelectedDevice(device)}
          />
        </section>

        <section className="feed-panel">
          <ThreatFeed alerts={alerts} onSelectDevice={(deviceId) => {
            const found = devices.find((device) => device.device_id === deviceId)
            if (found) setSelectedDevice(found)
          }} />
        </section>
      </main>

      <ComplianceAuditor device={selectedDevice} />
    </div>
  )
}

export default App
