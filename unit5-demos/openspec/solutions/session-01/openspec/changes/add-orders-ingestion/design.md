# Design

## Context

Es la primera pieza del pipeline: no hay código previo. Los ficheros de landing pueden contener errores (precios no numéricos, líneas sin identificador), y bronze debe guardarlos tal como llegan.

## Goals / Non-Goals

**Goals:**
- Una copia fiel de cada fichero en `bronze.orders_raw`, consultable con SQL.
- Saber de qué fichero viene cada fila y cuándo se cargó.

**Non-Goals:**
- Validar, tipar o limpiar los datos (corresponde a silver).
- Definir qué ocurre al cargar dos veces el mismo fichero (se tratará más adelante).

## Decisions

1. **Todas las columnas como texto (`VARCHAR`).** Si bronze tipara los datos, un precio `abc` haría fallar la carga o se perdería. Alternativa descartada: tipar en bronze y rechazar el fichero entero ante el primer error.
2. **Lectura directa del CSV con DuckDB (`read_csv`)** en una única sentencia `INSERT ... SELECT`. Alternativa descartada: leer el fichero con Python fila a fila, más lento y con más código.
3. **`_ingested_at` en UTC sin zona horaria**, según las convenciones del equipo.

## Risks / Trade-offs

- [Cargar dos veces el mismo fichero puede duplicar filas] → Comportamiento no especificado en este change; se abordará cuando sea necesario reprocesar.
