# Spec Delta

## Purpose

Ofrecer en la capa silver una tabla de líneas de pedido tipada y depurada, que sirva de base única para todos los agregados de negocio.

## ADDED Requirements

### Requirement: Líneas de pedido tipadas
La tabla `silver.order_lines` SHALL contener las columnas `order_id`, `order_ts` (TIMESTAMP), `order_date` (DATE derivada de `order_ts`), `store_id`, `customer_email` (en minúsculas y sin espacios), `product_sku`, `category`, `quantity` (INTEGER), `unit_price` (DECIMAL(10,2)) y `status`, y SHALL reconstruirse a partir de `bronze.orders_raw` en cada ejecución.

#### Scenario: Derivación de la fecha de negocio
- **WHEN** bronze contiene la línea del pedido O-1002 con `order_ts` = `2026-10-01T10:05:00`
- **THEN** silver la expone con `order_date` = 2026-10-01

#### Scenario: Normalización del email
- **WHEN** bronze contiene una línea con `customer_email` = ` Ana.Garcia@Example.com `
- **THEN** silver la expone con `customer_email` = `ana.garcia@example.com`

### Requirement: Tratamiento de filas inválidas
Las filas de bronze sin `order_id`, o cuyo `order_ts`, `quantity` o `unit_price` no se puedan convertir a su tipo, SHALL excluirse de `silver.order_lines`.

#### Scenario: Precio no numérico
- **WHEN** bronze contiene la línea del pedido O-1007 con `unit_price` = `abc`
- **THEN** el pedido O-1007 no aparece en `silver.order_lines`

#### Scenario: Línea sin identificador de pedido
- **WHEN** bronze contiene una línea con `order_id` vacío
- **THEN** esa línea no aparece en `silver.order_lines`

### Requirement: Deduplicación de líneas
`silver.order_lines` SHALL contener como máximo una fila por combinación (`order_id`, `product_sku`), conservando la de `_ingested_at` más reciente.

#### Scenario: Línea repetida en el fichero
- **WHEN** el fichero `2026-10-01.csv` contiene dos veces la línea (O-1003, SKU-PAN-BARRA)
- **THEN** `silver.order_lines` contiene una única fila para (O-1003, SKU-PAN-BARRA)

### Requirement: Exclusión de pedidos cancelados
Las líneas con `status` = `cancelled` SHALL excluirse de `silver.order_lines`.

#### Scenario: Pedido cancelado
- **WHEN** bronze contiene el pedido O-1005 con `status` = `cancelled`
- **THEN** O-1005 no aparece en `silver.order_lines`
