"""Parses the sale_date column. This is the version the assistant wrote.

The source mixes "2026-10-08" (ISO) and "08/10/2026". The assistant assumed
month/day for the second format: the assumption lives in SLASH_FORMAT.
"""
from datetime import datetime

SLASH_FORMAT = "%m/%d/%Y"


def parse_sale_date(text):
    """Return the date as ISO (YYYY-MM-DD), or None if it is not a valid date."""
    for fmt in ("%Y-%m-%d", SLASH_FORMAT):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None
