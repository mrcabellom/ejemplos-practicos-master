# Demo 02 · Refinar la tarea

## Qué se ve

Se le pide algo vago a un asistente de código («limpia los datos de ventas») y después la tarea refinada. `check_result.py` compara cada resultado con lo que el equipo quería, sin discutir a ojo.

Sirve cualquier asistente de código.

La petición vaga no falla porque el asistente sea torpe: «limpiar» admite muchas lecturas y cada una es razonable. El fichero tiene varias cosas que **parecen** errores y no lo son para este equipo:

| En el fichero | Lo que «limpiar» invita a hacer | Para el equipo es… |
|---|---|---|
| Espacio al final en `Luis Pérez ` y `marta ruiz` en minúsculas | Recortar y poner mayúsculas | Un dato de origen: no se toca |
| `norte`, `OESTE` y una región vacía | Unificar mayúsculas o rellenar | Un dato de origen: no se toca |
| Ventas 2 y 3 iguales salvo el id | Eliminar el «duplicado» | Dos ventas legítimas |
| Importe `-45.90` | Eliminarlo o corregirlo | Una devolución |
| Fecha `29/02/2026` | Borrar la fila | Una fecha inválida: queda vacía y la fila se conserva |

## Estructura

```text
02-refine-task/
├── check_result.py   comprobador: contiene el resultado esperado (el asistente no debe verlo)
├── examples/         dos resultados de ejemplo para probar el comprobador
└── workspace/        carpeta de trabajo del asistente
    ├── data/sales.csv
    └── output/
```

**Abre el asistente en `workspace/`, nunca en `02-refine-task/`.** El comprobador queda fuera de su alcance: si lo viera, tendría la regla y el resultado esperado y resolvería la tarea sin que se la hayas dado.

## Ejecutar

1. Abre el asistente en `workspace/` con una conversación nueva.
2. Pega la petición vaga.
3. Comprueba el resultado desde `02-refine-task/`: `uv run python check_result.py`.
4. Limpia con `uv run python check_result.py --reset` y abre otra conversación nueva.
5. Pega la petición refinada y comprueba otra vez.

**1. Petición vaga**

```text
Limpia los datos de ventas de data/sales.csv y guarda el resultado en output/sales_clean.csv.
```

**2. Petición refinada**

```text
Normaliza las fechas de la columna sale_date de data/sales.csv y guarda el resultado en output/sales_clean.csv.

- Problema: sale_date mezcla «2026-10-08» y «08/10/2026».
- Regla de negocio: el origen usa día/mes/año; «08/10/2026» es el 8 de octubre.
- Resultado esperado: todas las fechas en formato ISO (AAAA-MM-DD).
- Fuera de alcance: no cambies otras columnas ni elimines filas.
- Criterios de aceptación: una fecha inválida queda vacía y se informa de cuántas hay.
  Añade un test con ambos formatos y una fecha inválida.
- Si algo no está claro (por ejemplo, qué hacer con fechas futuras), pregunta antes de decidir.
```

## Qué mide el comprobador

Compara cada fila con el fichero original y marca:

- **Fecha:** ¿está en ISO y con la lectura día/mes?
- **Otras columnas:** ¿se ha cambiado algo de `customer`, `region` o `amount`?
- **Filas:** ¿falta alguna?
- **Columnas nuevas:** ¿se ha añadido alguna?

## Qué observar

| | Petición vaga | Petición refinada |
|---|---|---|
| ¿Cómo interpreta `08/10/2026`? | | |
| ¿Qué hace con `29/02/2026`? | | |
| ¿Elimina ventas (duplicadas, devolución…)? | | |
| ¿Cambia nombres, regiones o importes? | | |
| ¿Pregunta algo antes de decidir? | | |

Si el asistente pregunta antes de actuar, responde «lo que creas mejor»: la decisión sigue sin estar en la tarea.

## Resultados de ejemplo

`examples/` contiene dos ficheros para comprobar el funcionamiento de `check_result.py` sin asistente:

```bash
uv run python check_result.py examples/vague_result.csv
uv run python check_result.py examples/refined_result.csv
```

Son ejemplos escritos a mano de un resultado típico y de uno correcto, no la salida de ningún asistente concreto. El resultado real varía entre asistentes y entre ejecuciones.
