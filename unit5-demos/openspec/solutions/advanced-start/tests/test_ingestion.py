"""Scenarios of the orders-ingestion capability."""

import pytest

from mercaluz.ingestion.orders import ingest_orders_file, landing_file_for


def test_daily_file_loads_every_row(con, settings):
    loaded = ingest_orders_file(con, landing_file_for(settings.landing_dir, "2026-10-01"))
    assert loaded == 10
    sources = con.execute("SELECT DISTINCT _source_file FROM bronze.orders_raw").fetchall()
    assert sources == [("2026-10-01.csv",)]


def test_non_numeric_value_is_kept_as_text(con, settings):
    ingest_orders_file(con, landing_file_for(settings.landing_dir, "2026-10-01"))
    price = con.execute("SELECT unit_price FROM bronze.orders_raw WHERE order_id = 'O-1007'").fetchone()
    assert price == ("abc",)


def test_missing_landing_file_fails_without_loading(con, settings):
    with pytest.raises(FileNotFoundError, match="2026-09-30.csv"):
        ingest_orders_file(con, landing_file_for(settings.landing_dir, "2026-09-30"))
    tables = con.execute("SELECT count(*) FROM duckdb_tables() WHERE schema_name = 'bronze'").fetchone()
    assert tables == (0,)
