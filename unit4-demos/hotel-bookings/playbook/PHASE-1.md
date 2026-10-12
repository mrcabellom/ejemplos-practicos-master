# Fase 1 — Diagnóstico

**Objetivo:** reproducir la incidencia INC-0142 y que Claude Code localice
su causa. Se da por conocido el uso básico de la herramienta: el modo plan,
las instrucciones del proyecto y la gestión del contexto.

**Punto de partida:** el bloque común del [índice](README.md).

---

## Bloque 1 · Reproducir la incidencia

```powershell
python tasks.py occupancy
```

```
  MLG    2026-03-02    9/8      112%
```

Un hotel de 8 habitaciones con 9 ocupadas. No hace falta saber más del
negocio para empezar.

```powershell
python tasks.py reconcile
python tasks.py acceptance
python tasks.py test
```

| Orden | Resultado |
| --- | --- |
| `reconcile` | 11 filas y 8 reservas; `B-3002`, `B-3003` y `B-3008` están duplicadas. Termina con error |
| `acceptance` | Los 5 criterios en `FAIL` |
| `test` | 10 tests en verde, a pesar del defecto |

`acceptance` es el oráculo de la incidencia y se utiliza en todas las
fases.

---

## Bloque 2 · Localizar la causa en modo plan

```powershell
claude
```

```text
/plan Lee docs/tickets/INC-0142.md y python tasks.py acceptance. Explica por qué falla cada criterio y qué línea del código lo provoca. No propongas todavía el arreglo.
```

Resultado esperado: `load()`, en `src/pipeline/load.py`, inserta cada fila
sin comprobar si la reserva ya existe. Cada cambio en una reserva añade una
fila más, y sus habitaciones se cuentan varias veces.

Conviene abrir la línea que cita el agente y comprobar que dice lo que
afirma.

---

## Bloque 3 · Consultas que no ocupan contexto

En cualquier momento del análisis se puede hacer una consulta al margen:

```text
/btw ¿Qué diferencia hay entre reconcile y acceptance?
```

`/btw` responde sin añadir la pregunta a la conversación, como se puede
comprobar con `/context` antes y después.

```text
/recap
```

Resume en una línea el estado de la sesión, algo útil al retomarla.

---

## Bloque 4 · Explorar una alternativa

Antes de decidir el arreglo, se puede estudiar una alternativa sin alterar
la conversación principal:

```text
/branch alternativa-distinct
```

```text
¿Y si el informe de ocupación usara SELECT DISTINCT? ¿Qué criterios del oráculo pasarían y cuáles no?
```

Resultado esperado: no pasaría ninguno. El oráculo comprueba la tabla, no
el informe, y `DISTINCT` no elige qué versión de la reserva es la vigente.
Por eso `AGENTS.md` lo prohíbe.

`/resume` permite volver a la conversación original. La rama de
conversación se conserva, sin afectar a la principal.

---

## Cierre

| Herramienta | Para qué sirve |
| --- | --- |
| `/plan` | Analizar sin editar |
| `/btw` | Consultar sin consumir contexto |
| `/recap` | Recuperar el estado de la sesión |
| `/branch` y `/resume` | Explorar una idea sin perder el hilo |

Con la causa localizada, en la fase 2 Claude Code la corrige sin
intervención.

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| `reconcile` no muestra duplicados | Había un `warehouse.db` anterior: ejecutar `reset` y `run-all`. |
| El agente propone el arreglo | Se deja para la fase 2, donde se aborda con un objetivo comprobable. |
| `/branch` no está disponible | Actualizar Claude Code con `claude update`. |
| El agente cita una línea que no existe | Pedirle que abra el archivo y la compruebe. |
