# Demo 06 · Revertir el código no revierte sus efectos

## Qué se ve

Un script borra los clientes inactivos (más de 365 días sin comprar). Un «agente» lo simplifica y deja la ventana en 30 días, con un mensaje de commit que no lo dice. Al ejecutarlo se borran clientes activos. `git revert` arregla el script, pero **los clientes siguen borrados** hasta que se restaura la copia.

## Ejecutar

```bash
uv run python 06-revert-not-reverting/run_demo.py --pause
```

| Paso | Qué sale |
|---|---|
| 1 | 10 clientes |
| 2 | El diff del commit del agente: `365` → `30`. El mensaje no lo menciona |
| 3 | Copia de seguridad y ejecución: borra 7 (debería borrar 3). Quedan 3 |
| 4 | `git revert HEAD`: el código vuelve a 365, pero siguen quedando 3 |
| 5 | Restaurar la copia: 10 clientes |
| 6 | El script correcto borra 3. Quedan 7 |

## Para tener en cuenta

- Restaurar el código y recuperar el estado son decisiones distintas. Sin la copia del paso 3 no habría forma de recuperar los 7 clientes.
- Solo el diff muestra el cambio real: el mensaje del commit y el docstring siguen diciendo otra cosa.
- Un `DELETE` sobre datos reales es de riesgo alto: el agente propone y una persona autoriza, con una copia preparada.
