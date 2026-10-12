# Spec Delta

## MODIFIED Requirements

### Requirement: Fichero diario para Finanzas
El pipeline SHALL generar en cada ejecución el fichero `exports/finance_daily_sales.csv` con la cabecera `date;store;orders;gross_sales;returns;net_sales_ex_vat` y una línea por fila de `gold.daily_sales`, ordenadas por fecha y tienda.

#### Scenario: Contenido del export
- **WHEN** `gold.daily_sales` contiene (2026-10-01, BCN-014) con 1 pedido, `gross_revenue` 1,60, `returns_amount` 19,50 y `net_revenue` -14,58
- **THEN** el fichero contiene la línea `2026-10-01;BCN-014;1;1,60;19,50;-14,58`
