"""Shared fixtures: every test works on a copy of the landing files and a temporary warehouse."""

import shutil
from pathlib import Path

import pytest

from mercaluz.config import Settings, connect

LANDING = Path(__file__).resolve().parent.parent / "data" / "landing" / "orders"


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    landing = tmp_path / "landing"
    shutil.copytree(LANDING, landing)
    return Settings(
        landing_dir=landing,
        warehouse_path=tmp_path / "warehouse" / "test.duckdb",
        exports_dir=tmp_path / "exports",
    )


@pytest.fixture
def con(settings: Settings):
    c = connect(settings)
    yield c
    c.close()
