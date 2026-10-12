"""Check output/ against docs/data-contracts/trips.md.

    python -m src.bikes.check

Exit codes:
    0  the output meets the contract
    1  the output breaks the contract (the problems are listed)
    2  missing evidence: there is no output, or it is older than a delivery
"""

import csv
from collections import Counter
from pathlib import Path

INBOX = Path("inbox")
OUTPUT = Path("output")
FILES = ("trips.csv", "rejected.csv", "daily_usage.csv")
MAX_REJECTED = 0.10
DUPLICATE = "viaje duplicado"


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def problems(deliveries, trips, rejected, usage):
    found = []

    # 1. One trip, one row.
    for trip_id, times in sorted(Counter(t["trip_id"] for t in trips).items()):
        if times > 1:
            found.append(f"trip_id duplicado: {trip_id} ({times} filas)")

    # 2. Duration between 1 and 240 minutes.
    out_of_range = [t for t in trips if not 1 <= int(t["duration_min"]) <= 240]
    if out_of_range:
        found.append(f"duración fuera de rango (1-240 min): {len(out_of_range)} viajes")

    # 3. Per delivery: nothing is lost and no more than 10 % is rejected.
    for source, rows in deliveries.items():
        ok = sum(1 for t in trips if t["source"] == source)
        bad = [r for r in rejected if r["source"] == source]
        if len(rows) != ok + len(bad):
            found.append(f"{source}: balance roto ({len(rows)} leídos, {ok} + {len(bad)})")
        errors = sum(1 for r in bad if r["reason"] != DUPLICATE)
        if rows and errors / len(rows) > MAX_REJECTED:
            found.append(f"{source}: {errors / len(rows):.0%} rechazado "
                         f"({errors} de {len(rows)}); máximo {MAX_REJECTED:.0%}")

    # 4. Daily usage adds up to the trips.
    departures = sum(int(u["departures"]) for u in usage)
    if departures != len(trips):
        found.append(f"daily_usage suma {departures} salidas para {len(trips)} viajes")
    return found


def main():
    outputs = [OUTPUT / name for name in FILES]
    inbox = sorted(INBOX.glob("*.csv"))
    if not all(p.exists() for p in outputs):
        print("Falta evidencia: no existe output/. Ejecuta `python tasks.py transform`.")
        return 2
    if max(p.stat().st_mtime for p in inbox) > min(p.stat().st_mtime for p in outputs):
        print("Falta evidencia: hay entregas más nuevas que output/. "
              "Ejecuta `python tasks.py transform`.")
        return 2

    deliveries = {p.name: read(p) for p in inbox}
    trips, rejected, usage = (read(p) for p in outputs)
    found = problems(deliveries, trips, rejected, usage)

    print(f"Entregas: {len(deliveries)} | viajes: {len(trips)} | rechazados: {len(rejected)}")
    if not found:
        print("OK: la salida cumple el contrato.")
        return 0
    print("La salida NO cumple el contrato:")
    for p in found:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
