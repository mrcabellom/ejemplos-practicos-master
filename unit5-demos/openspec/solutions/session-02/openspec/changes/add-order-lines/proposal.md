# Proposal

## Why

`bronze.orders_raw` guarda los pedidos como texto y tal como llegan: con duplicados, pedidos cancelados y valores que no son números. Para calcular ventas hace falta una tabla de líneas de pedido con tipos correctos y sin esos problemas.

## What Changes

- Nueva tabla `silver.order_lines`, reconstruida en cada ejecución a partir de bronze.
- Columnas con su tipo (fecha y hora, enteros, decimales) y fecha de negocio derivada.
- Email del cliente normalizado (minúsculas y sin espacios).
- Exclusión de las filas que no se pueden tipar, de las líneas duplicadas y de los pedidos cancelados.

## Capabilities

### New Capabilities
- `order-lines`: líneas de pedido tipadas y depuradas en la capa silver.

### Modified Capabilities
<!-- Ninguna -->

## Impact

- Tablas: nueva `silver.order_lines`.
- Consumidores: base de los agregados de gold (próximo paso).
- Código: transformación bronze → silver, paso nuevo en `run_pipeline.py` y tests.
