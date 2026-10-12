# Fase 3 — Sesiones en paralelo

**Objetivo:** repartir los tickets pendientes entre varias sesiones de
Claude Code que trabajan a la vez, cada una en su propio worktree,
supervisarlas desde una sola vista e integrar el resultado.

**Punto de partida:** el bloque común del [índice](README.md).

---

## Bloque 0 · Los tickets pendientes

| Ticket | Qué pide | Archivos |
| --- | --- | --- |
| [BRI-201](../docs/tickets/BRI-201.md) | Informe de ocupación en JSON | `occupancy.py` y un test nuevo |
| [BRI-202](../docs/tickets/BRI-202.md) | Herramienta MCP `quarantine_rows` | `mcp_server/server.py` |
| [BRI-203](../docs/tickets/BRI-203.md) | Comprobación de capacidad en `reconcile` | `reconcile.py` |
| [BRI-204](../docs/tickets/BRI-204.md) | Validación del canal de venta | `contract.py`, su test y el contrato |

Antes de empezar, la pregunta clave: **¿pueden resolverse a la vez?** La
respuesta está en la columna de archivos. Si dos tickets modificaran el
mismo archivo, entrarían en conflicto al integrarlos.

---

## Bloque 1 · Cuatro sesiones en segundo plano

Desde el terminal, con el entorno de Python activado:

```powershell
claude --bg --name bri-201 "Resuelve docs/tickets/BRI-201.md cumpliendo sus criterios de aceptación. Toca solo los archivos que indica. Cuando python tasks.py test pase, haz commit."
claude --bg --name bri-202 "Resuelve docs/tickets/BRI-202.md cumpliendo sus criterios de aceptación. Toca solo los archivos que indica. Cuando python tasks.py test pase, haz commit."
claude --bg --name bri-203 "Resuelve docs/tickets/BRI-203.md cumpliendo sus criterios de aceptación. Toca solo los archivos que indica. Cuando python tasks.py test pase, haz commit."
claude --bg --name bri-204 "Resuelve docs/tickets/BRI-204.md cumpliendo sus criterios de aceptación. Toca solo los archivos que indica. Cuando python tasks.py test pase, haz commit."
```

Cada sesión crea su worktree en `.claude/worktrees/<nombre>` y trabaja en
una rama `worktree-<nombre>`; en este caso, de `worktree-bri-201` a
`worktree-bri-204`. La carpeta de trabajo principal no cambia:

```powershell
git status
git worktree list
```

`git worktree list` muestra la carpeta principal y cuatro worktrees
marcados como `locked`, que permanecen bloqueados mientras exista su
sesión.

> **Los worktrees parten de `main`, no de la rama actual.** Aunque las
> sesiones se lancen desde otra rama, cada worktree contiene únicamente lo
> que hay en `main`.

> Cuatro sesiones simultáneas consumen tanta cuota como cuatro sesiones
> independientes. Con un plan ajustado, es preferible lanzarlas de dos en
> dos.

---

## Bloque 2 · Supervisión

```powershell
claude agents
```

| Tecla | Acción |
| --- | --- |
| `Espacio` | Vista previa: qué hace la sesión o qué pregunta, sin abrirla |
| `Enter` | Abrir la sesión completa |
| Escribir en el panel y pulsar `Enter` | Responder a una sesión en espera |
| `Ctrl+X` | Detener una sesión |
| `Esc` | Salir; las sesiones siguen trabajando |

Alguna sesión puede quedar en **Needs input** porque solicita permiso para
algo que no está en `allow`. La vista previa muestra qué pide. **Cada
permiso sigue dependiendo de una persona**, aunque haya cuatro agentes
solicitándolos a la vez.

También desde el terminal:

```powershell
claude logs bri-203
claude attach bri-203
```

Comportamiento de referencia:

- Cada sesión resuelve su ticket en menos de un minuto, ejecuta los tests y
  hace **su propio commit** en su rama.
- La sesión de BRI-203 solicita autorización para `run-all`, porque
  necesita un almacén para comprobar su criterio. La carga se hace en el
  `warehouse.db` de **su** worktree; el de la carpeta principal no se
  modifica.
- Ninguna sesión sube su rama al remoto; al terminar, se ofrecen a hacerlo.

---

## Bloque 3 · Comprobación e integración

Cuando las cuatro sesiones están en **Completed**, cada rama se comprueba
**antes** de integrarla.

### Paso 1 · Commits propios

```powershell
git branch --list "worktree-bri-*"
git log --oneline main..worktree-bri-201
```

La segunda orden lista los commits que la rama tiene por encima de `main`.
Debe aparecer al menos uno. Si no aparece ninguno, la sesión no llegó a
hacer commit; `claude attach bri-201` permite preguntarle por qué.

### Paso 2 · Archivos modificados

```powershell
git diff --stat main...worktree-bri-201
git diff --stat main...worktree-bri-202
git diff --stat main...worktree-bri-203
git diff --stat main...worktree-bri-204
```

Cada lista debe coincidir con la columna de archivos del bloque 0, y
ningún archivo debe aparecer en dos ramas. Una rama que modifica archivos
ajenos a su ticket no se integra hasta haberla revisado.

### Paso 3 · Tests

Cada worktree es una carpeta normal. Con el entorno activado:

```powershell
cd .claude\worktrees\bri-201
python tasks.py test
cd ..\..\..
```

Se repite con los otros tres. Resultado de referencia: 12, 10, 10 y 13
tests, todos en verde; el número depende de cuántos tests escriba cada
sesión. En `bri-202`, además, `python tasks.py mcp-check` debe incluir
`quarantine_rows`.

### Paso 4 · Integración

La integración se hace desde la **carpeta principal** del repositorio, no
desde un worktree. Después del paso 3, `git worktree list` confirma en qué
carpeta se está.

```powershell
git switch main
git switch -c backlog/bri
git merge --no-edit worktree-bri-201
git merge --no-edit worktree-bri-202
git merge --no-edit worktree-bri-203
git merge --no-edit worktree-bri-204
python tasks.py test
```

Resultado esperado: **ningún conflicto y todos los tests en verde** (15 en
la ejecución de referencia). Con el almacén del bloque común, el efecto de
BRI-203 ya es visible:

```powershell
python tasks.py reconcile
```

```
  WARNING: 1 nights exceed the hotel capacity
    MLG 2026-03-02 9/8
```

### Paso 5 · Limpieza

Una vez integradas las ramas, los worktrees ya no son necesarios. En
`claude agents`, cada sesión se borra pulsando `Ctrl+X` dos veces
seguidas, lo que elimina también su worktree. Después:

```powershell
git worktree list
git branch -d worktree-bri-201 worktree-bri-202 worktree-bri-203 worktree-bri-204
```

`git worktree list` debe mostrar solo la carpeta principal. La opción `-d`
solo borra ramas ya integradas en la rama actual: si rechaza alguna, es
que no se integró.

---

## Bloque 4 · Paralelismo dentro de una sesión: `/fork` y `/subtask`

El trabajo en paralelo también puede iniciarse desde una sesión abierta:

| Orden | Qué crea | Adónde vuelve el resultado |
| --- | --- | --- |
| `/subtask <tarea>` | Un subagente que hereda la conversación | A la conversación actual, al terminar |
| `/fork <tarea>` | Una sesión nueva en segundo plano con una copia de la conversación | Se queda en `claude agents` |

```text
/subtask Lee los cuatro diffs de backlog/bri y dime si alguno contradice docs/data-contracts/fct_bookings.md.
```

Mientras tanto, la conversación principal puede continuar; la respuesta
llega cuando el subagente termina.

---

## Opcional · `/batch`

`/batch` hace todo lo anterior en un solo paso: estudia el repositorio,
divide el trabajo en unidades independientes, presenta un plan y, una vez
aprobado, lanza un agente por unidad, cada uno en su propio worktree.

```text
/batch resuelve los tickets BRI-201 a BRI-204 de docs/tickets
```

Su plan puede compararse con el reparto manual del bloque 0.

---

## Cierre

| Pregunta | Respuesta |
| --- | --- |
| ¿Por qué no hay conflictos? | Cada sesión escribe en su propio worktree |
| ¿Qué determina si se puede trabajar en paralelo? | Que los tickets no modifiquen los mismos archivos, no la herramienta |
| ¿Quién aprueba los permisos? | Una persona, sesión por sesión, desde `claude agents` |
| ¿Quién integra? | Una persona, rama por rama, después de revisar el diff |

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| La integración se hizo dentro de un worktree y no es posible cambiar a `backlog/bri` | Git no permite tener la misma rama en dos carpetas. En ese worktree, volver a su rama con `git switch worktree-bri-201` (la que corresponda). Lo integrado se conserva. |
| No está claro si un worktree contiene los cambios correctos | Pasos 1 a 3 del bloque 3: commits sobre `main`, archivos modificados y tests. |
| En el worktree falta algo que sí está en la rama actual | El worktree parte de `main`. Ese cambio debe integrarse antes en `main`. |
| `git worktree remove` falla porque está `locked` | Su sesión sigue existiendo. Hay que borrarla desde `claude agents`. |
| Windows devuelve `Permission denied` al borrar un worktree | OneDrive u otro programa tiene la carpeta abierta. Cerrar la sesión, ejecutar `git worktree prune` y borrar la carpeta manualmente. |
| Una sesión no puede ejecutar los tests | Se lanzó sin el entorno activado y `python` no es el del proyecto. Detenerla, activar el entorno y volver a lanzarla. |
| `--bg` falla por la confianza de la carpeta | Abrir `claude` una vez en el repositorio y aceptar el diálogo. |
| Dos ramas entran en conflicto al integrarlas | Una sesión modificó un archivo ajeno a su ticket. Revisar el diff y conservar solo la parte del ticket. |
| Una sesión queda en **Needs input** | Es lo esperado: está solicitando un permiso. `Espacio` muestra cuál. |
| No hay remoto y la sesión indica que no puede subir la rama | El trabajo queda en la rama local y se integra igual. |
