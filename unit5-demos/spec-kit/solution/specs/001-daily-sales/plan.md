# Implementation Plan: Ventas diarias por tienda

**Branch**: `001-daily-sales` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-daily-sales/spec.md`

## Summary

Pipeline batch que lee `data/raw/orders.csv`, clasifica cada línea como válida o rechazada (con
un único motivo), y publica dos tablas en DuckDB: `daily_sales` (tienda × día de Madrid) y
`rejected_lines`. Toda la lógica es SQL dentro de un módulo Python; cada tabla se reconstruye
entera en cada ejecución (`CREATE OR REPLACE`), lo que la hace idempotente.

## Technical Context

**Language/Version**: Python 3.12 (`.python-version`)

**Primary Dependencies**: duckdb (motor SQL y lector de CSV)

**Storage**: fichero DuckDB local (`warehouse.duckdb`); `:memory:` en tests

**Testing**: pytest con el propio `data/raw/orders.csv` como fixture (14 líneas)

**Target Platform**: ejecución local / job batch diario

**Project Type**: pipeline batch con CLI (`python -m daily_sales`)

**Performance Goals**: no aplica a este volumen (cientos de miles de líneas/día caben de sobra en DuckDB)

**Constraints**: importes en DECIMAL; día de negocio en Europe/Madrid

**Scale/Scope**: 2 tiendas en el ejemplo; 1 CSV diario

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo se cumple | Estado |
|---|---|---|
| I. Idempotent Pipelines | `CREATE OR REPLACE TABLE` en todas las tablas; test de doble ejecución | ✅ |
| II. Exact Money | `unit_price DECIMAL(10,2)`, `gross_revenue DECIMAL(12,2)` | ✅ |
| III. No Silent Drops | tabla `rejected_lines`; test `leídas = válidas + rechazadas` | ✅ |
| IV. Tests With Concrete Figures | tests con las cifras exactas de la spec | ✅ |
| V. Keep It Small | un módulo, SQL plano, sin orquestador | ✅ |

Re-check tras Phase 1: sin cambios, sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/001-daily-sales/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── tables.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
data/raw/orders.csv          # entrada (y fixture de tests)
src/daily_sales/
├── __init__.py
├── __main__.py              # CLI
└── pipeline.py              # SQL de carga, clasificación y agregación
tests/
└── test_pipeline.py         # un test por escenario de aceptación
```

**Structure Decision**: proyecto único con layout `src/`; el volumen no justifica capas
bronze/silver/gold separadas (principio V).

## Complexity Tracking

Sin violaciones de la constitución que justificar.
