# Demos de la Unidad 3 · Desarrollo asistido por IA

Seis demos pequeñas e independientes. Cada una se ejecuta con un solo comando y muestra una idea:

| Carpeta | Qué se ve | Comando |
|---|---|---|
| [01-instruction-vs-control](01-instruction-vs-control/) | Una instrucción no impide subir un secreto; un control sí | `uv run python 01-instruction-vs-control/run_demo.py` |
| [02-refine-task](02-refine-task/) | «Limpia los datos» frente a la tarea refinada, comparadas con lo que el equipo quería | `uv run python 02-refine-task/check_result.py` |
| [03-join-inflates](03-join-inflates/) | El informe suma 12.400 € y el origen 10.000 €; `DISTINCT` no lo arregla | `uv run python 03-join-inflates/run_demo.py` |
| [04-ambiguous-dates](04-ambiguous-dates/) | `08/10/2026` acaba siendo el 10 de agosto y un test lo da por bueno | `uv run python 04-ambiguous-dates/run_demo.py` |
| [05-weak-tests](05-weak-tests/) | Se rompe el código y un test sigue en verde | `uv run python 05-weak-tests/run_demo.py` |
| [06-revert-not-reverting](06-revert-not-reverting/) | `git revert` arregla el script, pero no devuelve los datos borrados | `uv run python 06-revert-not-reverting/run_demo.py` |

## Requisitos

- [uv](https://docs.astral.sh/uv/) y Git.
- No hace falta instalar nada más: `uv` descarga Python 3.12 y las dependencias la primera vez que se ejecuta una demo.

## Cómo ejecutarlas

Desde esta carpeta:

```bash
uv sync
uv run python 03-join-inflates/run_demo.py
```

Todas las demos con `run_demo.py` admiten `--pause`, que espera un Enter entre pasos para preguntar qué saldrá antes de cada resultado:

```bash
uv run python 03-join-inflates/run_demo.py --pause
```

La demo 02 necesita un asistente de código; el resto funciona sin ninguno.

## Estructura

```text
.
├── pyproject.toml              pytest y rich (salida en consola)
├── .python-version             3.12
├── 01-instruction-vs-control/  run_demo.py, template/
├── 02-refine-task/             check_result.py, data/, examples/, output/
├── 03-join-inflates/           run_demo.py, data/
├── 04-ambiguous-dates/         run_demo.py, parse_sale_date.py, test_*.py (unittest)
├── 05-weak-tests/              run_demo.py, clean_customers.py, test_weak.py, test_strong.py, data/
└── 06-revert-not-reverting/    run_demo.py, template/
```

Las demos 01 y 06 crean una carpeta `_repo/` con un repositorio Git independiente y la demo 05 crea `_broken/`. Ambas están en `.gitignore` y se regeneran al volver a ejecutar la demo.
