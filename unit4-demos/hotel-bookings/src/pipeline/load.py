"""Load hotel bookings into the analytical warehouse.

Usage:
    python -m src.pipeline.load --date 2026-03-01

Reads data/raw/bookings_<date>.json, the daily extract sent by the booking
engine and the online travel agencies. Every row is validated against the
contract; the ones that fail go to quarantine and the rest to fct_bookings.
"""

import argparse
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

from .contract import load_hotels, validate

DB = os.environ.get("BOOKINGS_DB", "warehouse.db")


def connect(db_path=None):
    con = sqlite3.connect(db_path or DB)
    con.row_factory = sqlite3.Row
    return con


def create_schema(con):
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS fct_bookings (
            booking_id    TEXT,
            hotel_id      TEXT,
            channel       TEXT,
            check_in      TEXT,
            check_out     TEXT,
            rooms         INTEGER,
            status        TEXT,
            total_amount  REAL,
            currency      TEXT,
            updated_at    TEXT,
            business_date TEXT,
            run_id        TEXT
        );

        CREATE TABLE IF NOT EXISTS quarantine (
            booking_id    TEXT,
            business_date TEXT,
            reason_code   TEXT,
            payload       TEXT,
            run_id        TEXT
        );

        CREATE TABLE IF NOT EXISTS run_log (
            run_id        TEXT,
            extract_date  TEXT,
            executed_at   TEXT,
            rows_read     INTEGER,
            rows_written  INTEGER,
            rows_rejected INTEGER
        );
        """
    )
    con.commit()


def read_source(date):
    path = os.path.join("data", "raw", f"bookings_{date}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No extract for {date}: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def business_date_of(row):
    """The business date comes from the event, never from the extract file."""
    return (row.get("updated_at") or "")[:10]


def load(date, db_path=None):
    """Append accepted rows; repeating a date may create duplicate bookings.

    Rejected rows are recorded in quarantine for each run.
    """
    run_id = str(uuid.uuid4())[:8]
    hotels = load_hotels()
    con = connect(db_path)
    create_schema(con)

    rows = read_source(date)
    written = rejected = 0

    for row in rows:
        reasons = validate(row, hotels)
        if reasons:
            con.execute(
                "INSERT INTO quarantine VALUES (?, ?, ?, ?, ?)",
                (
                    row.get("booking_id"),
                    business_date_of(row),
                    ",".join(reasons),
                    json.dumps(row, ensure_ascii=False),
                    run_id,
                ),
            )
            rejected += 1
            continue

        con.execute(
            "INSERT INTO fct_bookings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                row["booking_id"],
                row["hotel_id"],
                row["channel"],
                row["check_in"],
                row["check_out"],
                row["rooms"],
                row["status"],
                row["total_amount"],
                row["currency"],
                row["updated_at"],
                business_date_of(row),
                run_id,
            ),
        )
        written += 1

    con.execute(
        "INSERT INTO run_log VALUES (?, ?, ?, ?, ?, ?)",
        (
            run_id,
            date,
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            len(rows),
            written,
            rejected,
        ),
    )
    con.commit()
    con.close()

    print(f"[{run_id}] {date}: read={len(rows)} written={written} rejected={rejected}")
    return {"run_id": run_id, "read": len(rows), "written": written, "rejected": rejected}


def main():
    parser = argparse.ArgumentParser(description="Load the bookings extract of a given date")
    parser.add_argument("--date", required=True, help="Extract date, YYYY-MM-DD")
    args = parser.parse_args()
    load(args.date)


if __name__ == "__main__":
    main()
