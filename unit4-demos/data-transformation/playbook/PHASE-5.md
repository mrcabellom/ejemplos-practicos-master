# Fase 5 — MCP y especificación

**Objetivo:** resolver [OPS-105](../docs/tickets/OPS-105.md) entendiendo una
entrega grande sin llenar el contexto, y acordar el plan antes de tocar
código.

**Punto de partida:**

```powershell
python tasks.py deliver 5
python tasks.py pipeline
python tasks.py mcp-check
```

Debe verse `duración fuera de rango (1-240 min): 30 viajes`, y en el
`mcp-check`, `initialize OK` y `tools/list OK`.

---

## Bloque 1 · ¿Hace falta un MCP?

Antes de conectar nada: **¿esto no lo hace ya el agente?** Leer, buscar y usar
git, sí; un servidor para eso solo añade permisos.

`bike-data` (`mcp_server/server.py`) aporta algo concreto: `profile_csv` y
`duration_stats` devuelven **un resumen** sin pasar las filas.

```text
/mcp
```

`bike-data` conectado, con sus dos herramientas.

---

## Bloque 2 · Archivo frente a resumen

Dos conversaciones limpias, la misma pregunta:

| Forma | `Messages` antes | `Messages` después |
| --- | --- | --- |
| Leyendo el archivo | | |
| Con MCP | | |

```text
/clear
```

`/context`, y:

```text
Lee inbox/week-5.csv y dime la duración mínima, mediana y máxima, y cuántos
viajes superan 240 minutos. No uses MCP.
```

`/context`. Después:

```text
/clear
```

`/context`, y:

```text
Usa duration_stats sobre inbox/week-5.csv y dime la duración mínima, mediana y máxima, y cuántos
viajes superan 240 minutos.
```

`/context`. Esperado: 30 viajes por encima de 240 y un máximo de 3858
minutos. Comprobar la diferencia de `Messages`.

---

## Bloque 3 · Especificar antes de corregir

Plan mode (`Shift+Tab`):

```text
Lee docs/tickets/OPS-105.md, docs/plans/status.md y el contrato. Propón cómo
tratar los viajes de más de 240 minutos: qué regla cambia, qué motivo, qué
test y qué cifras esperas después. No edites nada.
```

Esperado: rechazar en `duration_minutes` con un motivo como
`duración excesiva`, un test, y después 3.010 válidos y **OK** (los 30
rechazos son el 1 % de la entrega).

Si el plan es correcto, apruébalo y deja que lo ejecute. Termina con:

```text
/check-delivery
```

---

## Cierre

```text
Completa docs/tickets/OPS-105.md con cuántos viajes estaban afectados y qué
se hizo con ellos. Actualiza docs/plans/status.md.
```

```powershell
git add docs src tests inbox
git commit -m "OPS-105: rechazar duraciones de más de 240 minutos"
```

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| `/mcp` muestra el servidor caído | `python tasks.py mcp-check`; abre `claude` con el entorno activado. |
| Escribe un script para calcularlo | También vale: mide su contexto igual. |
| Propone recortar la duración a 240 | `.claude/rules/transform.md`: se rechaza, no se inventa. |

Comandos: `/mcp`, `/context`, `Shift+Tab`.
