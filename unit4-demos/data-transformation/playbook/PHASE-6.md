# Fase 6 — Vigilancia con `/loop`

**Objetivo:** que un agente vigile la bandeja y detecte la caída de
[OPS-106](../docs/tickets/OPS-106.md) por sí solo, mientras otro la corrige.

**Punto de partida:** `python tasks.py all` en verde (`Ran 13 tests`) y de
`week-1` a `week-5` en `inbox/`. Esta vez la entrega **no** se envía antes:
llega mientras se trabaja.

Tres terminales con el entorno activado:

| Terminal | Para qué |
| --- | --- |
| A | Claude, el vigilante |
| B | Claude, para corregir |
| C | El operador simulado |

---

## Bloque 1 · El vigilante

En **A**:

```text
/loop 1m
```

Sin prompt, `/loop` usa `.claude/loop.md`: ejecuta el pipeline e informa en
una línea, sin corregir nada. Empieza con `OK: ...`.

> `/loop` sirve para vigilar un rato, no como monitorización: no recupera
> triggers perdidos y caduca. Se para con `Esc` o pidiéndolo.

---

## Bloque 2 · Llega la entrega

En **C**:

```powershell
python tasks.py deliver 6
```

En el siguiente disparo, **A** dice `SE ROMPE: KeyError: 'user_type'`.
Compara con el punto 3 de `docs/plans/predictions.md`.

---

## Bloque 3 · Corregir

En **B**:

```text
Lee docs/tickets/OPS-106.md. Diagnostica la causa sin cambiar nada:
compara la cabecera de week-6.csv con la de week-5.csv usando profile_csv.
```

Esperado: `user_type` ahora se llama `rider_type`.

```text
Haz que la transformación acepte los dos nombres. Primero el test, después
el cambio mínimo. Termina con /check-delivery.
```

Esperado: `Ran 14 tests` y **Cumple**. En **A**, el siguiente disparo dice
`OK` y, como antes falló, el bucle se detiene.

---

## Bloque 4 · Revisión final

```text
Delega en data-reviewer una revisión completa de src/bikes/ contra el
contrato.
```

Esperado: **Sin objeciones**.

---

## Cierre

```text
Completa docs/tickets/OPS-106.md. Actualiza docs/plans/status.md con el
estado final y lo pendiente.
```

```powershell
git add docs src tests inbox
git commit -m "OPS-106: aceptar rider_type"
git log --oneline
```

El historial recoge las seis semanas, ticket a ticket.

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| El vigilante intenta corregir | `loop.md`: solo informa. |
| Renombra la columna en la entrega | El hook lo impide; se adapta la transformación. |
| El bucle no se detiene | Pídele que pare o pulsa `Esc` en A. |

Comandos: `/loop`, `/check-delivery`, `/agents`.

## Siguiente entrega

Para seguir practicando, crea `deliveries/week-7.csv` y `OPS-107.md` con una
sorpresa nueva (viajes que cruzan medianoche, bicis sin `bike_id`...) y
repite el ciclo.
