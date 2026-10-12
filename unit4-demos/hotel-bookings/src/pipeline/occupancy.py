"""Provisional occupancy report, the one the management dashboard reads.

Usage:
    python -m src.pipeline.occupancy

For every hotel and night it adds up the rooms of the confirmed bookings
staying that night and divides by the hotel capacity. A stay from check_in
to check_out occupies the nights in [check_in, check_out): the guest leaves
on the morning of check_out.

It lists every night with at least one occupied room. The pricing system
reads this output to decide tomorrow's rates.
"""

import os
import sqlite3
from collections import defaultdict
from datetime import date, timedelta

from .contract import load_hotels

DB = os.environ.get("BOOKINGS_DB", "warehouse.db")


def nights(check_in, check_out):
    """Yield the nights of a stay as ISO dates, check_out excluded."""
    day = date.fromisoformat(check_in)
    end = date.fromisoformat(check_out)
    while day < end:
        yield day.isoformat()
        day += timedelta(days=1)


def occupied_rooms(con):
    """Return {(hotel_id, night): rooms} from the confirmed bookings."""
    occupied = defaultdict(int)
    for row in con.execute(
        "SELECT hotel_id, check_in, check_out, rooms FROM fct_bookings "
        "WHERE status = 'confirmed'"
    ):
        for night in nights(row[1], row[2]):
            occupied[(row[0], night)] += row[3]
    return occupied


def main():
    if not os.path.exists(DB):
        print("Warehouse not found. Run 'python tasks.py run-all' first.")
        return 1

    capacity = load_hotels()
    con = sqlite3.connect(DB)
    occupied = occupied_rooms(con)
    con.close()

    print("Occupancy report (provisional dashboard)")
    print("----------------------------------------")
    print("  hotel  night        rooms   occupancy")
    for (hotel_id, night), rooms in sorted(occupied.items()):
        total = capacity[hotel_id]
        print(f"  {hotel_id:<5}  {night}   {rooms:>2}/{total:<2}   {rooms / total:>6.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
