# Tasks

## 1. Estructura del proyecto

- [ ] 1.1 Crear el paquete `mercaluz/` con `config.py` (rutas de landing, warehouse y exports, y conexión a DuckDB que crea los schemas bronze, silver y gold); verificar que `uv run python -c "import mercaluz.config"` no da error

## 2. Carga en bronze

- [ ] 2.1 Implementar la carga de un fichero de landing en `bronze.orders_raw` con todas las columnas como texto, `_source_file` e `_ingested_at`; verificar con un test que `2026-10-01.csv` carga 10 filas con `_source_file` = `2026-10-01.csv`
- [ ] 2.2 Verificar con un test que la línea O-1007 conserva `unit_price` = `abc`
- [ ] 2.3 Fallar con un error que menciona la ruta si no existe el fichero; verificar con un test para 2026-09-30 que bronze no cambia

## 3. Punto de entrada

- [ ] 3.1 Crear `run_pipeline.py` con `--date` y `--all` que muestra `[bronze] <fecha>: <n> rows loaded`; verificar que `uv run python run_pipeline.py --all` carga 10 y 5 filas
