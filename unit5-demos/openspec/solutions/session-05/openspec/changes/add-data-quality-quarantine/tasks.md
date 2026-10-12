# Tasks

## 1. Reglas de calidad

- [ ] 1.1 Evaluar las reglas DQ001–DQ005 en una columna `dq_failed_rules`; verificar con un test que O-1006 incumple DQ003 y O-1007 incumple DQ004

## 2. Cuarentena y silver

- [ ] 2.1 Crear `silver.order_lines_quarantine` en la misma transacción que `silver.order_lines`; verificar con un test que el fichero 2026-10-01 deja 3 filas en cuarentena
- [ ] 2.2 Verificar con un test que una fila con `order_id` vacío y cantidad 0 genera una sola fila con [DQ001, DQ003]
- [ ] 2.3 Verificar con un test que ejecutar dos veces la transformación no duplica la cuarentena
- [ ] 2.4 Actualizar el test existente de silver: el 2026-10-01 quedan 5 líneas (O-1006 pasa a cuarentena); verificar que `uv run pytest` pasa completo

## 3. Pipeline

- [ ] 3.1 Mostrar en `run_pipeline.py` las filas de cuarentena (`[silver] order_lines_quarantine: <n> rows`); verificar que `uv run python run_pipeline.py --all` muestra 3 y que VLC-007 ya no aparece el 2026-10-01 en `gold.daily_sales`
