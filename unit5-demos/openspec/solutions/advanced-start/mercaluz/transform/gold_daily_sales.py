"""silver.order_lines -> gold.daily_sales: sales per business date and store (completed lines only)."""

import duckdb


def build_gold_daily_sales(con: duckdb.DuckDBPyConnection) -> int:
    con.execute(
        """
        CREATE OR REPLACE TABLE gold.daily_sales AS
        SELECT
            order_date,
            store_id,
            count(DISTINCT order_id)                          AS orders_count,
            CAST(sum(quantity * unit_price) AS DECIMAL(12,2)) AS total_amount
        FROM silver.order_lines
        WHERE status = 'completed'
        GROUP BY order_date, store_id
        ORDER BY order_date, store_id
        """
    )
    return con.execute("SELECT count(*) FROM gold.daily_sales").fetchone()[0]
