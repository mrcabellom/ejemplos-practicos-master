# Tasks

## 1. Fichero para Finanzas

- [ ] 1.1 Generar `exports/finance_daily_sales.csv` con la cabecera `date;store;orders;total_amount` y una línea por fila de gold ordenadas por fecha y tienda; verificar con un test que contiene `2026-10-01;MAD-001;2;26,09`
- [ ] 1.2 Verificar con un test que los importes usan coma decimal y dos decimales: `2026-10-01;BCN-014;1;1,60`

## 2. Pipeline

- [ ] 2.1 Añadir el paso de export a `run_pipeline.py` (`[export] <ruta del fichero>`); verificar que `uv run python run_pipeline.py --all` genera el fichero con 6 líneas de datos
