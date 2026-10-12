"""Scenarios of the daily-sales capability."""

from decimal import Decimal

from mercaluz.ingestion.orders import ingest_orders_file, landing_file_for
from mercaluz.transform.gold_daily_sales import build_gold_daily_sales
from mercaluz.transform.silver_orders import build_silver_order_lines


def build(con, settings):
    ingest_orders_file(con, landing_file_for(settings.landing_dir, "2026-10-01"))
    build_silver_order_lines(con)
    build_gold_daily_sales(con)


def sales(con, store_id):
    return con.execute(
        "SELECT orders_count, total_amount FROM gold.daily_sales "
        "WHERE order_date = '2026-10-01' AND store_id = ?",
        [store_id],
    ).fetchone()


def test_daily_sales_of_a_store(con, settings):
    build(con, settings)
    assert sales(con, "MAD-001") == (2, Decimal("26.09"))


def test_returns_do_not_count(con, settings):
    build(con, settings)
    assert sales(con, "BCN-014") == (1, Decimal("1.60"))
