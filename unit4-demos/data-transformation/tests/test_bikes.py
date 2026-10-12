"""Tests for the rules and the transform. They describe the current behaviour."""

import unittest
from datetime import datetime

from src.bikes import rules
from src.bikes.transform import daily_usage, transform


def row(**changes):
    base = {"trip_id": "T1", "bike_id": "B1",
            "start_time": "2026-10-05T08:00", "end_time": "2026-10-05T08:20",
            "start_station": "Sol", "end_station": "Atocha", "user_type": "member"}
    return {**base, **changes}


class TestRules(unittest.TestCase):

    def test_iso_time(self):
        self.assertEqual(rules.parse_time("2026-10-05T08:02"), datetime(2026, 10, 5, 8, 2))

    def test_invalid_time_is_rejected(self):
        with self.assertRaises(ValueError):
            rules.parse_time("ayer por la tarde")

    def test_duration_in_minutes(self):
        start, end = datetime(2026, 10, 5, 8, 0), datetime(2026, 10, 5, 8, 17)
        self.assertEqual(rules.duration_minutes(start, end), 17)

    def test_negative_duration_is_rejected(self):
        start, end = datetime(2026, 10, 5, 8, 0), datetime(2026, 10, 5, 7, 54)
        with self.assertRaises(ValueError):
            rules.duration_minutes(start, end)

    def test_station_strips_spaces(self):
        self.assertEqual(rules.clean_station("  Atocha "), "Atocha")

    def test_station_outside_catalog_is_rejected(self):
        with self.assertRaises(ValueError):
            rules.clean_station("Gran Vía")

    def test_user_type_is_lowercased(self):
        self.assertEqual(rules.clean_user_type(" Member"), "member")


class TestTransform(unittest.TestCase):

    def test_rejection_keeps_reason_and_source(self):
        trips, rejected = transform([("week-1.csv", [row(), row(trip_id="T2", start_station="Gran Vía")])])
        self.assertEqual(len(trips), 1)
        self.assertEqual(rejected[0]["reason"], "estación desconocida")
        self.assertEqual(rejected[0]["source"], "week-1.csv")

    def test_daily_usage_groups_by_day_and_station(self):
        trips, _ = transform([("week-1.csv", [row(), row(trip_id="T2", end_time="2026-10-05T08:10")])])
        self.assertEqual(daily_usage(trips), [
            {"date": "2026-10-05", "station": "Sol", "departures": 2, "avg_minutes": 15.0},
        ])


if __name__ == "__main__":
    unittest.main()
