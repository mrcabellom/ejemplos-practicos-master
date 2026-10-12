"""Tests written from the data contract: the source writes day/month/year."""
import unittest

from parse_sale_date import parse_sale_date


class TestDataContract(unittest.TestCase):
    def test_slash_date_is_day_first(self):
        # 8 October, not 10 August
        self.assertEqual(parse_sale_date("08/10/2026"), "2026-10-08")

    def test_day_above_twelve(self):
        self.assertEqual(parse_sale_date("31/10/2026"), "2026-10-31")

    def test_invalid_date(self):
        self.assertIsNone(parse_sale_date("29/02/2026"))


if __name__ == "__main__":
    unittest.main()
