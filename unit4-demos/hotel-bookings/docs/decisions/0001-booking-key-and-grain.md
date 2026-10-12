# 0001. La clave de negocio de las reservas es `booking_id`

- **Fecha:** 2026-02-10
- **Estado:** aceptada

## Contexto

El motor de reservas y las agencias online envían un evento por cada cambio
de una reserva: alta, confirmación, modificación de fechas o de
habitaciones y cancelación. Por eso, la misma reserva aparece varias veces,
con marcas temporales distintas y, a veces, en extractos de días
diferentes.

## Decisión

`fct_bookings` tiene grain de reserva, identificada por `booking_id`.
Cuando llegan varias versiones, prevalece la de `updated_at` más reciente.

## Alternativas descartadas

- **Una fila por evento.** Conserva el historial, pero el cuadro de
  dirección y el sistema de precios necesitan el estado vigente. Cada
  consumidor tendría que elegir la versión por su cuenta, y alguno lo haría
  mal.
- **Clave compuesta `booking_id` + `updated_at`.** Resuelve la unicidad
  técnica, pero traslada a cada consulta la responsabilidad de quedarse con
  la última versión.

## Consecuencias

Antes de insertar, la carga debe comparar la clave y la marca temporal.
Una carga que solo inserta rompe el grain, y el problema aparece en cuanto
se modifica una reserva o se vuelve a cargar un extracto.
