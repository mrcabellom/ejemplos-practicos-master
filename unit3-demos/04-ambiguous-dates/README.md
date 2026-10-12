# Demo 04 · Un test en verde no es una prueba de que esté bien

## Qué se ve

La columna `sale_date` mezcla `2026-10-08` y `08/10/2026`. El origen escribe día/mes/año, pero el asistente supuso mes/día y escribió sus propios tests con esa misma suposición.

- `parse_sale_date.py`: el código del asistente. La suposición está en una línea: `SLASH_FORMAT = "%m/%d/%Y"`.
- `test_written_by_assistant.py`: los tests del asistente. Pasan.
- `test_data_contract.py`: los tests escritos desde el contrato de datos. Fallan.

Se ejecutan con `unittest`, que viene con Python.

## Ejecutar

```bash
uv run python 04-ambiguous-dates/run_demo.py --pause
```

| Paso | Qué sale |
|---|---|
| 1 | El código del asistente: `08/10/2026` se lee como el 10 de agosto |
| 2 | Los tests del asistente: **3 de 3 pasan** (verificación) |
| 3 | Los tests del contrato: **2 de 3 fallan** (validación) |
| 4 | Se cambia una línea en una copia y los tests del contrato pasan |

También se pueden lanzar a mano desde `04-ambiguous-dates/`:

```bash
uv run python -m unittest -v test_written_by_assistant
uv run python -m unittest -v test_data_contract
```

## Para tener en cuenta

- **Verificación:** ¿el código cumple lo que se le pidió? Los tests del asistente pasan.
- **Validación:** ¿responde a lo que el origen necesita? Los tests del contrato lo dicen: no.
- La regla «el origen usa día/mes» no se puede deducir del código: tiene que estar en la tarea.
- Con el código corregido, los tests del asistente fallarían: codificaban la suposición equivocada. Hay que corregirlos también.
