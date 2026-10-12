# Kinesia · API de reservas

## What This Is

API REST para que la recepción de Kinesia, una clínica de fisioterapia de Madrid con dos fisios,
consulte huecos libres y reserve citas. Sustituye a la hoja de cálculo compartida.

## Core Value

**Nunca dos pacientes en el mismo hueco.** Si todo lo demás falla, la agenda tiene que ser fiable.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Recepción ve los huecos libres de cada fisio para un día
- [ ] Recepción reserva citas sin solapes y respetando horario, festivos y antelación mínima

### Out of Scope

- Cancelaciones — se siguen gestionando por teléfono (brief); candidatas a v2
- Recordatorios por SMS — no lo necesitan ahora (brief)
- Pagos online — se cobra en la clínica
- Reserva directa por pacientes — será otro milestone, con la web
- Autenticación — la API solo es accesible desde la red de la clínica (revisar en v2)

## Context

- Hoy usan una hoja de cálculo: hay dobles reservas, citas con 5 minutos de antelación y citas en festivo.
- Fisios: Ana (`ANA`) y Luis (`LUIS`). Sesiones de 45 min. L-V de 9 a 14 y de 16 a 20.
- Brief completo: `docs/brief.md`.

## Constraints

- **Tech stack**: Python 3.12 (`.python-version`), FastAPI, SQLite (stdlib), pytest, uv — equipo pequeño, sin infraestructura
- **Estructura**: paquete `src/kinesia/`, aplicación en `kinesia.main:app`, tests en `tests/`
- **Idioma**: código e identificadores en inglés; los textos `detail` de los errores, en español (los lee recepción)
- **Zona horaria**: una sola sede en Madrid; todas las horas son locales
- **Tests**: cada regla de negocio tiene un test con fechas concretas y un "ahora" fijo

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Horas locales sin zona horaria | Una sola clínica en Madrid; evita conversiones | — Pending |
| SQLite en un fichero | Cero infraestructura; suficiente para 2 fisios | — Pending |

---
*Last updated: 2026-10-06 after initialization*
