"""Run the Mercaluz daily orders pipeline.

Usage:
    uv run python run_pipeline.py --date 2026-10-01
    uv run python run_pipeline.py --all
"""

import argparse

from rich.console import Console
from rich.text import Text

from mercaluz.config import Settings, connect
from mercaluz.exports.finance_csv import export_finance_csv
from mercaluz.ingestion.orders import ingest_orders_file, landing_file_for
from mercaluz.transform.gold_daily_sales import build_gold_daily_sales
from mercaluz.transform.silver_orders import build_silver_order_lines, quarantined_rows

console = Console(highlight=False, soft_wrap=True)
STEP_STYLES = {"bronze": "dark_orange3", "silver": "grey70", "gold": "gold1", "export": "cyan"}


def log(step: str, message: str) -> None:
    tag = f"[{step}]".ljust(8)
    console.print(Text.assemble((tag, f"bold {STEP_STYLES[step]}"), f" {message}"))


def run(settings: Settings, dates: list[str]) -> None:
    con = connect(settings)
    try:
        for d in dates:
            loaded = ingest_orders_file(con, landing_file_for(settings.landing_dir, d))
            log("bronze", f"{d}: {loaded} rows loaded")
        log("silver", f"order_lines: {build_silver_order_lines(con)} rows")
        log("silver", f"order_lines_quarantine: {quarantined_rows(con)} rows")
        log("gold", f"daily_sales: {build_gold_daily_sales(con)} rows")
        log("export", str(export_finance_csv(con, settings.exports_dir)))
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--date", help="Business date (YYYY-MM-DD) to process")
    group.add_argument("--all", action="store_true", help="Process every landing file")
    args = parser.parse_args()

    settings = Settings()
    if args.all:
        dates = sorted(p.stem for p in settings.landing_dir.glob("*.csv"))
    else:
        dates = [args.date]
    run(settings, dates)


if __name__ == "__main__":
    main()
