---
status: complete
phase: 01-schedule-and-bookings
source: [01-01-SUMMARY.md]
started: 2026-10-06T11:50:00Z
updated: 2026-10-06T11:58:00Z
---

## Tests

### 1. Ver huecos de Luis el martes 13 de octubre
expected: `GET /slots?therapist=LUIS&day=2026-10-13` lista 11 huecos, de 09:00 a 19:00
result: pass

### 2. Reservar y ver el hueco ocupado
expected: tras reservar LUIS 2026-10-13T09:45, ese hueco ya no aparece en /slots
result: pass

### 3. Intentar reservar el 12 de octubre
expected: 422 con `"error": "closed"` y un `detail` que se entiende
result: pass

### 4. Reservar dos veces el mismo hueco
expected: la segunda reserva devuelve 409 `slot_taken`
result: pass

### 5. Mensajes de error comprensibles para recepción
expected: los `detail` se pueden leer en voz alta a un paciente sin traducir nada técnico
result: pass

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[]
