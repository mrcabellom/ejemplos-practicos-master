# Research: Ventas diarias por tienda

## 1. Cómo calcular el día de Madrid a partir de un timestamp UTC

- **Decision**: leer `order_ts` como `TIMESTAMPTZ` y convertir con `timezone('Europe/Madrid', order_ts)` antes de truncar a `DATE`.
- **Rationale**: DuckDB aplica las reglas de horario de verano (UTC+2 en octubre, UTC+1 en invierno); no hay que sumar horas manualmente.
- **Alternatives considered**: sumar `INTERVAL 2 HOUR` (falla en invierno); cortar en UTC (asigna `O-1006` al día equivocado).

## 2. Cómo detectar duplicados y conservar "la primera"

- **Decision**: numerar las filas en orden de lectura (`source_row`) y usar `row_number() OVER (PARTITION BY order_id, line_id ORDER BY source_row)`; la fila 1 sigue, las demás son `duplicate`.
- **Rationale**: es determinista y deja rastro de qué copia se descartó.
- **Alternatives considered**: `SELECT DISTINCT` (descarta sin rastro, viola el principio III).

## 3. Cómo garantizar la idempotencia

- **Decision**: reconstrucción completa con `CREATE OR REPLACE TABLE` en cada ejecución.
- **Rationale**: el CSV diario es pequeño; reconstruir es más simple que hacer MERGE.
- **Alternatives considered**: MERGE por clave (necesario solo con carga incremental, fuera de alcance).

## 4. Tipo de dato para importes

- **Decision**: `DECIMAL(10,2)` en la entrada y `DECIMAL(12,2)` en los agregados.
- **Rationale**: principio II; la suma de DECIMAL en DuckDB es exacta.
- **Alternatives considered**: `DOUBLE` (prohibido por la constitución).
