# Contract: tablas publicadas

> En Data Engineering, el "contrato" no es una API REST: es el esquema de las tablas que leen
> otros equipos. Cambiar un nombre, un tipo o la clave es un *breaking change* para ellos.

## daily_sales

**Consumidores**: Operaciones (informe diario de tiendas)
**Clave**: (`store_id`, `sales_date`), única
**Granularidad**: una fila por tienda y día de Madrid con al menos una línea válida

| Columna | Tipo | Nulo | Definición |
|---|---|---|---|
| store_id | VARCHAR | no | tienda |
| sales_date | DATE | no | día del pedido en hora de Europe/Madrid |
| orders | INTEGER | no | nº de `order_id` distintos con alguna línea válida |
| units | INTEGER | no | suma de `quantity` de las líneas válidas |
| gross_revenue | DECIMAL(12,2) | no | suma de `quantity × unit_price` de las líneas válidas |

## rejected_lines

**Consumidores**: equipo de datos (investigación de descuadres)
**Clave**: `source_row`, única

| Columna | Tipo | Nulo | Definición |
|---|---|---|---|
| source_row | BIGINT | no | posición de la línea en el CSV de entrada |
| order_id | VARCHAR | no | |
| line_id | INTEGER | no | |
| reject_reason | VARCHAR | no | uno de: `duplicate`, `missing_store`, `not_completed`, `non_positive_quantity` |

## Invariante

`count(raw_order_lines) = count(líneas válidas) + count(rejected_lines)`
