"""Delete inactive customers: those who have not bought in the last year (365 days)."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "shop.db"

# Fixed date so the demo is reproducible (in production this would be today)
REFERENCE_DATE = "2026-10-08"
INACTIVITY_DAYS = 365


def main():
    con = sqlite3.connect(DB_PATH)
    with con:
        cursor = con.execute(
            "DELETE FROM customers WHERE last_purchase < date(?, ?)",
            (REFERENCE_DATE, f"-{INACTIVITY_DAYS} days"),
        )
    con.close()
    print(f"Clientes borrados: {cursor.rowcount}")


if __name__ == "__main__":
    main()
