"""Scenarios of the order-lines capability."""

from datetime import date

from mercaluz.ingestion.orders import ingest_orders_file, landing_file_for
from mercaluz.transform.silver_orders import build_silver_order_lines

HEADER = "order_id,order_ts,store_id,customer_email,product_sku,category,quantity,unit_price,status\n"


def load(con, settings, business_date="2026-10-01"):
    ingest_orders_file(con, landing_file_for(settings.landing_dir, business_date))
    return build_silver_order_lines(con)


def test_business_date_is_derived_from_order_ts(con, settings):
    load(con, settings)
    row = con.execute(
        "SELECT order_date, quantity FROM silver.order_lines WHERE order_id = 'O-1002'"
    ).fetchone()
    assert row == (date(2026, 10, 1), 1)


def test_email_is_normalized(con, settings):
    (settings.landing_dir / "2026-10-03.csv").write_text(
        HEADER + "O-2001,2026-10-03T10:00:00,MAD-001, Ana.Garcia@Example.com ,SKU-PAN-BARRA,"
        "alimentacion_basica,1,0.80,completed\n",
        encoding="utf-8",
    )
    load(con, settings, "2026-10-03")
    email = con.execute("SELECT customer_email FROM silver.order_lines").fetchone()
    assert email == ("ana.garcia@example.com",)


def test_invalid_rows_are_excluded(con, settings):
    load(con, settings)
    ids = {r[0] for r in con.execute("SELECT order_id FROM silver.order_lines").fetchall()}
    assert "O-1007" not in ids
    assert None not in ids


def test_duplicated_line_is_kept_once(con, settings):
    load(con, settings)
    count = con.execute("SELECT count(*) FROM silver.order_lines WHERE order_id = 'O-1003'").fetchone()
    assert count == (1,)


def test_cancelled_orders_are_excluded(con, settings):
    assert load(con, settings) == 5  # O-1006 goes to quarantine since data-quality (session 5)
    count = con.execute("SELECT count(*) FROM silver.order_lines WHERE order_id = 'O-1005'").fetchone()
    assert count == (0,)
