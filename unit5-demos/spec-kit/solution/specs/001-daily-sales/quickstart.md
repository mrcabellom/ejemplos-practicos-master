# Quickstart: Ventas diarias por tienda

Guía para validar la feature de principio a fin.

## 1. Ejecutar los tests

```bash
uv run pytest -q
```

Todos deben pasar. Cada test corresponde a un escenario de [spec.md](spec.md).

## 2. Ejecutar el pipeline

```bash
uv run python -m daily_sales data/raw/orders.csv --db warehouse.duckdb
```

Salida esperada:

```text
Lines read: 14
  rejected [duplicate]: 1
  rejected [missing_store]: 1
  rejected [non_positive_quantity]: 2
  rejected [not_completed]: 1
daily_sales rows: 4
```

Seguida de las 4 filas del escenario 1 de US1.

## 3. Comprobar la idempotencia

Ejecuta el paso 2 otra vez: la salida debe ser idéntica.
