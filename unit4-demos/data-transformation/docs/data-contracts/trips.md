# Contrato de datos: viajes

Qué se garantiza en `output/`.

## Un viaje, una fila

`trip_id` identifica el viaje. Si llega más de una vez (el operador a veces
reenvía viajes), se conserva la **primera** aparición, por orden de entrega
y de fila. Las demás van a `rejected.csv` con motivo `viaje duplicado`.

## `trips.csv`

| Columna | Formato | Ejemplo |
| --- | --- | --- |
| `trip_id` | Texto | `T0001` |
| `bike_id` | Texto | `B101` |
| `start_time`, `end_time` | ISO `AAAA-MM-DDTHH:MM` | `2026-10-05T08:02` |
| `duration_min` | Entero entre **1 y 240** | `17` |
| `start_station`, `end_station` | Una del catálogo | `Atocha` |
| `user_type` | `member` o `casual` | `member` |
| `source` | Entrega de origen | `week-1.csv` |

Catálogo de estaciones: Sol, Atocha, Retiro, Moncloa, Chamberí, Lavapiés.

## `rejected.csv`

Un viaje que no se puede limpiar no desaparece: va aquí con sus valores
originales, su entrega (`source`) y su motivo (`reason`).

## `daily_usage.csv`

Una fila por fecha de inicio y estación de salida, con `departures` y
`avg_minutes`. La suma de `departures` es igual al número de viajes.

## Entregas

- **Balance:** viajes leídos de una entrega = válidos + rechazados.
- **Calidad:** si se rechaza más del **10 %** de una entrega, la entrega no
  se da por buena. Los duplicados no cuentan: reenviar viajes es normal.
