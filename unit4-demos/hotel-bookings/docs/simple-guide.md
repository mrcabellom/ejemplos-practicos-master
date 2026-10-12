# El proyecto, sin tecnicismos

## La idea en una frase

Cada día llegan archivos con reservas de hotel y con los cambios que han
sufrido. El objetivo es convertirlos en una tabla fiable, en la que cada
reserva aparezca una sola vez, para saber qué ocupación tuvo cada hotel
cada noche.

## El libro de reservas de recepción

Los archivos de `data/raw/` funcionan como las hojas que llegan cada
mañana a recepción con las novedades del día anterior. Una hoja puede traer
una reserva nueva, pero también un cambio en una reserva ya conocida: el
cliente añade una habitación, confirma una reserva provisional o la
cancela.

Por eso, dos filas con el mismo `booking_id` no son dos reservas, sino dos
noticias sobre la misma reserva.

## Qué es la granularidad

La granularidad responde a una pregunta:

> ¿Qué representa exactamente cada fila de esta tabla?

En `fct_bookings`, cada fila debe ser **una reserva**. `booking_id` es su
identificador, como el localizador que se entrega al cliente. Si una
reserva aparece varias veces en los archivos, se guarda una sola fila: la
versión con el `updated_at` más reciente.

| Resultado | Cada fila representa | Ejemplo |
| --- | --- | --- |
| `fct_bookings` (tabla) | Una reserva | El estado actual de la reserva B-3002 |
| Ocupación diaria (consulta, ampliación opcional) | Un hotel en una noche | Málaga, noche del 2 de marzo |

Son dos granularidades distintas porque responden a preguntas distintas.

## El problema: un hotel por encima de su capacidad

Si el programa se limita a añadir cada fila que lee, guarda la misma
reserva varias veces y, al sumar habitaciones, cuenta de más.

| Lo que llega | Qué significa |
| --- | --- |
| B-3002, Málaga, 2 habitaciones, día 1 | Se crea la reserva |
| B-3002, Málaga, 3 habitaciones, día 2 | El cliente añade una habitación |

Es una única reserva de 3 habitaciones, no dos reservas de 2 y de 3. Si se
guardan las dos filas, Málaga suma 5 habitaciones donde debería haber 3, y
la noche del 2 de marzo aparece con 9 habitaciones ocupadas en un hotel de
8: **un 112 %**.

Con las cancelaciones ocurre lo mismo. Si se guardan la fila «confirmada»
y la fila «cancelada», la reserva sigue ocupando habitaciones aunque el
cliente ya no vaya a venir. Es lo que sucede en Madrid con `B-3008`.

## Por qué importa fuera del equipo de datos

El sistema de precios se basa en la ocupación: si cree que un hotel está
lleno, sube la tarifa. Un error en una tabla termina en quejas en
recepción. Por eso la incidencia la abre el departamento de Revenue y no
el equipo de datos.

## Cómo se demuestra el arreglo

1. Cargar dos veces el mismo archivo deja la tabla igual.
2. Una versión nueva de una reserva sustituye a la anterior.
3. Una versión antigua cargada después no sobrescribe a la nueva.

Los tests actuales no comprueban nada de esto, y por eso pasan aunque el
defecto siga ahí. `python tasks.py acceptance` sí lo comprueba: es el
oráculo de la incidencia y pasa a verde cuando la carga es correcta.

## Qué fecha se usa

Conviene no confundir dos fechas:

- **La noche de la estancia:** de `check_in` a `check_out`, sin incluir la
  noche de salida. Es la que cuenta para la ocupación.
- **La fecha de negocio** (`business_date`): el día en que se hizo el
  cambio, tomado de `updated_at`. No coincide necesariamente con el día en
  que llegó el archivo: una agencia puede enviar con retraso una reserva
  hecha el día anterior, como ocurre con `B-3010`.

## Lo que el informe no muestra

El informe de ocupación solo incluye las noches con alguna habitación
ocupada. Si Barcelona no tuvo reservas la noche del 2 de marzo, esa noche
no aparece. Para quien fija los precios, una noche ausente no equivale a
una noche al 0 %.

Una consulta de ocupación completa tendría una fila por hotel y noche,
haya reservas o no: del 1 al 5 de marzo, con tres hoteles, 15 filas.
Figura como ampliación opcional del plan de trabajo.

## Las filas rechazadas

Las reservas que no cumplen las reglas no se descartan: se guardan en
`quarantine` junto con el motivo. En los datos actuales hay tres:

| Reserva | Motivo del rechazo |
| --- | --- |
| `B-3005` | La fecha de salida es anterior a la de entrada |
| `B-3006` | Corresponde a un hotel que no existe |
| `B-3011` | Está en dólares y el contrato solo admite euros |

La última es una reserva real que no se cuenta en la ocupación. Qué hacer
con ella es una decisión de negocio, no del código.

## Corregir el código no corrige los datos

Si el almacén ya contiene filas duplicadas, corregir el programa no las
elimina. Hay que volver a cargar los archivos desde cero, y eso es un
**reproceso**: sigue el procedimiento de `docs/runbooks/backfill.md` y
requiere autorización, porque mientras dura, el sistema de precios trabaja
con datos incompletos.

## Estado actual del código

Mientras INC-0142 siga abierta, `src/pipeline/load.py` añade cada fila sin
comprobar si la reserva ya existe. Los tests pasan, `reconcile` detecta
duplicados, `acceptance` falla sus cinco criterios y el informe muestra el
112 %. El plan de trabajo (`playbook/`) lo resuelve con Claude Code.

## Glosario

| Término | Significado |
| --- | --- |
| Reserva (`booking`) | Solicitud de alojamiento de un cliente, identificada por `booking_id` |
| Versión | Cada cambio de una reserva: alta, confirmación, modificación o cancelación |
| Clave de negocio | Identificador que indica si dos filas se refieren a lo mismo; aquí, `booking_id` |
| Granularidad (`grain`) | Lo que representa cada fila de una tabla |
| Ocupación | Habitaciones ocupadas dividido entre habitaciones del hotel, para una noche |
| Cuarentena (`quarantine`) | Tabla donde se guardan las filas rechazadas con su motivo |
| Reproceso | Nueva carga de los datos desde el origen con el código corregido |
