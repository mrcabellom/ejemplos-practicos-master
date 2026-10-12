# Fase 3 — Skill y subagente

**Objetivo:** resolver [OPS-103](../docs/tickets/OPS-103.md) con una
validación que se repite siempre igual (skill) y una decisión tomada en un
contexto aparte (subagente).

**Punto de partida:**

```powershell
python tasks.py deliver 3
```

Todavía **no** ejecutes el pipeline: lo hará el skill.

| | Skill | Subagente | Hook (fase 4) |
| --- | --- | --- | --- |
| Se activa | Al pedirlo o porque encaja | Al delegar | Solo, ante un evento |
| Contexto | El de la conversación | Uno propio | Ninguno |
| Sirve para | Un procedimiento que se repite | Una opinión especializada | Un control |

---

## Bloque 1 · El skill

En `.claude/skills/check-delivery/SKILL.md`: `name`, `description` (lo que
el agente lee para decidir si lo usa) y `allowed-tools` (lo que ejecuta sin
pedir permiso).

```text
/check-delivery
```

Esperado: **No cumple**, con `trip_id duplicado` para `T0103`, `T0104` y
`T0105`. No corrige nada. Compara con el punto 1 de
`docs/plans/predictions.md`.

`/clear` y, sin nombrar el skill:

```text
Ha llegado la entrega de la semana 3. ¿Se puede publicar el informe?
```

¿Lo ha elegido solo? Ejecutar los mismos comandos no es lo mismo que usarlo.

### Mejorarlo

Añade al procedimiento:

```markdown
6. Cuenta los rechazos de la última entrega por motivo (columna reason de
   output/rejected.csv).
```

Invócalo otra vez: el informe incluye los motivos.

---

## Bloque 2 · El subagente

```text
/context
```

```text
Lee docs/tickets/OPS-103.md y delega en data-reviewer: según el contrato,
¿dónde y cómo se deduplica por trip_id, qué viaje se conserva y si los
duplicados cuentan para el máximo del 10 %? Tráeme su propuesta. No
modifiques nada.
```

`Ctrl+O` o `/tasks` muestran su trabajo. Lee en **su** contexto; al tuyo
solo vuelve el informe. `/context` otra vez: `Messages` sube poco.

Esperado: deduplicar en `transform()` después de limpiar, conservar la
primera aparición, motivo `viaje duplicado`, y no cuenta para el 10 %
(`check.py` ya lo excluye).

---

## Bloque 3 · Aplicar

```text
Implementa la propuesta del revisor: primero un test que falle, después el
cambio mínimo en transform.py. Termina con /check-delivery.
```

Esperado: `Ran 11 tests`, **Cumple**, 3 rechazos `viaje duplicado`.

---

## Cierre

```text
Añade a docs/plans/status.md la decisión sobre duplicados y completa
docs/tickets/OPS-103.md: no hay que pedir nada al operador.
```

```powershell
git add .claude/skills docs src tests inbox
git commit -m "OPS-103: descartar viajes reenviados"
```

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| El skill corrige el código | Recuérdale «Lo que este skill no hace». |
| No elige el skill solo | Normal: la descripción ayuda, no obliga. |
| El subagente quiere ejecutar comandos | No tiene esas herramientas: mira `tools:`. |
| Conserva el último viaje | El contrato dice el primero. |

Comandos: `/check-delivery`, `/context`, `/tasks`, `/agents`.
