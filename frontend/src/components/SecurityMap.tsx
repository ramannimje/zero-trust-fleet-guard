import { LatLngExpression } from 'leaflet'
import { MapContainer, Marker, Polygon, Popup, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

import L from 'leaflet'
import { DeviceStatus, GeofenceData } from '../App'

const ICON_GREEN = new L.Icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

const ICON_RED = new L.Icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-red.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

interface SecurityMapProps {
  devices: DeviceStatus[]
  geofence: GeofenceData | null
  onSelectDevice: (device: DeviceStatus) => void
}

export default function SecurityMap({ devices, geofence, onSelectDevice }: SecurityMapProps) {
  const center: LatLngExpression = [37.7825, -122.397]
  const polygon: [number, number][] = geofence?.polygon.map(
    (point) => [point[0], point[1]] as [number, number],
  ) ?? []

  return (
    <div className="security-map">
      <MapContainer center={center} zoom={15} scrollWheelZoom style={{ height: '100%', minHeight: '520px' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {polygon.length > 0 && (
          <Polygon pathOptions={{ color: '#34d399', weight: 3, fillOpacity: 0.1 }} positions={polygon} />
        )}
        {devices.map((device) => {
          const position: LatLngExpression = [device.payload.latitude, device.payload.longitude]
          const isCompliant = device.evaluation?.compliance_status === 'COMPLIANT'
          return (
            <Marker
              key={device.device_id}
              position={position}
              icon={isCompliant ? ICON_GREEN : ICON_RED}
              eventHandlers={{
                click: () => onSelectDevice(device),
              }}
            >
              <Popup>
                <strong>{device.device_id}</strong>
                <div>Status: {device.evaluation?.compliance_status}</div>
                <div>Risk: {device.evaluation?.risk_score}</div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}
