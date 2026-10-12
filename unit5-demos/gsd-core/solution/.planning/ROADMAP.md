# Roadmap: Kinesia · API de reservas

## Overview

Una agenda fiable para recepción: consultar huecos libres y reservar sin solapes. Es el valor principal
del proyecto y cabe en una sola fase.

## Phases

- [x] **Phase 1: Schedule and bookings** - Huecos libres y reservas sin solapes

## Phase Details

### Phase 1: Schedule and bookings
**Goal**: Recepción consulta huecos y reserva citas sin que nunca haya dos pacientes en el mismo hueco
**Depends on**: Nothing (first phase)
**Requirements**: AGEN-01, AGEN-02, RES-01, RES-02, RES-03, RES-04
**Success Criteria** (what must be TRUE):
  1. `GET /slots` devuelve solo huecos libres, dentro del horario y nunca en festivo o fin de semana
  2. Reservar un hueco ya ocupado devuelve un error y no crea la cita
  3. Una reserva con menos de 2 h de antelación se rechaza con un motivo claro
**Plans**: 1 plan

Plans:
- [x] 01-01: Agenda (`GET /slots`) y reservas (`POST /appointments`) con persistencia y validaciones

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Schedule and bookings | 1/1 | Complete | 2026-10-06 |
