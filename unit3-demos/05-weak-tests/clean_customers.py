"""Customer cleaning: normalizes emails and removes duplicates.

Usage:  uv run python clean_customers.py                           (uses data/customers.csv)
        uv run python clean_customers.py data/customers_blank.csv  (extra: empty emails)
"""
import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def normalize_email(email):
    """Strip leading and trailing spaces and lowercase the email."""
    return email.strip().lower()


def deduplicate_customers(customers):
    """Keep one customer per normalized email (the first one that appears)."""
    seen = set()
    unique = []
    for customer in customers:
        key = normalize_email(customer["email"])
        if key in seen:
            continue
        seen.add(key)
        unique.append({**customer, "email": key})
    return unique


def load_customers(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_DIR / "customers.csv"
    customers = load_customers(path)
    unique = deduplicate_customers(customers)
    print(f"Clientes leídos: {len(customers)}")
    print(f"Clientes únicos: {len(unique)}")
    for customer in unique:
        print(f"  {customer['customer_id']:>3}  {customer['name']:<12} {customer['email']!r}")


if __name__ == "__main__":
    main()
