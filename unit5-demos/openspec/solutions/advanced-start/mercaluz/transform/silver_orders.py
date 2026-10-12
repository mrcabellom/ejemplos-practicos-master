"""bronze.orders_raw -> silver.order_lines and silver.order_lines_quarantine.

Every bronze row is evaluated once against the data quality rules (DQ001-DQ005).
Rows that pass go to silver.order_lines (typed, deduplicated, without cancelled orders);
rows that fail go to silver.order_lines_quarantine with the list of failed rules.
Both tables are rebuilt in the same transaction.
"""

from datetime import datetime, timezone

import duckdb

EVALUATED_ROWS = """
    SELECT
        *,
        list_filter([
            CASE WHEN order_id IS NULL OR order_id = '' THEN 'DQ001' END,
            CASE WHEN TRY_CAST(order_ts AS TIMESTAMP) IS NULL THEN 'DQ002' END,
            CASE WHEN coalesce(TRY_CAST(quantity AS INTEGER) <= 0, true) THEN 'DQ003' END,
            CASE WHEN coalesce(TRY_CAST(unit_price AS DECIMAL(10,2)) < 0, true) THEN 'DQ004' END,
            CASE WHEN coalesce(status NOT IN ('completed', 'returned', 'cancelled'), true) THEN 'DQ005' END
        ], rule -> rule IS NOT NULL) AS dq_failed_rules
    FROM bronze.orders_raw
"""


def build_silver_order_lines(con: duckdb.DuckDBPyConnection) -> int:
    quarantined_at = datetime.now(timezone.utc).replace(tzinfo=None)
    con.begin()
    try:
        con.execute(f"CREATE OR REPLACE TEMP TABLE evaluated_rows AS {EVALUATED_ROWS}")
        con.execute(
            """
            CREATE OR REPLACE TABLE silver.order_lines AS
            WITH typed AS (
                SELECT
                    order_id,
                    CAST(order_ts AS TIMESTAMP)       AS order_ts,
                    store_id,
                    lower(trim(customer_email))       AS customer_email,
                    product_sku,
                    category,
                    CAST(quantity AS INTEGER)         AS quantity,
                    CAST(unit_price AS DECIMAL(10,2)) AS unit_price,
                    status,
                    _ingested_at
                FROM evaluated_rows
                WHERE len(dq_failed_rules) = 0
            ),
            dedup AS (
                SELECT *,
                       row_number() OVER (
                           PARTITION BY order_id, product_sku
                           ORDER BY _ingested_at DESC
                       ) AS rn
                FROM typed
            )
            SELECT order_id, order_ts, CAST(order_ts AS DATE) AS order_date, store_id,
                   customer_email, product_sku, category, quantity, unit_price, status
            FROM dedup
            WHERE rn = 1 AND status <> 'cancelled'
            """
        )
        con.execute(
            """
            CREATE OR REPLACE TABLE silver.order_lines_quarantine AS
            SELECT * EXCLUDE (dq_failed_rules), dq_failed_rules, ? AS _quarantined_at
            FROM evaluated_rows
            WHERE len(dq_failed_rules) > 0
            """,
            [quarantined_at],
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    return con.execute("SELECT count(*) FROM silver.order_lines").fetchone()[0]


def quarantined_rows(con: duckdb.DuckDBPyConnection) -> int:
    return con.execute("SELECT count(*) FROM silver.order_lines_quarantine").fetchone()[0]
