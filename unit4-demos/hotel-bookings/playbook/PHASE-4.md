# Fase 4 — Configuración generada por Claude

**Objetivo:** que Claude Code escriba parte de su propia configuración
(permisos, un skill, un hook y la línea de estado) y revisarla antes de
incorporarla al repositorio.

**Punto de partida:** el bloque común del [índice](README.md).

---

## Bloque 0 · Dónde se guarda cada elemento

| Archivo | Alcance | Se versiona |
| --- | --- | --- |
| `.claude/settings.json` | Todo el equipo | Sí |
| `.claude/settings.local.json` | Una persona, en este repositorio | No |
| `.claude/skills/<nombre>/SKILL.md` | Todo el equipo | Sí |
| `~/.claude/skills/<nombre>/SKILL.md` | Una persona, en todos sus proyectos | No |

Criterio de la fase: **la configuración que genera Claude se revisa igual
que el código escrito por otra persona.** El trabajo se hace en una rama:

```powershell
git switch -c config/claude-self
```

---

## Bloque 1 · Permisos a partir del uso

```text
/fewer-permission-prompts
```

Claude revisa las sesiones anteriores en el repositorio, identifica las
órdenes de solo lectura que se han aprobado manualmente con más frecuencia
y propone añadirlas a `allow` en `.claude/settings.json`.

El diff se revisa línea a línea:

- ¿Alguna regla permite escribir en el almacén? `run`, `run-all` y `reset`
  deben seguir en `ask`.
- ¿Alguna regla es demasiado amplia, como `Bash(python *)`? Permitiría
  ejecutar cualquier script.
- ¿Alguna contradice un `deny`? El `deny` prevalece, pero la regla sobra.

Lo que no esté justificado se elimina antes de aceptar el cambio.

---

## Bloque 2 · Un skill escrito por Claude

Cerrar un ticket sigue siempre el mismo procedimiento: ejecutar los tests,
revisar el diff, comprobar los criterios y dejar constancia del resultado
en el ticket. Es un buen candidato para un skill:

```text
Crea el skill .claude/skills/close-ticket/SKILL.md. Recibe un identificador de ticket como argumento. Debe leer docs/tickets/<ticket>.md, ejecutar python tasks.py test, mostrar git diff --stat y comprobar uno a uno los criterios de aceptación del ticket. python tasks.py acceptance es el oráculo de INC-0142: ejecútalo y cuéntalo solo para ese ticket. Si todos los criterios se cumplen, añade al final del ticket una sección "Cierre" con los comandos ejecutados y su resultado. Si alguno no se cumple, no escribe nada en el ticket: informa de qué criterio falla y por qué. Que solo se invoque a mano, que no haga commit y que no lance cargas ni reprocesos.
```

En el `SKILL.md` generado se comprueba lo siguiente:

| Campo | Para qué sirve |
| --- | --- |
| `disable-model-invocation: true` | Solo se lanza con `/close-ticket`, nunca por iniciativa del agente |
| `arguments` y `$ticket` (o `$ARGUMENTS`) | Recibir el identificador del ticket |
| `allowed-tools` | Ejecutar tests, oráculo y diff, y editar el ticket, sin pedir permiso; nada más |
| `` !`git diff --stat` `` | Incluir el diff al invocarlo, sin consumir un turno |

### Paso 1 · Un ticket sin resolver

En esta rama, BRI-204 sigue abierto: `unknown_channel` no está
implementado.

```text
/close-ticket BRI-204
```

Resultado esperado: **el skill no lo cierra** e indica qué criterio falla.
Es el comportamiento correcto: un ticket se cierra porque sus criterios se
cumplen, no porque alguien lo solicite. `git status` confirma que el
ticket no se ha modificado.

### Paso 2 · El mismo ticket, resuelto

El ticket se resuelve en una rama aparte, para no mezclarlo con la
configuración:

```powershell
git switch -c try/bri-204
claude -p "Resuelve docs/tickets/BRI-204.md cumpliendo sus criterios de aceptación. Toca solo los archivos que indica." --permission-mode acceptEdits
git add src tests docs/data-contracts
git commit -m "BRI-204"
```

Los archivos del skill, todavía sin commit, se mantienen al cambiar de
rama. En la sesión de Claude:

```text
/close-ticket BRI-204
```

Resultado esperado: el skill añade la sección "Cierre" al ticket. El
oráculo sigue fallando, porque INC-0142 continúa abierta, pero no cuenta
para BRI-204. Si el skill se niega a cerrar por culpa del oráculo, el
prompt no lo dejó claro y hay que corregirlo.

Una vez revisada la sección, se deshace la prueba:

```powershell
git restore docs/tickets/BRI-204.md
git switch config/claude-self
git branch -D try/bri-204
```

---

## Bloque 3 · Un hook escrito por Claude

```text
Crea un hook PostToolUse en .claude/settings.local.json que, cuando edites un archivo de src/pipeline/, ejecute python tasks.py test y, si falla, devuelva código 2 con el final de la salida en stderr. Escribe el script en .claude/hooks/run_tests_after_edit.py, en Python y sin dependencias.
```

Antes de aceptarlo, conviene comprobar si el script filtra por ruta o si
lanzará los tests después de cualquier edición. Después:

```text
/hooks
```

El hook debe aparecer en `PostToolUse`. Para probarlo, basta con un cambio
que rompa un test:

```text
En src/pipeline/contract.py cambia SUPPORTED_CURRENCY a "USD".
```

Resultado esperado: el hook devuelve el fallo a Claude justo después de la
edición, sin que nadie haya lanzado los tests. A continuación se pide
revertir el cambio.

A diferencia del hook `Stop` de la fase 2, que comprueba **antes de
terminar el turno**, este comprueba **después de cada edición**.

---

## Bloque 4 · La línea de estado

```text
/statusline muestra la rama de git, el modelo y el porcentaje de contexto usado. Escríbelo como script de Python, solo con la biblioteca estándar: en Windows no hay jq.
```

Sin la última frase, Claude suele generar un comando de bash que usa `jq`
para leer el JSON de la sesión. En macOS y Linux funciona si `jq` está
instalado; en Windows, la línea de estado aparece vacía o con errores.

El script se ejecuta con el `python` del terminal desde el que se abrió
`claude`; con el entorno activado, es el del proyecto.

Conviene comprobar dónde se ha guardado: la línea de estado es una
preferencia personal, no del equipo.

---

## Bloque 5 · Auditoría y decisión

```text
/doctor prompt-audit
```

Revisa `CLAUDE.md`, `AGENTS.md`, las reglas, los skills y los subagentes
en busca de instrucciones contradictorias o que nada respalda. Su informe
se contrasta con lo generado en esta fase.

Qué se incorpora y dónde:

| Elemento | Destino |
| --- | --- |
| Permisos nuevos | Los ya revisados, al `settings.json` del equipo |
| `close-ticket` | Equipo: es el procedimiento de cierre común |
| Hook de tests tras editar | Personal mientras se prueba; después, decisión del equipo |
| Línea de estado | Personal |

```powershell
git add .claude/settings.json .claude/skills/close-ticket
git commit -m "Add close-ticket skill and reviewed permission allowlist"
```

---

## Cierre

Claude Code puede escribir su propia configuración, pero no decide qué
entra en la del equipo. La configuración es código: pasa por diff,
revisión y commit, como cualquier otro cambio.

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| La línea de estado no aparece o muestra errores | El script usa `jq`, que no viene instalado en Windows. Pedir que lo reescriba en Python con la biblioteca estándar. |
| `/close-ticket` se niega a cerrar | El ticket no está resuelto en esta rama. Es el comportamiento correcto: paso 1 del bloque 2. |
| `/close-ticket` cierra un ticket sin resolver | El skill no comprueba los criterios. Pedir a Claude que lo corrija. |
| `/close-ticket` escribe "No cerrado" en el ticket | El skill no distingue entre informar y cerrar. Deshacer con `git restore docs/tickets/<ticket>.md` y pedir que solo escriba si se cumplen los criterios. |
| No se puede cerrar ningún ticket BRI | El skill aplica el oráculo de INC-0142 a todos los tickets, cuando solo debe contar para INC-0142. |
| `/fewer-permission-prompts` no propone nada | No hay suficientes sesiones previas en el repositorio. |
| El skill se invoca solo | Falta `disable-model-invocation: true`. |
| El hook no se ejecuta | Revisar `/hooks`. En Windows, comprobar que el entorno estaba activado al abrir `claude`. |
| El hook lanza los tests tras cualquier edición | No filtra por ruta: debe comprobar `tool_input.file_path`. |
| Claude escribe en `.claude/settings.json` algo que se pidió como local | Moverlo a `settings.local.json` antes del commit. |
