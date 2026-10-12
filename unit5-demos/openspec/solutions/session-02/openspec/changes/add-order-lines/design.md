# Design

## Context

`bronze.orders_raw` contiene texto sin validar. Silver es la primera capa con tipos y la base de todos los agregados.

## Goals / Non-Goals

**Goals:**
- Una tabla de líneas de pedido con tipos correctos, sin duplicados ni pedidos cancelados.

**Non-Goals:**
- Reglas de negocio adicionales sobre los valores (por ejemplo, cantidades negativas): no están especificadas.
- Registrar qué filas se excluyen y por qué.

## Decisions

1. **Reconstrucción completa en cada ejecución** (`CREATE OR REPLACE TABLE ... AS SELECT`). El volumen es pequeño y el resultado siempre refleja bronze. Alternativa descartada: actualización incremental, más compleja y sin beneficio con este volumen.
2. **Conversión con `TRY_CAST`**: devuelve NULL en lugar de fallar, y las filas con NULL en columnas obligatorias se excluyen. Alternativa descartada: `CAST`, que haría fallar toda la ejecución por una sola fila errónea.
3. **Deduplicación con `row_number()`** por (`order_id`, `product_sku`), ordenando por `_ingested_at` descendente.

## Risks / Trade-offs

- [Las filas excluidas no dejan registro] → Aceptado en este paso; Operaciones no puede saber cuántas filas se pierden.
