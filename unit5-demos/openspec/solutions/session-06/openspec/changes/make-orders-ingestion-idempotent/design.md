# Design

## Context

La ingesta hace un `INSERT INTO bronze.orders_raw SELECT ... FROM read_csv(...)` cada vez que se ejecuta. Bronze no tiene clave natural: es una copia literal y puede contener filas idénticas (las dos líneas de O-1003). La unidad natural de carga es el **fichero** (`_source_file`), que equivale a una fecha de negocio.

## Goals / Non-Goals

**Goals:**
- Que el pipeline se pueda relanzar sin duplicar datos.
- Que el reprocesado refleje exactamente el último fichero recibido.

**Non-Goals:**
- Conservar el historial de versiones de un fichero.
- Evitar recargar un fichero que no ha cambiado (optimización no necesaria con este volumen).

## Decisions

1. **Sustitución por `_source_file` con DELETE + INSERT dentro de una transacción.** Es sencillo y atómico: si el INSERT falla, la transacción se deshace y las filas anteriores siguen en bronze.
   - Alternativa descartada: **MERGE**. Necesita una clave que identifique cada fila, y bronze no la tiene: las dos líneas de O-1003 son idénticas.
   - Alternativa descartada: **columna de versión de carga** (`_load_id`) y que silver filtre la última versión. Traslada la complejidad a todos los consumidores de bronze.
2. **Nombre del fichero como parámetro SQL** (`WHERE _source_file = ?`): el nombre viene de un sistema externo y no debe insertarse en la consulta con un f-string.

## Risks / Trade-offs

- [Un fichero corregido incompleto sustituye a uno completo] → Fuera de alcance; las reglas de calidad detectan filas inválidas, no filas que faltan.
- [Dos ejecuciones simultáneas del mismo fichero] → DuckDB solo admite un proceso de escritura; en producción, Airflow debe limitarse a una ejecución a la vez.

## Migration Plan

1. Desplegar el código.
2. Reprocesar las fechas ya cargadas: cada recarga sustituye sus duplicados. En local, basta con borrar `warehouse/` y ejecutar `run_pipeline.py --all`.
3. Rollback: desplegar la versión anterior; bronze sigue siendo válido.
