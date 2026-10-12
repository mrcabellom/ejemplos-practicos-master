# kinesia-booking-api

Repositorio de la API de reservas de **Kinesia**, una clínica de fisioterapia ficticia de Madrid con dos
fisioterapeutas, Ana y Luis.

La clínica gestiona las citas en una hoja de cálculo compartida y quiere una API para la recepción. Este
repositorio contiene la petición y las herramientas de Python. La API se construye con *spec-driven development*
(GSD Core).

## Qué hay ya

```
docs/brief.md                  ← petición de Marta Gil, gerente de la clínica
pyproject.toml, uv.lock        ← proyecto Python 3.12 gestionado con uv (fastapi, uvicorn, pytest, httpx)
.python-version                ← fija Python 3.12
```

## Uso

La versión de Python (3.12) está fijada en `.python-version`. Si no está instalada, `uv sync` la descarga.

```bash
uv sync
```

El paquete `src/kinesia/` y la carpeta `tests/` todavía no existen: se crean al construir la API.
