"""Tests written by the assistant, with the same assumption as its code (month/day)."""
import unittest

from parse_sale_date import parse_sale_date


class TestWrittenByAssistant(unittest.TestCase):
    def test_iso_date(self):
        self.assertEqual(parse_sale_date("2026-10-08"), "2026-10-08")

    def test_slash_date(self):
        self.assertEqual(parse_sale_date("08/10/2026"), "2026-08-10")

    def test_invalid_date(self):
        self.assertIsNone(parse_sale_date("29/02/2026"))


if __name__ == "__main__":
    unittest.main()
