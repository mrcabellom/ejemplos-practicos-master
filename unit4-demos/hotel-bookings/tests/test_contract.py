"""Characterization tests for the data contract.

They describe current behaviour and act as a safety net before refactoring:
if a change breaks them, it altered something that was agreed.

Run with `python tasks.py test`, pytest or `python -m unittest`.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pipeline.contract import validate

HOTELS = {"MLG": 8}


def row(**overrides):
    base = {
        "booking_id": "B-1", "hotel_id": "MLG", "channel": "direct",
        "check_in": "2026-03-01", "check_out": "2026-03-03", "rooms": 1,
        "status": "confirmed", "total_amount": 100.0, "currency": "EUR",
    }
    base.update(overrides)
    return base


class TestContract(unittest.TestCase):

    def test_valid_row_has_no_reasons(self):
        self.assertEqual(validate(row(), HOTELS), [])

    def test_unknown_hotel_is_rejected(self):
        self.assertIn("unknown_hotel", validate(row(hotel_id="SVQ"), HOTELS))

    def test_check_out_must_be_after_check_in(self):
        self.assertIn("invalid_stay", validate(row(check_out="2026-03-01"), HOTELS))

    def test_zero_rooms_is_rejected(self):
        self.assertIn("invalid_rooms", validate(row(rooms=0), HOTELS))

    def test_currency_other_than_eur_is_rejected(self):
        self.assertIn("unsupported_currency", validate(row(currency="USD"), HOTELS))

    def test_unknown_status_is_rejected(self):
        self.assertIn("unknown_status", validate(row(status="no_show"), HOTELS))


if __name__ == "__main__":
    unittest.main()
