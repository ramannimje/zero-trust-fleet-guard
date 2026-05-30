import asyncio
import random
import time

import httpx

from app.schemas import DeviceStatePayload

BASE_LATITUDE = 37.7825
BASE_LONGITUDE = -122.3970
GEOFENCE_RADIUS = 0.0035
SIMULATED_FORBIDDEN_APPS = [
    "spoofed-vpn",
    "credential-extractor",
    "shadow-admin",
]


def _build_payload(device_id: str, state_index: int) -> DeviceStatePayload:
    is_bad_actor = state_index % 7 == 0
    is_rootswitch = state_index % 11 == 0
    drift = (state_index % 10) * 0.0006

    latitude = BASE_LATITUDE + ((state_index % 5) - 2) * 0.0007 + (drift if is_bad_actor else 0)
    longitude = BASE_LONGITUDE + ((state_index % 7) - 3) * 0.0008 + (-drift if is_bad_actor else 0)

    apps = ["corporate-mail", "vpn-client", "secure-browser"]
    if is_bad_actor:
        apps.append(random.choice(SIMULATED_FORBIDDEN_APPS))
    if state_index % 13 == 0:
        apps.append("enterprise-spoof")

    os_patch_level = "2024-06" if state_index % 9 != 0 else "2023-11"
    if state_index % 17 == 0:
        os_patch_level = "2022-12"

    return DeviceStatePayload(
        device_id=device_id,
        latitude=latitude,
        longitude=longitude,
        installed_applications=apps,
        is_rooted_or_jailbroken=is_rootswitch,
        os_patch_level=os_patch_level,
    )


async def send_heartbeat(client: httpx.AsyncClient, payload: DeviceStatePayload) -> None:
    try:
        response = await client.post("/ingest", json=payload.model_dump())
        response.raise_for_status()
    except Exception as exc:
        print(f"[Simulator] failed to send telemetry for {payload.device_id}: {exc}")


async def run_simulator() -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=10.0) as client:
        devices = [f"device-{i:03d}" for i in range(1, 51)]
        iteration = 0
        while True:
            tasks = []
            for index, device_id in enumerate(devices):
                current_index = iteration + index
                payload = _build_payload(device_id, current_index)
                tasks.append(send_heartbeat(client, payload))
            await asyncio.gather(*tasks)
            iteration += 1
            print(f"[Simulator] pushed telemetry batch {iteration}")
            await asyncio.sleep(3.0)


if __name__ == "__main__":
    asyncio.run(run_simulator())
