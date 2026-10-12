# Demo 03 · Un JOIN que infla el informe

## Qué se ve

Un informe de ventas por región suma **12.400 €** cuando el origen tiene **10.000 €**. El arreglo rápido con `DISTINCT` tampoco cuadra; buscar la causa, sí.

Datos (`data/`):

- `sales.csv`: 6 ventas. Las ventas 2 y 3 son iguales y las dos son legítimas.
- `customers.csv`: Luis (cliente 2) aparece repetido tal cual; Marta (cliente 3) tiene dos versiones porque cambió de región.

## Ejecutar

```bash
uv run python 03-join-inflates/run_demo.py --pause
```

| Paso | Qué sale |
|---|---|
| 1. Total en el origen | 10.000 |
| 2. JOIN directo | 12.400: el síntoma |
| 3. «Arreglo» con `DISTINCT` | 10.300: sigue sin cuadrar, funde dos ventas legítimas y deja a Marta en dos regiones |
| 4. Diagnóstico | Los clientes 2 y 3 aparecen dos veces en `customers`: la causa |
| 5. Un cliente por `customer_id` (versión más reciente) antes del JOIN | 10.000 |
| 6. Comprobación de conciliación | `OK` |

## Para tener en cuenta

- «El total no cuadra» es el síntoma; «clientes repetidos» es la hipótesis que se comprueba en el paso 4.
- En el paso 5 hay una decisión de negocio: quedarse con la versión **más reciente** de Marta. Quedarse con una fila cualquiera también cuadra el total, pero puede asignar sus ventas a otra región.
- La comprobación del paso 6 es una conciliación: el total del informe debe coincidir con el del origen. Conviene que forme parte de los tests.
