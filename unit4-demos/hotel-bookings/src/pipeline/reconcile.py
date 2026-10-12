"""Reconcile the warehouse against its declared contract.

Usage:
    python -m src.pipeline.reconcile

Fixes nothing: it only reports. If the number of distinct keys does not
match the number of rows, the table has lost its declared grain.
Exits with a non-zero status so it can act as a quality gate in CI.
"""

import os
import sqlite3

DB = os.environ.get("BOOKINGS_DB", "warehouse.db")


def main():
    if not os.path.exists(DB):
        print("Warehouse not found. Run 'python tasks.py run-all' first.")
        return 1

    con = sqlite3.connect(DB)
    rows = con.execute("SELECT COUNT(*) FROM fct_bookings").fetchone()[0]
    keys = con.execute("SELECT COUNT(DISTINCT booking_id) FROM fct_bookings").fetchone()[0]
    quarantined = con.execute("SELECT COUNT(*) FROM quarantine").fetchone()[0]
    duplicates = con.execute(
        "SELECT booking_id, COUNT(*) n FROM fct_bookings "
        "GROUP BY booking_id HAVING n > 1 ORDER BY booking_id"
    ).fetchall()
    con.close()

    print("Reconciliation")
    print("--------------")
    print(f"  rows in fct_bookings ......... {rows}")
    print(f"  distinct bookings ............ {keys}")
    print(f"  rows in quarantine ........... {quarantined}")

    if duplicates:
        print()
        print(f"  WARNING: {len(duplicates)} bookings appear more than once")
        for booking_id, times in duplicates[:10]:
            print(f"    {booking_id}: {times} rows")
        print()
        print("  The contract declares one row per booking. This state breaks it.")
        return 1

    print()
    print("  No duplicates. The declared grain holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
