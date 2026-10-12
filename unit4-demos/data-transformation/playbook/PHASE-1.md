# Fase 1 — Entender sin escribir

**Objetivo:** responder a [OPS-101](../docs/tickets/OPS-101.md) sin cambiar
código, y saber deshacer lo que haga el agente.

**Punto de partida:** `main` limpio, sin entregas nuevas.

| Comprobación | Orden | Debe verse |
| --- | --- | --- |
| Entorno | `python tasks.py setup` | `Python 3.x OK` |
| Todo | `python tasks.py all` | `Ran 9 tests`, `OK: la salida cumple el contrato` |

---

## Bloque 1 · Explorar en modo plan

```powershell
claude
```

Pulsa `Shift+Tab` hasta ver **plan mode**: el agente puede leer, pero no
editar.

```text
Lee docs/tickets/OPS-101.md y responde a sus tres preguntas. Para cada
afirmación, cita archivo y línea. No modifiques nada.
```

Abre dos de las citas y comprueba que la línea dice lo que el agente
afirma. **Una afirmación sin cita no está comprobada.**

---

## Bloque 2 · Anticipar

La tercera pregunta del ticket (¿Qué pasa si el operador manda algo raro?)
merece concretarse:

```text
Sin ejecutar nada, ¿qué pasaría con la transformación y con la comprobación
si una entrega trajera...
1. un trip_id que ya llegó la semana anterior,
2. una estación que no está en el catálogo,
3. una columna con otro nombre?
Responde en una tabla, citando archivo y línea.
```

Sal de plan mode (`Shift+Tab`):

```text
Guarda esa tabla en docs/plans/predictions.md.
```

Las fases 3, 4 y 6 comprueban si acertó.

---

## Bloque 3 · Deshacer

```text
Añade al docstring de src/bikes/rules.py la línea "Revisado para OPS-101". No compruebes nada más.
```

En otro terminal, `git diff`. Vuelve a Claude, `/rewind`, elige el punto
anterior y restaura **código y conversación**. `git diff` ya no muestra
el cambio.

```text
Ejecuta python tasks.py reset.
```

`/rewind` otra vez: `Test-Path output` sigue en `False`. **`/rewind`
deshace las ediciones del agente, no lo que se ejecuta en el terminal.**

```powershell
python tasks.py pipeline
```

---

## Cierre

```text
Completa en docs/tickets/OPS-101.md las notas del equipo de datos (hechos
con archivo y línea) y una respuesta breve para Planificación.
```

```powershell
git add docs
git commit -m "OPS-101: cómo se calcula el uso diario"
```

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| Responde sin citar | Cita archivo y línea de cada afirmación. |
| Intenta leer `deliveries/` | Está denegado: las entregas futuras no se ven. |
| `/rewind` no ofrece restaurar código | El cambio tiene que haberlo hecho el agente. |

Comandos: `Shift+Tab`, `/rewind`.
