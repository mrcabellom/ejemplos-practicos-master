"""Transform every delivery in inbox/ and write output/.

    python -m src.bikes.transform

Outputs:
    output/trips.csv        valid trips, with their duration and delivery
    output/rejected.csv     discarded trips, with their reason
    output/daily_usage.csv  departures and average duration per day and station
"""

import csv
from collections import defaultdict
from pathlib import Path

from . import rules

INBOX = Path("inbox")
OUTPUT = Path("output")
ISO = "%Y-%m-%dT%H:%M"

TRIP_COLUMNS = ["trip_id", "bike_id", "start_time", "end_time", "duration_min",
                "start_station", "end_station", "user_type", "source"]
REJECTED_COLUMNS = ["trip_id", "bike_id", "start_time", "end_time",
                    "start_station", "end_station", "user_type", "source", "reason"]
USAGE_COLUMNS = ["date", "station", "departures", "avg_minutes"]


def clean_trip(row, source):
    start = rules.parse_time(row["start_time"])
    end = rules.parse_time(row["end_time"])
    return {
        "trip_id": row["trip_id"].strip(),
        "bike_id": row["bike_id"].strip(),
        "start_time": start.strftime(ISO),
        "end_time": end.strftime(ISO),
        "duration_min": rules.duration_minutes(start, end),
        "start_station": rules.clean_station(row["start_station"]),
        "end_station": rules.clean_station(row["end_station"]),
        "user_type": rules.clean_user_type(row["user_type"]),
        "source": source,
    }


def transform(deliveries):
    """deliveries: list of (delivery name, rows). Returns (trips, rejected)."""
    trips, rejected = [], []
    for source, rows in deliveries:
        for row in rows:
            try:
                trips.append(clean_trip(row, source))
            except ValueError as error:
                rejected.append({**row, "source": source, "reason": str(error)})
    return trips, rejected


def daily_usage(trips):
    """Group by start date and start station."""
    groups = defaultdict(list)
    for trip in trips:
        groups[(trip["start_time"][:10], trip["start_station"])].append(trip["duration_min"])
    return [
        {"date": date, "station": station, "departures": len(minutes),
         "avg_minutes": round(sum(minutes) / len(minutes), 1)}
        for (date, station), minutes in sorted(groups.items())
    ]


def read_inbox():
    deliveries = []
    for path in sorted(INBOX.glob("*.csv")):
        with open(path, newline="", encoding="utf-8") as f:
            deliveries.append((path.name, list(csv.DictReader(f))))
    return deliveries


def write(path, rows, columns):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    deliveries = read_inbox()
    trips, rejected = transform(deliveries)

    OUTPUT.mkdir(exist_ok=True)
    write(OUTPUT / "trips.csv", trips, TRIP_COLUMNS)
    write(OUTPUT / "rejected.csv", rejected, REJECTED_COLUMNS)
    write(OUTPUT / "daily_usage.csv", daily_usage(trips), USAGE_COLUMNS)

    for source, rows in deliveries:
        bad = sum(1 for r in rejected if r["source"] == source)
        print(f"{source}: {len(rows)} leídos | {len(rows) - bad} válidos | {bad} rechazados")
    print(f"Total: {len(trips)} viajes válidos, {len(rejected)} rechazados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
