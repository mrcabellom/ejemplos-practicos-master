# Phase 1: Schedule and bookings - Context

**Gathered:** 2026-10-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Recepción consulta los huecos libres de un fisio para un día y reserva citas sin solapes.
Las cancelaciones, la autenticación y la web de pacientes quedan fuera de este milestone.

</domain>

<decisions>
## Implementation Decisions

### Huecos y horario
- **D-01:** Sesiones de 45 min encadenadas desde la apertura de cada tramo (9:00 y 16:00). La sesión
  debe **terminar** dentro del tramo: los últimos huecos son 12:45 y 19:00 (11 huecos por día).
  No se ofrece 13:30 (acabaría a las 14:15) ni 19:45.
- **D-02:** Solo se reserva en el inicio de un hueco. `10:10` → 422 `not_a_slot`.
- **D-06:** Cerrado sábados, domingos y festivos nacionales entre semana (lista fija:
  2026-10-12, 2026-12-08, 2026-12-25, 2027-01-01, 2027-01-06). Día cerrado → `GET /slots` vacío;
  reservar → 422 `closed`.

### Solapes
- **D-03:** Un fisio no puede tener dos citas que empiecen a menos de 45 min → 409 `slot_taken`.
- **D-04:** Un paciente (identificado por teléfono) no puede tener dos citas solapadas, aunque sean
  con fisios distintos → 409 `patient_busy`.

### Antelación
- **D-05:** Mínimo 2 h entre "ahora" y el inicio de la cita (justo 2 h sí vale). El pasado también
  es `too_late` → 422.
- **D-09:** "Ahora" se inyecta en la aplicación (`clock`) para que los tests usen una fecha fija.

### API y datos
- **D-07:** SQLite en un fichero (`kinesia.db`), módulo `sqlite3` de la librería estándar. Tests con
  una base de datos temporal por test.
- **D-08:** Todos los errores con el mismo cuerpo: `{"error": "<código>", "detail": "<texto>"}`. El código
  va en inglés (`slot_taken`) y el `detail`, en español, porque lo lee recepción.
- Horas en local de Madrid, sin zona horaria (`2026-10-06T09:00`).

### Claude's Discretion
- Estructura de módulos y nombres de funciones.
- Validación de nombre y teléfono (mínimos razonables).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `docs/brief.md` — Petición original de la gerente: fisios, horario, antelación y fuera de alcance

</canonical_refs>

<code_context>
## Existing Code Insights

Proyecto vacío: solo `pyproject.toml` y `uv.lock` (fastapi, uvicorn, pytest, httpx), `.python-version` y `docs/brief.md`.

</code_context>

<specifics>
## Specific Ideas

- Fechas de prueba: "ahora" = lunes 2026-10-05 10:00. Martes 2026-10-06 es laborable;
  sábado 2026-10-10 y lunes 2026-10-12 (Fiesta Nacional) están cerrados.

</specifics>

<deferred>
## Deferred Ideas

- Festivos configurables (fichero o tabla) en vez de una lista en código — revisar antes de 2027
- Festivos locales de Madrid (2 de mayo, San Isidro) — Marta lo confirmará

</deferred>

---

*Phase: 01-schedule-and-bookings*
*Context gathered: 2026-10-06*
