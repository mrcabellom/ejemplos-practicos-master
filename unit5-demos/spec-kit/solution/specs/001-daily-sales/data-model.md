# Data Model: Ventas diarias por tienda

```text
data/raw/orders.csv ──► raw_order_lines ──► (clasificación) ──┬──► daily_sales     (válidas, agregadas)
                                                              └──► rejected_lines  (rechazadas + motivo)
```

## raw_order_lines (interna)

Copia tipada del CSV más `source_row` (orden de lectura, empieza en 1).

| Campo | Tipo | Descripción |
|---|---|---|
| source_row | BIGINT | posición en el fichero |
| order_id | VARCHAR | |
| line_id | INTEGER | `order_id + line_id` debería ser único (no lo es: duplicados) |
| order_ts | TIMESTAMPTZ | viene en UTC |
| store_id | VARCHAR | vacío → NULL |
| product_id | VARCHAR | |
| quantity | INTEGER | puede ser 0 o negativa |
| unit_price | DECIMAL(10,2) | |
| status | VARCHAR | `completed`, `cancelled`... |

## Reglas de validación (en este orden, gana la primera)

| # | Condición | `reject_reason` |
|---|---|---|
| 1 | no es la primera aparición de `order_id + line_id` | `duplicate` |
| 2 | `store_id` es NULL | `missing_store` |
| 3 | `status <> 'completed'` | `not_completed` |
| 4 | `quantity <= 0` | `non_positive_quantity` |

## daily_sales y rejected_lines (publicadas)

Ver el contrato en [contracts/tables.md](contracts/tables.md).
