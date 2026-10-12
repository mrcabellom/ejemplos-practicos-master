# Spec Delta

## Purpose

Cargar en la capa bronze los ficheros diarios de pedidos que llegan a landing, sin transformarlos y conservando el origen de cada fila, para poder auditarlos y reprocesarlos.

## ADDED Requirements

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
