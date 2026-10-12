# Contrato de datos: `fct_bookings`

## Grain

Una fila por reserva. `booking_id` es la clave de negocio y es única en la
tabla.

## Semántica

Cada fila representa **la última versión aceptada** de una reserva. Una
reserva cambia a lo largo del tiempo: pasa de `tentative` a `confirmed`,
cambia de fechas o de número de habitaciones, o se cancela. Cada cambio
llega como una fila nueva en el extracto del día.

Cuando llegan dos versiones de la misma reserva, prevalece la de
`updated_at` más reciente, **sea cual sea el orden en que se carguen**.
Volver a cargar un extracto idéntico no modifica la tabla.

## Fecha de negocio

`business_date` se obtiene de `updated_at`, nunca del nombre del extracto
ni de la hora de carga. Una reserva que una agencia envía con retraso se
asigna al día en que se realizó.

## Columnas

| Columna | Tipo | Notas |
| --- | --- | --- |
| `booking_id` | TEXT | Clave de negocio. Única. No nula. |
| `hotel_id` | TEXT | Debe existir en `data/reference/hotels.json`. |
| `channel` | TEXT | `direct`, `booking`, `expedia`. |
| `check_in` | TEXT | Fecha de entrada, ISO. |
| `check_out` | TEXT | Fecha de salida, ISO. Posterior a `check_in`. |
| `rooms` | INTEGER | Habitaciones reservadas. Al menos 1. |
| `status` | TEXT | `tentative`, `confirmed`, `cancelled`. |
| `total_amount` | REAL | Importe total de la estancia. No negativo. |
| `currency` | TEXT | Solo `EUR` en esta versión. |
| `updated_at` | TEXT | Marca temporal del cambio en origen, UTC. |
| `business_date` | TEXT | Derivada de `updated_at`. |
| `run_id` | TEXT | Ejecución que escribió la fila. |

La tabla no guarda datos personales del huésped. El extracto tampoco los
incluye: los conserva el motor de reservas.

## Regla de ocupación

Una reserva ocupa sus `rooms` cada noche del intervalo
`[check_in, check_out)`: el huésped deja el hotel la mañana de `check_out`.
Solo cuentan las reservas en estado `confirmed`. La capacidad de cada hotel
figura en `data/reference/hotels.json`.

Como consecuencia directa del grain, si una reserva aparece dos veces, sus
habitaciones se cuentan dos veces.

## Filas rechazadas

Una fila que incumple cualquier regla no se descarta: se escribe en
`quarantine` con su `reason_code`, su `run_id` y el contenido original
(`payload`).

| `reason_code` | Condición |
| --- | --- |
| `missing_booking_id` | Sin `booking_id` |
| `unknown_hotel` | `hotel_id` fuera de la referencia |
| `invalid_stay` | Fechas ilegibles o `check_out` no posterior a `check_in` |
| `invalid_rooms` | `rooms` no es un entero mayor o igual que 1 |
| `unknown_status` | Estado fuera de la lista |
| `missing_amount`, `negative_amount` | Importe ausente o negativo |
| `unsupported_currency` | Moneda distinta de `EUR` |

## Consumidores

- **Cuadro de dirección:** ocupación diaria por hotel.
- **Sistema de precios:** fija la tarifa del día siguiente a partir de la
  ocupación.
- **Cierre contable mensual:** importe confirmado por hotel.

Cualquier cambio de grain o de tipos obliga a avisar a los tres
consumidores y a publicar una nueva versión de este contrato.
