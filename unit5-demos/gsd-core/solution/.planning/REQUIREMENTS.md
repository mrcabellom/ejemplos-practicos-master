# Requirements: Kinesia · API de reservas

**Defined:** 2026-10-06
**Core Value:** Nunca dos pacientes en el mismo hueco.

## v1 Requirements

### Agenda

- [x] **AGEN-01**: Recepción puede consultar los huecos libres de un fisio para un día
- [x] **AGEN-02**: Los huecos respetan sesiones de 45 min, el horario partido y los días de cierre (fines de semana y festivos nacionales)

### Reservas

- [x] **RES-01**: Recepción puede reservar una cita para un paciente (nombre y teléfono) en un hueco libre
- [x] **RES-02**: Un fisio nunca tiene dos citas que se solapen
- [x] **RES-03**: Un paciente no puede tener dos citas a la misma hora (con fisios distintos)
- [x] **RES-04**: No se puede reservar en el pasado ni con menos de 2 horas de antelación

## v2 Requirements

- **CAN-01**: Recepción puede cancelar una cita y el hueco vuelve a quedar libre
- **NOTI-01**: Recordatorio por SMS 24 h antes de la cita
- **WEB-01**: Los pacientes reservan desde la web

## Out of Scope

| Feature | Reason |
|---------|--------|
| Pagos online | Se cobra en la clínica |
| Varias sedes | Solo hay una clínica |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AGEN-01 | Phase 1 | Complete |
| AGEN-02 | Phase 1 | Complete |
| RES-01 | Phase 1 | Complete |
| RES-02 | Phase 1 | Complete |
| RES-03 | Phase 1 | Complete |
| RES-04 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 6 total
- Mapped to phases: 6
- Unmapped: 0 ✓

---
*Requirements defined: 2026-10-06*
*Last updated: 2026-10-06 after Phase 1 execution*
