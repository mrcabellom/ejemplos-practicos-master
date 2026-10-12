# Fase 2 — Instrucciones y contexto

**Objetivo:** resolver [OPS-102](../docs/tickets/OPS-102.md) comprobando de
paso qué lee el agente al arrancar, qué recuerda y qué olvida.

**Punto de partida:**

```powershell
python tasks.py deliver 2
python tasks.py pipeline
```

Debe verse: `week-2.csv: 42% rechazado (5 de 12); máximo 10%`.

---

## Bloque 1 · Qué lee el agente al arrancar

```text
/memory
```

Aparecen `CLAUDE.md` y `AGENTS.md`: `CLAUDE.md` empieza por `@AGENTS.md`,
una **importación** que se carga sin que el agente tenga que decidir leerla.

`.claude/rules/transform.md` aún no aparece: tiene `paths: src/bikes/**` y
solo se carga al trabajar con esos archivos. Lo verás en el bloque 2.

---

## Bloque 2 · El contexto, paso a paso

Anota cada medición:

| Momento | Uso total | `Messages` |
| --- | --- | --- |
| A. Inicio | | |
| B. Tras investigar | | |
| C. Tras `/compact` | | |
| D. Tras `/clear` | | |

### Paso 1 · Medir (A)

```text
/context
```

### Paso 2 · Investigar (B)

```text
Lee docs/tickets/OPS-102.md, output/rejected.csv, inbox/week-2.csv y
src/bikes/rules.py. ¿Por qué se bloquea el informe? No modifiques nada.
```

Esperado: 5 viajes llegan como `15/10/2026 08:40` y `parse_time` solo
acepta ISO. `/context` sube, y `/memory` ya muestra `transform.md`.

### Paso 3 · Una decisión y un aviso

Planificación llama mientras investigas:

```text
Toma nota de dos cosas, sin cambiar código:
1. Decisión: aceptamos también fechas dd/mm/aaaa HH:MM; el operador no va
   a cambiar su sistema.
2. Aviso de Planificación: desde la semana 4, la estación Sol se llamará
   Puerta del Sol.
```

```text
Crea docs/plans/status.md a partir de docs/plans/STATUS-TEMPLATE.md con el
objetivo (cerrar OPS-102), la decisión 1, la evidencia y el siguiente paso
(test y cambio en parse_time). NO incluyas el aviso 2.
```

Comprueba que el aviso 2 no está en el archivo.

### Paso 4 · Compactar (C)

```text
/compact Conserva el objetivo y las decisiones.
```

`/context`: `Messages` baja mucho. Pregunta:

```text
¿Qué dos cosas te pedí que anotaras? No leas archivos.
```

Probablemente recuerda las dos: estaban en el resumen. Pero el resumen lo
escribe el agente y puede dejarse detalles.

### Paso 5 · Limpiar (D)

```text
/clear
```

`/context` y la misma pregunta. Esperado: no lo sabe.

```text
Lee docs/plans/status.md. ¿En qué estábamos y cuál es el siguiente paso?
```

Recupera la decisión 1. **El aviso 2 se ha perdido**: solo estaba en la
conversación.

### Paso 6 · Retomar desde el estado

```text
Haz el siguiente paso de docs/plans/status.md: primero un test que falle,
después el cambio mínimo, después python tasks.py all.
```

Esperado: `Ran 10 tests`, `OK: la salida cumple el contrato`.

| Comando | Qué hace | Qué se pierde |
| --- | --- | --- |
| `/compact` | Resume la conversación | Lo que el resumen omita |
| `/clear` | Empieza de cero | Todo lo que no esté en un archivo |
| Autocompactación | `/compact` automático cerca del límite | Igual que `/compact` |

---

## Cierre

Añade tú el aviso 2 en «Pendiente» de `docs/plans/status.md`: **hará falta
en la fase 4.**

```text
Completa las notas y la respuesta de docs/tickets/OPS-102.md.
```

```powershell
git add docs src tests inbox
git commit -m "OPS-102: aceptar fechas dd/mm/aaaa"
```

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| Escribe el aviso en el estado | Bórralo: el paso 5 necesita un dato sin escribir. |
| Tras `/clear` «recuerda» el aviso | Pregúntale de dónde lo saca. |
| Cambia el código antes del test | `/rewind` y empieza por el test. |

Comandos: `/memory`, `/context`, `/compact`, `/clear`.
