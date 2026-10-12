# Plan de trabajo

Seis fases, una por semana de servicio. En cada una el operador envía una
entrega con su ticket, y el equipo la resuelve con un agente de código. Cada
fase recoge los prompts, el resultado esperado y qué hacer si el agente se
desviase.

> El agente tiene denegado el acceso a esta carpeta y `deliveries/` en
> `.claude/settings.json`: contienen los resultados esperados y las entregas
> futuras, y el agente debe llegar a sus conclusiones con el código y los
> datos.

## Arrancar una fase

Las fases van **en orden**: cada entrega se suma a las anteriores y cada
solución se apoya en el anterior.

```powershell
git switch main
git status
.venv\Scripts\Activate.ps1
python tasks.py deliver N
```

En macOS y Linux, `source .venv/bin/activate`. `git status` debe decir
`nothing to commit, working tree clean`. `deliver N` simula al operador:
deja `inbox/week-N.csv` y su ticket en `docs/tickets/`. La fase 1 no lo
necesita. Después, abre `claude` desde ese mismo terminal.

## Fases

| # | Fase | Ticket | Criterio de cierre | Tests |
| --- | --- | --- | --- | ---: |
| [1](PHASE-1.md) | Entender sin escribir | OPS-101 | Respuesta con cada afirmación respaldada por archivo y línea | 9 |
| [2](PHASE-2.md) | Instrucciones y contexto | OPS-102 | Trabajo retomado tras `/clear` solo con `docs/plans/status.md` | 10 |
| [3](PHASE-3.md) | Skill y subagente | OPS-103 | Validación repetible y decisión del revisor aplicada | 11 |
| [4](PHASE-4.md) | Hooks y permisos | OPS-104 | Cada protección clasificada: instrucción, hook, permiso o aislamiento | 12 |
| [5](PHASE-5.md) | MCP y especificación | OPS-105 | Plan aprobado antes de tocar código y contexto medido | 13 |
| [6](PHASE-6.md) | Vigilancia con `/loop` | OPS-106 | Caída detectada sin intervención y arreglo revisado | 14 |

## Entregables

| Archivo | Fase |
| --- | --- |
| Notas y respuesta en `docs/tickets/OPS-10N.md` | Todas |
| `docs/plans/predictions.md` | 1, y se comprueba en la 3, 4 y 6 |
| `docs/plans/status.md` | 2, y se mantiene hasta el final |
| Un test nuevo en `tests/test_bikes.py` | De la 2 a la 6 |

## Cifras de referencia

| Fase | Al llegar la entrega | Tras el arreglo |
| --- | --- | --- |
| 1 | 11 válidos, 1 rechazado · OK | — |
| 2 | `week-2.csv`: 42 % rechazado | 23 válidos · OK |
| 3 | `trip_id` duplicado: T0103, T0104, T0105 | 30 válidos · 3 `viaje duplicado` · OK |
| 4 | `week-4.csv`: 40 % rechazado | 40 válidos · OK |
| 5 | Duración fuera de rango: 30 viajes | 3.010 válidos · OK |
| 6 | `KeyError: 'user_type'` | 3.018 válidos · OK |
