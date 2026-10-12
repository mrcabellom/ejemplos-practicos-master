# Plan de trabajo

Este plan resuelve en seis fases la incidencia
[INC-0142](../docs/tickets/INC-0142.md), la ocupación del 112 % del Brisa
Málaga Playa, y los tickets pendientes BRI-201 a BRI-204. En cada fase,
Claude Code asume una parte mayor del trabajo: primero un objetivo que se
cumple sin intervención, después varias sesiones en paralelo, parte de su
propia configuración, la revisión del código y, por último, la ejecución
sin terminal.

> El agente tiene denegado el acceso a esta carpeta en
> `.claude/settings.json` (`Read(./playbook/**)`), porque contiene los
> resultados esperados y el agente debe llegar a ellos a partir del código
> y los datos.

## El problema, en pocas palabras

Un hotel de 8 habitaciones aparece con 9 ocupadas porque cada cambio en
una reserva se guarda como si fuera una reserva nueva. El oráculo,
`python tasks.py acceptance`, indica cuándo está resuelto.

## Punto de partida de cada fase

Las fases son independientes entre sí. Todas parten de `main`, sin cambios
pendientes y con el almacén reconstruido:

```powershell
git switch main
git status
.venv\Scripts\Activate.ps1
python tasks.py reset
python tasks.py run-all
claude
```

En macOS y Linux, el entorno se activa con `source .venv/bin/activate`.
`git status` debe mostrar `nothing to commit, working tree clean`. Claude
Code se abre desde ese mismo terminal, con el entorno activado.

Cuando una fase aprovecha el resultado de otra, explica cómo generarlo si
no se dispone de él.

## Fases

| # | Fase | Funciones de Claude Code | Criterio de cierre |
| --- | --- | --- | --- |
| [1](PHASE-1.md) | Diagnóstico | `/plan`, `/btw`, `/recap`, `/branch` | La causa localizada, con su archivo y su línea |
| [2](PHASE-2.md) | `/goal` y el oráculo | `/goal`, `acceptEdits`, hook `Stop` | Oráculo en verde con una condición que delimita el cambio |
| [3](PHASE-3.md) | Sesiones en paralelo | `claude --bg`, `claude agents`, worktrees, `/subtask`, `/fork`, `/batch` | Cuatro tickets integrados sin conflictos |
| [4](PHASE-4.md) | Configuración generada por Claude | `/fewer-permission-prompts`, skills, hooks, `/statusline`, `/doctor` | Configuración revisada y repartida entre la del equipo y la personal |
| [5](PHASE-5.md) | Revisión automática | `/diff`, `/code-review`, `/simplify`, subagente | Una decisión sobre si el cambio se integra en `main` |
| [6](PHASE-6.md) | Ejecución sin terminal y cierre | `claude -p`, `/loop`, `/schedule`; con GitHub, `/install-github-app` y `@claude` | `check` en verde y respuesta enviada a Revenue |

## Sin cuenta de GitHub

Basta con Git. Todas las fases se pueden completar en local; la única
excepción es el bloque opcional de GitHub de la fase 6.

En la fase 3, si no es posible subir ramas al remoto, el trabajo de cada
sesión se queda en una rama local y se integra de la misma forma.

## Entregables

No forman parte del repositorio de partida: cada fase genera los suyos.

| Entregable | Fase |
| --- | --- |
| Rama `fix/inc-0142` con el arreglo y al menos un test nuevo | 2 |
| Rama `backlog/bri` con los tickets BRI-201 a BRI-204 | 3 |
| Skill `.claude/skills/close-ticket/` y permisos revisados | 4 |
| Tabla de hallazgos por revisor y decisión final | 5 |
| `check` en verde y respuesta en `docs/tickets/INC-0142.md` | 6 |

## Cifras de referencia

| | Con el defecto | Tras el arreglo |
| --- | ---: | ---: |
| `python tasks.py acceptance` | 5 criterios en `FAIL` | 5 en `PASS` |
| Filas en `fct_bookings` tras `run-all` | 11 | 8 |
| Reservas distintas | 8 | 8 |
| Málaga, noche del 2 de marzo | 9/8 · 112 % | 7/8 · 88 % |
| Málaga, noche del 3 de marzo | 8/8 · 100 % | 6/8 · 75 % |
| Madrid, noche del 2 de marzo | 7/10 · 70 % | 4/10 · 40 % |
| Madrid, noches del 3 y 4 de marzo | 3/10 · 30 % | 0/10 · 0 % |

Coste orientativo: el `/goal` de la fase 2 cuesta unos 0,20 $ y tarda
menos de un minuto; cada ticket de la fase 3, unos 0,15 $ y medio minuto.
