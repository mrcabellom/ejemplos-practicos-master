# Spec Delta

## MODIFIED Requirements

### Requirement: Líneas de pedido tipadas
La tabla `silver.order_lines` SHALL contener las columnas `order_id`, `order_ts` (TIMESTAMP), `order_date` (DATE derivada de `order_ts`), `store_id`, `customer_key` (seudónimo definido en la capability `pii-protection`), `product_sku`, `category`, `quantity` (INTEGER), `unit_price` (DECIMAL(10,2)) y `status`, y MUST NOT contener `customer_email`. La tabla SHALL reconstruirse a partir de `bronze.orders_raw` en cada ejecución.

#### Scenario: Derivación de la fecha de negocio
- **WHEN** bronze contiene la línea del pedido O-1002 con `order_ts` = `2026-10-01T10:05:00`
- **THEN** silver la expone con `order_date` = 2026-10-01

#### Scenario: Normalización del email
- **WHEN** bronze contiene una línea con `customer_email` = ` Ana.Garcia@Example.com `
- **THEN** silver la expone con el `customer_key` de `ana.garcia@example.com` y sin columna `customer_email`
