# Proposal

## Why

Las cajas y la tienda online envían cada día un fichero CSV con las líneas de pedido a `data/landing/orders/`. Hoy esos ficheros no se cargan en ningún sitio, por lo que no se pueden consultar con SQL ni sirven de base para los informes de ventas. Es el primer paso del pipeline.

## What Changes

- Carga de un fichero diario de pedidos en la tabla `bronze.orders_raw`, sin transformarlo.
- Cada fila guarda el nombre del fichero de origen y el instante de carga.
- Error explícito si no existe el fichero de la fecha solicitada.
- Punto de entrada `run_pipeline.py` para cargar una fecha (`--date`) o todos los ficheros (`--all`).

## Capabilities

### New Capabilities
- `orders-ingestion`: carga de los ficheros diarios de pedidos en la capa bronze.

### Modified Capabilities
<!-- Ninguna -->

## Impact

- Tablas: nueva `bronze.orders_raw` en el warehouse local `warehouse/mercaluz.duckdb`.
- Consumidores: ninguno todavía; bronze es la base de las siguientes capas.
- Código: paquete `mercaluz/` (configuración e ingesta), `run_pipeline.py` y tests.
