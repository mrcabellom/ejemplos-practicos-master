"""Validation rules derived from the data contract.

The contract itself lives in docs/data-contracts/fct_bookings.md. This module
only translates it into code: if a rule changes, both must change.
"""

import json
import os
from datetime import date

VALID_STATUSES = {"tentative", "confirmed", "cancelled"}
SUPPORTED_CURRENCY = "EUR"
HOTELS_FILE = os.path.join("data", "reference", "hotels.json")


def load_hotels(path=HOTELS_FILE):
    """Return {hotel_id: rooms} from the reference file."""
    with open(path, encoding="utf-8") as f:
        return {h["hotel_id"]: h["rooms"] for h in json.load(f)}


def _parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def validate(row, hotels):
    """Return the list of rejection reasons. Empty means the row is valid."""
    reasons = []

    if not row.get("booking_id"):
        reasons.append("missing_booking_id")

    if row.get("hotel_id") not in hotels:
        reasons.append("unknown_hotel")

    check_in = _parse_date(row.get("check_in"))
    check_out = _parse_date(row.get("check_out"))
    if check_in is None or check_out is None or check_out <= check_in:
        reasons.append("invalid_stay")

    rooms = row.get("rooms")
    if not isinstance(rooms, int) or rooms < 1:
        reasons.append("invalid_rooms")

    if row.get("status") not in VALID_STATUSES:
        reasons.append("unknown_status")

    amount = row.get("total_amount")
    if amount is None:
        reasons.append("missing_amount")
    elif amount < 0:
        reasons.append("negative_amount")

    if row.get("currency") != SUPPORTED_CURRENCY:
        reasons.append("unsupported_currency")

    return reasons
