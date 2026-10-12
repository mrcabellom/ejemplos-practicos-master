# orders-ingestion Specification

## Purpose

Cargar en la capa bronze los ficheros diarios de pedidos que llegan a landing, sin transformarlos y conservando el origen de cada fila, para poder auditarlos y reprocesarlos.

## Requirements

### Requirement: Carga diaria de ficheros de pedidos
El pipeline SHALL cargar el fichero `data/landing/orders/<YYYY-MM-DD>.csv` de la fecha solicitada en la tabla `bronze.orders_raw`, con todas las columnas del CSV como texto y sin descartar ni corregir ninguna fila. Cada fila SHALL incluir `_source_file` (nombre del fichero) e `_ingested_at` (instante de la carga en UTC).

#### Scenario: Carga de un día
- **WHEN** se ejecuta el pipeline para la fecha 2026-10-01
- **THEN** `bronze.orders_raw` contiene las 10 filas de `2026-10-01.csv`
- **AND** todas tienen `_source_file` = `2026-10-01.csv`

#### Scenario: Valor no numérico conservado
- **WHEN** el fichero `2026-10-01.csv` contiene la línea del pedido O-1007 con `unit_price` = `abc`
- **THEN** bronze conserva el valor `abc` sin modificarlo

### Requirement: Fichero de pedidos ausente
Si no existe el fichero de la fecha solicitada, el pipeline MUST terminar con un error que indique la ruta esperada, sin cargar ninguna fila.

#### Scenario: Fecha sin fichero
- **WHEN** se ejecuta el pipeline para la fecha 2026-09-30 y no existe `2026-09-30.csv`
- **THEN** la ejecución termina con un error que menciona `2026-09-30.csv`
- **AND** `bronze.orders_raw` no cambia

### Requirement: Reprocesado de una fecha ya cargada
Al cargar un fichero que ya se había cargado antes, el pipeline SHALL sustituir de forma atómica todas las filas de `bronze.orders_raw` con ese `_source_file` por el contenido actual del fichero.

#### Scenario: Doble ejecución del mismo día
- **WHEN** se ejecuta dos veces el pipeline para la fecha 2026-10-01 sin que el fichero cambie
- **THEN** `bronze.orders_raw` contiene exactamente 10 filas con `_source_file` = `2026-10-01.csv`

#### Scenario: Fichero corregido que elimina una línea
- **WHEN** se carga `2026-10-02.csv` con 5 filas y después se recibe una versión corregida con 4 filas, sin la línea del pedido O-1011
- **THEN** `bronze.orders_raw` contiene 4 filas con `_source_file` = `2026-10-02.csv`
- **AND** el pedido O-1011 no aparece en `silver.order_lines`

#### Scenario: Fallo a mitad de la sustitución
- **WHEN** la carga del fichero corregido falla después de eliminar las filas anteriores
- **THEN** `bronze.orders_raw` conserva las filas de la carga anterior
