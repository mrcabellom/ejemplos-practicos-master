"""Scenarios of the data-quality capability and the modified invalid-row handling of order-lines."""

from mercaluz.ingestion.orders import ingest_orders_file, landing_file_for
from mercaluz.transform.gold_daily_sales import build_gold_daily_sales
from mercaluz.transform.silver_orders import build_silver_order_lines

HEADER = "order_id,order_ts,store_id,customer_email,product_sku,category,quantity,unit_price,status\n"


def load(con, settings, business_date="2026-10-01"):
    ingest_orders_file(con, landing_file_for(settings.landing_dir, business_date))
    build_silver_order_lines(con)


def failed_rules(con, order_id):
    return con.execute(
        "SELECT dq_failed_rules FROM silver.order_lines_quarantine WHERE order_id IS NOT DISTINCT FROM ?",
        [order_id],
    ).fetchall()


def test_negative_quantity_goes_to_quarantine(con, settings):
    load(con, settings)
    assert failed_rules(con, "O-1006") == [(["DQ003"],)]


def test_non_numeric_price_goes_to_quarantine(con, settings):
    load(con, settings)
    assert failed_rules(con, "O-1007") == [(["DQ004"],)]


def test_missing_order_id_goes_to_quarantine(con, settings):
    load(con, settings)
    assert failed_rules(con, None) == [(["DQ001"],)]


def test_row_failing_several_rules_is_quarantined_once(con, settings):
    (settings.landing_dir / "2026-10-03.csv").write_text(
        HEADER + ",2026-10-03T10:00:00,MAD-001,x@example.com,SKU-PAN-BARRA,alimentacion_basica,0,0.80,completed\n",
        encoding="utf-8",
    )
    load(con, settings, "2026-10-03")
    assert failed_rules(con, None) == [(["DQ001", "DQ003"],)]


def test_rebuilding_does_not_duplicate_quarantine(con, settings):
    load(con, settings)
    build_silver_order_lines(con)
    assert con.execute("SELECT count(*) FROM silver.order_lines_quarantine").fetchone() == (3,)


def test_negative_quantity_no_longer_reaches_gold(con, settings):
    load(con, settings)
    build_gold_daily_sales(con)
    assert con.execute("SELECT count(*) FROM silver.order_lines WHERE order_id = 'O-1006'").fetchone() == (0,)
    stores = {r[0] for r in con.execute(
        "SELECT store_id FROM gold.daily_sales WHERE order_date = '2026-10-01'"
    ).fetchall()}
    assert "VLC-007" not in stores
