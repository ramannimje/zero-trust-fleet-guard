import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "audit_log.db"


class AuditDatabase:
    def __init__(self, path: str | Path = DB_PATH):
        self.path = Path(path)
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.path)
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS device_status (
                device_id TEXT PRIMARY KEY,
                latest_payload TEXT NOT NULL,
                latest_evaluation TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        await self._conn.commit()

    async def log_event(self, device_id: str, event_type: str, payload: str, timestamp: str) -> None:
        assert self._conn is not None
        await self._conn.execute(
            "INSERT INTO audit_events (device_id, event_type, payload, timestamp) VALUES (?, ?, ?, ?)",
            (device_id, event_type, payload, timestamp),
        )
        await self._conn.commit()

    async def upsert_device_status(self, device_id: str, latest_payload: str, latest_evaluation: str, updated_at: str) -> None:
        assert self._conn is not None
        await self._conn.execute(
            "INSERT INTO device_status (device_id, latest_payload, latest_evaluation, updated_at) VALUES (?, ?, ?, ?)"
            " ON CONFLICT(device_id) DO UPDATE SET latest_payload=excluded.latest_payload, latest_evaluation=excluded.latest_evaluation, updated_at=excluded.updated_at",
            (device_id, latest_payload, latest_evaluation, updated_at),
        )
        await self._conn.commit()

    async def fetch_recent_alerts(self, limit: int = 20) -> list[dict]:
        assert self._conn is not None
        cursor = await self._conn.execute(
            "SELECT device_id, event_type, payload, timestamp FROM audit_events ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [
            {"device_id": row[0], "event_type": row[1], "payload": row[2], "timestamp": row[3]}
            for row in rows
        ]

    async def fetch_device_states(self) -> list[dict]:
        assert self._conn is not None
        cursor = await self._conn.execute(
            "SELECT device_id, latest_payload, latest_evaluation, updated_at FROM device_status"
        )
        rows = await cursor.fetchall()
        return [
            {
                "device_id": row[0],
                "latest_payload": row[1],
                "latest_evaluation": row[2],
                "updated_at": row[3],
            }
            for row in rows
        ]
