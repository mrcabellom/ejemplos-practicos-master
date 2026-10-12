# Tasks

## 1. Tipos de IVA

- [ ] 1.1 Crear `mercaluz/reference/vat_rates.csv` y cargarlo en `gold.vat_rates`; verificar con un test que contiene las 4 categorías con sus tipos
- [ ] 1.2 Fallar si silver tiene categorías sin tipo; verificar con un test que una línea `mascotas` hace fallar la ejecución mencionando `mascotas` y sin modificar gold

## 2. Nuevas métricas en gold

- [ ] 2.1 Reescribir `gold.daily_sales` con `gross_revenue`, `returns_amount` y `net_revenue`; verificar con tests que (2026-10-01, MAD-001) da 26,09 / 0,00 / 23,03 y (2026-10-01, BCN-014) da 1,60 / 19,50 / -14,58
- [ ] 2.2 Verificar con un test que (2026-10-02, MAD-001), con un pedido completado y otro devuelto, tiene `orders_count` = 1 y `net_revenue` = -7,00
- [ ] 2.3 Crear la vista `gold.daily_sales_v1`; verificar con un test que devuelve `total_amount` = 26,09 para (2026-10-01, MAD-001)
- [ ] 2.4 Actualizar los tests existentes de gold que usaban `total_amount`

## 3. Export de Finanzas

- [ ] 3.1 Cambiar la cabecera y las columnas del export; verificar con un test que contiene `2026-10-01;BCN-014;1;1,60;19,50;-14,58` y que `uv run pytest` pasa completo

## Workflow follow-up

- Enviar a BI la lista de informes que deben migrar antes del 2026-12-31.
- Crear el change `remove-daily-sales-v1-view` con fecha objetivo 2026-12-31.
