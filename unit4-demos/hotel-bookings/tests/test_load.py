"""Tests for the load step and the occupancy report.

Known gap: no test loads an extract twice or loads versions out of order,
so the suite stays green while INC-0142 is open.

Run with `python tasks.py test`, pytest or `python -m unittest`.
"""

import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pipeline.load import connect, load
from src.pipeline.occupancy import nights


class TestLoad(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "t.db")

    def tearDown(self):
        self.tmp.cleanup()

    def test_valid_rows_are_written(self):
        result = load("2026-03-01", db_path=self.db)
        self.assertEqual(result["written"], 4)
        self.assertEqual(result["rejected"], 2)

    def test_invalid_rows_are_quarantined_with_a_reason(self):
        load("2026-03-01", db_path=self.db)
        with closing(connect(self.db)) as con:
            reasons = [r["reason_code"] for r in con.execute("SELECT reason_code FROM quarantine")]
        self.assertTrue(any("invalid_stay" in r for r in reasons))
        self.assertTrue(any("unknown_hotel" in r for r in reasons))

    def test_business_date_comes_from_the_event(self):
        """B-3010 arrives in the day-3 extract but was booked on day 2."""
        load("2026-03-03", db_path=self.db)
        with closing(connect(self.db)) as con:
            found = con.execute(
                "SELECT business_date FROM fct_bookings WHERE booking_id = 'B-3010'"
            ).fetchone()
        self.assertEqual(found["business_date"], "2026-03-02")


class TestOccupancy(unittest.TestCase):

    def test_check_out_night_is_not_occupied(self):
        self.assertEqual(
            list(nights("2026-03-01", "2026-03-03")),
            ["2026-03-01", "2026-03-02"],
        )


if __name__ == "__main__":
    unittest.main()
