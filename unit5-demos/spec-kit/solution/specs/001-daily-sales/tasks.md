---
description: "Task list for 001-daily-sales"
---

# Tasks: Ventas diarias por tienda

**Input**: Design documents from `/specs/001-daily-sales/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: incluidos; la constitución (principio IV) los exige con cifras concretas.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)

## Phase 1: Setup

- [x] T001 Crear el paquete `src/daily_sales/` con `__init__.py` y añadir el build-system a `pyproject.toml`
- [x] T002 [P] Crear `tests/test_pipeline.py` con un fixture que ejecute el pipeline sobre `data/raw/orders.csv`

## Phase 2: Foundational

- [x] T003 Cargar el CSV tipado en `raw_order_lines` con `source_row` en `src/daily_sales/pipeline.py`
- [x] T004 Clasificar líneas con `reject_reason` (orden de data-model.md) y `sales_date` en Europe/Madrid en `src/daily_sales/pipeline.py`

**Checkpoint**: las líneas están clasificadas; ya se pueden construir las dos tablas.

## Phase 3: User Story 1 - Consultar ventas diarias por tienda (Priority: P1) 🎯 MVP

**Goal**: `daily_sales` con las cifras exactas de la spec.

**Independent Test**: `uv run pytest -q -k "daily_sales or madrid or duplicate or rerun or decimal"`

- [x] T005 [P] [US1] Test de las 4 filas esperadas en `tests/test_pipeline.py`
- [x] T006 [P] [US1] Test del corte de día en hora de Madrid (O-1006) en `tests/test_pipeline.py`
- [x] T007 [P] [US1] Test de la línea duplicada O-1003 en `tests/test_pipeline.py`
- [x] T008 [P] [US1] Test de idempotencia (doble ejecución sobre el mismo fichero DuckDB) en `tests/test_pipeline.py`
- [x] T009 [US1] Construir `daily_sales` según contracts/tables.md en `src/daily_sales/pipeline.py`

**Checkpoint**: US1 funciona y se puede entregar sola.

## Phase 4: User Story 2 - Saber por qué se descartó una línea (Priority: P2)

**Goal**: `rejected_lines` y el balance leídas = válidas + rechazadas.

**Independent Test**: `uv run pytest -q -k "reason or silent"`

- [x] T010 [P] [US2] Test de las 5 líneas rechazadas y sus motivos en `tests/test_pipeline.py`
- [x] T011 [P] [US2] Test del balance de filas (14 = 9 + 5) en `tests/test_pipeline.py`
- [x] T012 [US2] Construir `rejected_lines` en `src/daily_sales/pipeline.py`

## Phase 5: Polish

- [x] T013 CLI `python -m daily_sales` con el resumen de filas en `src/daily_sales/__main__.py`
- [x] T014 Ejecutar quickstart.md y verificar la salida esperada

## Dependencies & Execution Order

- Setup (T001–T002) → Foundational (T003–T004) → US1 (T005–T009) → US2 (T010–T012) → Polish.
- Dentro de cada historia, los tests [P] se escriben primero y deben fallar antes de implementar.
