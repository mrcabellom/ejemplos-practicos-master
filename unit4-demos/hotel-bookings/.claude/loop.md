Revisa el estado del almacén sin modificar nada.

1. Ejecuta `python tasks.py reconcile`. Si falta el almacén o hay otro error
   de ejecución, informa de que falta evidencia y detente; no lo
   interpretes como duplicados.
2. Si el grain se respeta, responde en una línea y termina.
3. Si hay reservas duplicadas, indica cuáles y cuántas veces aparecen.
4. No corrijas nada, no borres filas y no lances cargas ni reprocesos.

Si tres iteraciones seguidas devuelven el mismo estado, dilo y detén el
bucle.
