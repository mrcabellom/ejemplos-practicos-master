# Spec Delta

## ADDED Requirements

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
