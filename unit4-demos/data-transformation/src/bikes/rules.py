"""Cleaning rules for a trip, one per field.

Each function takes the text as it arrives in the delivery and returns the
clean value. If it cannot be cleaned, it raises ValueError with the reason,
which ends up in the `reason` column of output/rejected.csv.
"""

from datetime import datetime

STATIONS = {"Sol", "Atocha", "Retiro", "Moncloa", "Chamberí", "Lavapiés"}
USER_TYPES = {"member", "casual"}
TIME_FORMATS = ("%Y-%m-%dT%H:%M",)


def parse_time(value):
    """'2026-10-05T08:02' -> datetime."""
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            pass
    raise ValueError("fecha no válida")


def duration_minutes(start, end):
    """Minutes between start and end. The trip has to last something."""
    minutes = int((end - start).total_seconds() // 60)
    if minutes <= 0:
        raise ValueError("duración no positiva")
    return minutes


def clean_station(value):
    """'  Atocha ' -> 'Atocha'. Only stations in the catalog are accepted."""
    name = " ".join(value.split())
    if name not in STATIONS:
        raise ValueError("estación desconocida")
    return name


def clean_user_type(value):
    """' Member' -> 'member'."""
    user_type = value.strip().lower()
    if user_type not in USER_TYPES:
        raise ValueError("tipo de usuario desconocido")
    return user_type
