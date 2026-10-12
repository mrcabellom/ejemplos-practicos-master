# Demo 05 · ¿Protegen realmente las pruebas?

## Qué se ve

`clean_customers.py` deduplica clientes por email normalizado: `Ana@Mail.com` y `ana@mail.com ` son el mismo cliente. Hay dos ficheros de tests:

- `test_weak.py`: comprueba que se eliminan duplicados **exactos**.
- `test_strong.py`: comprueba la propiedad central, que mayúsculas y espacios no crean clientes distintos.

El script rompe el código a propósito en una copia (`_broken/`) y muestra qué tests se dan cuenta.

## Ejecutar

```bash
uv run python 05-weak-tests/run_demo.py --pause
```

| Paso | Qué sale |
|---|---|
| 1 | 5 filas leídas, 3 clientes únicos |
| 2 | Los dos ficheros de tests pasan |
| 3 | Se quita `.lower()` de `normalize_email()` (solo en la copia) |
| 4 | El test débil **sigue pasando** |
| 5 | El fuerte falla: 3 de 4 tests |
| Extra | `customers_blank.csv`: 4 clientes y salen 3 |

## Para tener en cuenta

- Si al romper la propiedad central no falla ningún test, esos tests no la protegen, aunque estén en verde.
- Un asistente que «añade tests» puede escribir justo el débil: comprueba algo cierto pero secundario.
- El extra del paso final ilustra un buen comentario de revisión: lugar, condición y consecuencia, con un caso reproducible.
