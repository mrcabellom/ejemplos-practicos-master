"""Scenarios of the finance-export capability."""

from mercaluz.exports.finance_csv import export_finance_csv
from mercaluz.ingestion.orders import ingest_orders_file, landing_file_for
from mercaluz.transform.gold_daily_sales import build_gold_daily_sales
from mercaluz.transform.silver_orders import build_silver_order_lines


def export_lines(con, settings):
    ingest_orders_file(con, landing_file_for(settings.landing_dir, "2026-10-01"))
    build_silver_order_lines(con)
    build_gold_daily_sales(con)
    path = export_finance_csv(con, settings.exports_dir)
    return path.read_text(encoding="utf-8").splitlines()


def test_export_has_header_and_one_line_per_store(con, settings):
    lines = export_lines(con, settings)
    assert lines[0] == "date;store;orders;total_amount"
    assert "2026-10-01;MAD-001;2;26,09" in lines


def test_amounts_use_decimal_comma_and_two_decimals(con, settings):
    assert "2026-10-01;BCN-014;1;1,60" in export_lines(con, settings)
