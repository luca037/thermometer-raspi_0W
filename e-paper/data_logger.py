import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_data.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            internal_temp REAL,
            internal_humidity REAL,
            external_temp REAL,
            external_humidity REAL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON readings(timestamp)
    """)
    conn.commit()
    conn.close()


def log_reading(internal_temp=None, internal_humidity=None,
                external_temp=None, external_humidity=None):
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO readings
           (timestamp, internal_temp, internal_humidity, external_temp, external_humidity)
           VALUES (?, ?, ?, ?, ?)""",
        (ts, internal_temp, internal_humidity, external_temp, external_humidity),
    )
    conn.commit()
    conn.close()


def get_readings(days=2):
    since = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat(timespec="seconds")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT timestamp, internal_temp, internal_humidity, external_temp, external_humidity
           FROM readings
           WHERE timestamp >= ?
           ORDER BY timestamp ASC""",
        (since,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
