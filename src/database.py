"""
SQLite layer — directly connected to the NLP pipeline, kept deliberately
simple (two tables, no ORM) per the design doc's database algorithm.

complaints table   -> steps 10-11, 15-16, 17-18
notifications table -> steps 12-13
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from config import DB_PATH, VALID_STATUSES

SCHEMA = """
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id            TEXT PRIMARY KEY,
    registration_number     TEXT NOT NULL,
    complaint_text          TEXT NOT NULL,
    category                TEXT,
    priority                TEXT,
    ml_priority              TEXT,
    safety_rule_escalated    INTEGER,
    department               TEXT,
    location                 TEXT,
    equipment                TEXT,
    problem                  TEXT,
    status                   TEXT NOT NULL DEFAULT 'Submitted',
    created_at                TEXT NOT NULL,
    updated_at                 TEXT NOT NULL,
    resolved_at                 TEXT
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id     TEXT NOT NULL,
    department        TEXT NOT NULL,
    message            TEXT NOT NULL,
    is_read              INTEGER NOT NULL DEFAULT 0,
    created_at             TEXT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id)
);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def create_complaint(ticket: dict) -> None:
    """Step 10-11: build and store the complaint record."""
    now = datetime.now(timezone.utc).isoformat()
    entities = ticket.get("entities", {})
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO complaints (
                complaint_id, registration_number, complaint_text,
                category, priority, ml_priority, safety_rule_escalated,
                department, location, equipment, problem,
                status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket["ticket_id"],
                ticket["student_id"],
                ticket["complaint_text"],
                ticket["category"],
                ticket["final_priority"],
                ticket["ml_priority"],
                int(ticket["safety_rule_escalated"]),
                ticket["assigned_department"],
                ", ".join(entities.get("LOCATION", []) + entities.get("BLOCK", [])),
                ", ".join(entities.get("EQUIPMENT", [])),
                ", ".join(entities.get("PROBLEM", [])),
                ticket["status"],
                now,
                now,
            ),
        )


def create_notification(complaint_id: str, department: str, message: str) -> None:
    """Step 12-13: notification for the assigned department."""
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO notifications (complaint_id, department, message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (complaint_id, department, message, now),
        )


def get_complaint(complaint_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,)
        ).fetchone()
        return dict(row) if row else None


def get_complaints_by_registration(registration_number: str) -> list[dict]:
    """Case-insensitive match, e.g. '21cs045' finds '21CS045'."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM complaints WHERE UPPER(registration_number) = UPPER(?) "
            "ORDER BY created_at DESC",
            (registration_number,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_complaints_by_department(department: str) -> list[dict]:
    """
    Return complaints assigned to a department.

    Uses case-insensitive and whitespace-insensitive matching
    so department names such as:
        AV / IT Support
        av / it support
        AV / IT Support 
    are treated as the same department.
    """

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM complaints
            WHERE UPPER(TRIM(department)) = UPPER(TRIM(?))
            ORDER BY created_at DESC
            """,
            (department,),
        ).fetchall()

        return [dict(r) for r in rows]


def get_all_complaints() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM complaints ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_distinct_priorities() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT priority FROM complaints WHERE priority IS NOT NULL"
        ).fetchall()
        found = {r["priority"] for r in rows}
    ordered = [p for p in ["Critical", "High", "Medium", "Low"] if p in found]
    ordered += sorted(found - set(ordered))
    return ordered


def update_status(complaint_id: str, new_status: str) -> dict | None:
    """Step 15-16: staff updates status; resolved_at set only on Resolved."""
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Must be one of {VALID_STATUSES}")

    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        if new_status == "Resolved":
            conn.execute(
                "UPDATE complaints SET status = ?, updated_at = ?, resolved_at = ? WHERE complaint_id = ?",
                (new_status, now, now, complaint_id),
            )
        else:
            conn.execute(
                "UPDATE complaints SET status = ?, updated_at = ? WHERE complaint_id = ?",
                (new_status, now, complaint_id),
            )
    return get_complaint(complaint_id)


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
