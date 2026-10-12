# Spec Delta

## Purpose

Publicar en la capa gold las ventas diarias por tienda que consumen los informes de Power BI.

## ADDED Requirements

### Requirement: Ventas diarias por tienda
La tabla `gold.daily_sales` SHALL contener una fila por (`order_date`, `store_id`) con `orders_count` (número de pedidos distintos con líneas `completed`) y `total_amount` (suma de `quantity * unit_price` de las líneas `completed`, IVA incluido, DECIMAL(12,2)), y SHALL reconstruirse a partir de `silver.order_lines` en cada ejecución.

#### Scenario: Ventas de una tienda en un día
- **WHEN** el 2026-10-01 la tienda MAD-001 tiene las líneas completadas 6 x 0,95 y 1 x 8,49 (pedido O-1001) y 1 x 11,90 (pedido O-1002)
- **THEN** `gold.daily_sales` contiene para (2026-10-01, MAD-001) `orders_count` = 2 y `total_amount` = 26,09

### Requirement: Devoluciones excluidas de las métricas
Las líneas con `status` = `returned` SHALL NOT contribuir a ninguna métrica de `gold.daily_sales`.

#### Scenario: Devolución no contabilizada
- **WHEN** el 2026-10-01 la tienda BCN-014 tiene una línea completada de 2 x 0,80 y el pedido O-1004 devuelto por 19,50
- **THEN** `gold.daily_sales` contiene para (2026-10-01, BCN-014) `orders_count` = 1 y `total_amount` = 1,60
