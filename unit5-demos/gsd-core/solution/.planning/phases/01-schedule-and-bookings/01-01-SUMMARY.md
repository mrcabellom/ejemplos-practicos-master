---
phase: 01-schedule-and-bookings
plan: 01
subsystem: api
tags: [fastapi, sqlite, pytest]

provides:
  - "schedule.py: day_slots, is_open, overlaps, booking_error"
  - "create_app(db_path, clock) con GET /slots, POST /appointments y GET /appointments/{id}"
  - "Persistencia en SQLite (store.py)"

key-files:
  created: [src/kinesia/schedule.py, src/kinesia/store.py, src/kinesia/api.py, src/kinesia/main.py, tests/test_schedule.py, tests/test_api.py]

key-decisions:
  - "Reglas de agenda sin E/S para testearlas sin base de datos"
  - "El solape del mismo fisio se comprueba antes que el del paciente: con ambos, gana slot_taken"

requirements-completed: ["AGEN-01", "AGEN-02", "RES-01", "RES-02", "RES-03", "RES-04"]

coverage:
  - id: D1
    description: "Un día laborable tiene 11 huecos que terminan dentro de cada tramo"
    requirement: "AGEN-02"
    verification:
      - kind: unit
        ref: "tests/test_schedule.py#test_a_working_day_has_11_slots_that_end_inside_each_shift"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fines de semana y festivos sin huecos"
    requirement: "AGEN-02"
    verification:
      - kind: unit
        ref: "tests/test_schedule.py#test_weekends_and_national_holidays_have_no_slots"
        status: pass
    human_judgment: false
  - id: D3
    description: "Reservar un hueco libre lo quita de la agenda"
    requirement: "RES-01"
    verification:
      - kind: integration
        ref: "tests/test_api.py#test_booking_a_free_slot_removes_it_from_the_agenda"
        status: pass
    human_judgment: false
  - id: D4
    description: "Doble reserva del mismo fisio rechazada (409 slot_taken)"
    requirement: "RES-02"
    verification:
      - kind: integration
        ref: "tests/test_api.py#test_same_therapist_cannot_be_double_booked"
        status: pass
    human_judgment: false
  - id: D5
    description: "Paciente con dos citas a la vez rechazado (409 patient_busy)"
    requirement: "RES-03"
    verification:
      - kind: integration
        ref: "tests/test_api.py#test_patient_cannot_have_two_appointments_at_once"
        status: pass
    human_judgment: false
  - id: D6
    description: "Antelación, cierre y hora fuera de hueco rechazados (422)"
    requirement: "RES-04"
    verification:
      - kind: integration
        ref: "tests/test_api.py#test_invalid_times_are_rejected_with_a_reason"
        status: pass
    human_judgment: false
  - id: D7
    description: "Mensajes de error comprensibles para recepción"
    verification: []
    human_judgment: true
    rationale: "Si el texto de 'detail' es claro para una recepcionista lo decide una persona"

duration: 9min
completed: 2026-10-06
status: complete
---

# Phase 1: Schedule and bookings — Plan 01 Summary

**Agenda y reservas de extremo a extremo: huecos de 45 min con horario partido y festivos, reservas en SQLite y rechazo de solapes por fisio y por paciente**

## Accomplishments

- Tracer: `GET /slots?therapist=ANA&day=2026-10-06` devuelve 11 huecos (09:00 … 19:00)
- `POST /appointments` → 201 con la cita; 409 `slot_taken` / `patient_busy`; 422 `too_late` / `closed` / `not_a_slot`
- `GET /appointments/{id}` para consultar una cita
- 13 tests en verde: 6 de reglas de agenda y 7 de API con `TestClient` y reloj fijo (2026-10-05 10:00)

## Commits

- `feat(01-01): GET /slots de extremo a extremo`
- `feat(01-01): reservar un hueco libre y verlo ocupado`
- `feat(01-01): validaciones de reserva (solapes, antelación, cierre)`

## Deviations from Plan

None — plan executed as written.

## Self-Check: PASSED
