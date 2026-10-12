"""Scenarios of the reprocessing requirement of orders-ingestion."""

import duckdb
import pytest

from mercaluz.ingestion.orders import ingest_orders_file, landing_file_for
from mercaluz.transform.silver_orders import build_silver_order_lines


def bronze_rows(con, source_file):
    return con.execute(
        "SELECT count(*) FROM bronze.orders_raw WHERE _source_file = ?", [source_file]
    ).fetchone()[0]


def test_running_the_same_day_twice_does_not_duplicate(con, settings):
    path = landing_file_for(settings.landing_dir, "2026-10-01")
    ingest_orders_file(con, path)
    ingest_orders_file(con, path)
    assert bronze_rows(con, "2026-10-01.csv") == 10


def test_corrected_file_replaces_the_previous_version(con, settings):
    path = landing_file_for(settings.landing_dir, "2026-10-02")
    ingest_orders_file(con, path)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    path.write_text("".join(line for line in lines if not line.startswith("O-1011,")), encoding="utf-8")

    ingest_orders_file(con, path)
    build_silver_order_lines(con)

    assert bronze_rows(con, "2026-10-02.csv") == 4
    assert con.execute("SELECT count(*) FROM silver.order_lines WHERE order_id = 'O-1011'").fetchone() == (0,)


def test_failed_reload_keeps_the_previous_version(con, settings):
    path = landing_file_for(settings.landing_dir, "2026-10-02")
    ingest_orders_file(con, path)
    # A corrupt corrected file (missing the status column) makes the insert fail after the delete.
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rsplit(",", 1)[0] for line in lines) + "\n", encoding="utf-8")

    with pytest.raises(duckdb.Error):
        ingest_orders_file(con, path)
    assert bronze_rows(con, "2026-10-02.csv") == 5
