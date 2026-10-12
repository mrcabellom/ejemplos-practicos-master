"""Acceptance check for INC-0142: does the load honour the contract?

Usage:
    python -m src.pipeline.acceptance

Builds throwaway warehouses in a temporary folder, loads the extracts in
several orders and checks the result against the contract. It never touches
warehouse.db, so running it twice gives the same answer and needs no
authorisation.

Exits with a non-zero status when any criterion fails, so it can serve as
the completion condition of an agent goal or as a CI gate.
"""

import sqlite3
import sys
import tempfile
from contextlib import closing, redirect_stdout
from io import StringIO
from pathlib import Path

from .contract import load_hotels
from .load import load
from .occupancy import occupied_rooms

DATES = ("2026-03-01", "2026-03-02", "2026-03-03")
EXPECTED_BOOKINGS = 8


def _build(folder, name, dates):
    """Load the given extract dates, in order, into a new warehouse.

    Writes only to <folder>/<name>.db. Calling it twice with the same name
    loads the dates again on top of that file; criteria() uses each name once.
    """
    db = str(Path(folder) / f"{name}.db")
    with redirect_stdout(StringIO()):  # keep the per-run lines out of the report
        for date in dates:
            load(date, db_path=db)
    return db


def _query(db, sql, params=()):
    with closing(sqlite3.connect(db)) as con:
        return con.execute(sql, params).fetchall()


def _table(db):
    return sorted(_query(db, "SELECT * FROM fct_bookings ORDER BY booking_id"))


def _counts(db):
    rows, keys = _query(
        db, "SELECT COUNT(*), COUNT(DISTINCT booking_id) FROM fct_bookings"
    )[0]
    return rows, keys


def _booking(db, booking_id):
    return _query(
        db, "SELECT rooms, status FROM fct_bookings WHERE booking_id = ?", (booking_id,)
    )


def _strip_run_id(table):
    """Drop run_id, the last column: it changes on every run by design."""
    return [row[:-1] for row in table]


def criteria(folder):
    """Yield (description, passed, detail) for every acceptance criterion."""
    in_order = _build(folder, "in_order", DATES)
    rows, keys = _counts(in_order)
    yield (
        "One row per booking after loading the three extracts",
        rows == keys == EXPECTED_BOOKINGS,
        f"{rows} rows, {keys} distinct bookings (expected {EXPECTED_BOOKINGS} and {EXPECTED_BOOKINGS})",
    )

    twice = _build(folder, "twice", DATES + ("2026-03-02",))
    same = _strip_run_id(_table(twice)) == _strip_run_id(_table(in_order))
    rows, _ = _counts(twice)
    yield (
        "Loading an extract again leaves fct_bookings unchanged",
        same,
        f"{rows} rows after reloading 2026-03-02",
    )

    stale = _build(folder, "stale_last", DATES + ("2026-03-01",))
    b3002 = _booking(stale, "B-3002")
    b3003 = _booking(stale, "B-3003")
    yield (
        "An older version loaded last does not overwrite a newer one",
        b3002 == [(3, "confirmed")] and b3003 == [(4, "confirmed")],
        f"B-3002 {b3002}, B-3003 {b3003} (expected 3 rooms confirmed, 4 rooms confirmed)",
    )

    capacity = load_hotels()
    with closing(sqlite3.connect(in_order)) as con:
        occupied = occupied_rooms(con)
    over = sorted(
        f"{hotel} {night} {rooms}/{capacity[hotel]}"
        for (hotel, night), rooms in occupied.items()
        if rooms > capacity[hotel]
    )
    yield (
        "No night exceeds the hotel capacity",
        not over,
        ", ".join(over) or "none over capacity",
    )

    mlg = occupied.get(("MLG", "2026-03-02"), 0)
    mad = occupied.get(("MAD", "2026-03-02"), 0)
    yield (
        "Occupancy on 2 March matches the contract",
        (mlg, mad) == (7, 4),
        f"MLG {mlg}/8, MAD {mad}/10 (expected 7/8 and 4/10)",
    )


def main():
    print("Acceptance check for INC-0142")
    print("-----------------------------")
    failed = 0
    with tempfile.TemporaryDirectory() as folder:
        for description, passed, detail in criteria(folder):
            failed += not passed
            print(f"  [{'PASS' if passed else 'FAIL'}] {description}")
            print(f"         {detail}")
    print()
    if failed:
        print(f"  {failed} criteria failed. The load does not honour the contract yet.")
        return 1
    print("  All criteria pass. The load honours the contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
