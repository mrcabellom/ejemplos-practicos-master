# Proposal

## Why

Finanzas cuadra cada mes las ventas de Power BI con contabilidad y no le salen: `total_amount` incluye IVA y no descuenta devoluciones, mientras que contabilidad trabaja con ventas netas sin IVA. En el cierre de septiembre hubo 38.000 € de diferencia y dos días de trabajo manual en Excel para explicarla.

## What Changes

- **BREAKING** `gold.daily_sales` sustituye `total_amount` por tres métricas: `gross_revenue` (ventas brutas con IVA), `returns_amount` (devoluciones con IVA) y `net_revenue` (ventas netas de devoluciones y sin IVA).
- Las devoluciones dejan de ignorarse y pasan a restar en `net_revenue`.
- Nueva tabla de tipos de IVA por categoría de producto; una categoría sin tipo detiene la ejecución.
- Vista de compatibilidad `gold.daily_sales_v1` con el esquema anterior hasta el 2026-12-31.
- **BREAKING** El export de Finanzas cambia sus columnas.

## Capabilities

### New Capabilities
<!-- Ninguna -->

### Modified Capabilities
- `daily-sales`: nuevas métricas bruto/devoluciones/neto, IVA por categoría, eliminación del requisito "Devoluciones excluidas de las métricas" y vista de compatibilidad.
- `finance-export`: nuevas columnas del fichero.

## Impact

- Tablas: `gold.daily_sales` (cambio de esquema), nueva vista `gold.daily_sales_v1`, nueva tabla de referencia `gold.vat_rates`.
- Consumidores:
  - Power BI (12 informes usan `total_amount`): migrar a `gross_revenue` o `net_revenue` antes del 2026-12-31; mientras tanto pueden usar `gold.daily_sales_v1`.
  - Macro de Excel de Finanzas: Marta (Control de Gestión) valida las nuevas columnas.
- Código: transformación de gold, export de Finanzas, fichero de tipos de IVA y tests.
