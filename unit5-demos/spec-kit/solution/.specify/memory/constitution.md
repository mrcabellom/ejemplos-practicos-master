<!--
Sync Impact Report
- Version change: (template) → 1.0.0
- Added principles: I. Idempotent Pipelines, II. Exact Money, III. No Silent Drops,
  IV. Tests With Concrete Figures, V. Keep It Small
- Added sections: Technology Constraints, Development Workflow
- Templates requiring updates: none (plan-template Constitution Check reads this file)
-->

# La Despensa Data Constitution

## Core Principles

### I. Idempotent Pipelines (NON-NEGOTIABLE)

Ejecutar un pipeline dos veces con la misma entrada MUST producir exactamente las mismas tablas.
Las cargas reconstruyen o hacen MERGE por clave; nunca se hace `INSERT` a ciegas sobre datos ya cargados.

**Rationale**: los reprocesados son rutina (fallos, datos tardíos); duplicar ventas no lo es.

### II. Exact Money

Los importes MUST almacenarse como `DECIMAL` con 2 decimales. Está prohibido usar `FLOAT`/`DOUBLE`
para dinero. Cualquier redondeo MUST estar especificado (regla y momento en que se aplica).

**Rationale**: Finanzas cuadra al céntimo; los flotantes no.

### III. No Silent Drops

Toda fila de entrada que no llegue a la tabla final MUST quedar registrada con un motivo
(`reject_reason`). Debe cumplirse siempre: `filas leídas = filas válidas + filas rechazadas`.

**Rationale**: "faltan ventas" es la incidencia más cara de investigar si no hay rastro.

### IV. Tests With Concrete Figures

Cada escenario de aceptación MUST tener un test automático con un fixture pequeño (< 50 filas)
y cifras esperadas concretas (p. ej. `gross_revenue = 7.95`), no solo "no está vacío".

**Rationale**: las cifras concretas son lo que impide que una IA o una persona cambie la semántica
de una métrica sin darse cuenta.

### V. Keep It Small

Se usa la herramienta más simple que resuelva el problema: SQL sobre DuckDB antes que frameworks
de orquestación; un módulo antes que varios. Toda complejidad extra MUST justificarse en el plan.

## Technology Constraints

- Python 3.12 (fijado en `.python-version`), gestionado con `uv`.
- DuckDB como motor local; SQL legible como forma principal de transformar.
- `pytest` para tests.
- Las tablas publicadas tienen un contrato documentado (columnas, tipos, clave, nulos) en
  `specs/<feature>/contracts/`.

## Development Workflow

- Ningún cambio de tabla publicada sin spec: `/speckit-specify` → `/speckit-clarify` → `/speckit-plan`
  → `/speckit-tasks` → `/speckit-implement`.
- Las preguntas de negocio (zona horaria, qué cuenta como venta, redondeos) se resuelven en
  `/speckit-clarify`, no dentro del código.

## Governance

Esta constitución prevalece sobre cualquier otra práctica del repositorio. El "Constitution Check"
de cada `plan.md` MUST verificar los principios I–V. Las enmiendas se hacen con `/speckit-constitution`,
subiendo versión (MAJOR: se elimina o redefine un principio; MINOR: se añade; PATCH: redacción).

**Version**: 1.0.0 | **Ratified**: 2026-10-06 | **Last Amended**: 2026-10-06
