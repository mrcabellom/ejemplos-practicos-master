# Runbook: reproceso del almacén

## Cuándo se usa

Cuando el estado histórico de `fct_bookings` es incorrecto y no basta con
corregir el código, porque las filas ya escritas siguen en la tabla.

## Antes de empezar

1. Identificar los extractos afectados y anotarlos en la incidencia.
2. Comprobar que el contrato vigente coincide con lo que se va a escribir.
3. Avisar a los consumidores del contrato. El sistema de precios debe
   congelar tarifas mientras dure el reproceso.
4. Obtener autorización explícita. Un reproceso nunca se lanza por
   iniciativa del agente ni de la persona que desarrolla el cambio.

## Procedimiento

```bash
python tasks.py reset
python tasks.py run --date 2026-03-01
python tasks.py run --date 2026-03-02
python tasks.py run --date 2026-03-03
python tasks.py reconcile
python tasks.py occupancy
```

## Después

- Verificar que el número de reservas distintas coincide con el de filas.
- Verificar que ninguna noche supera la capacidad del hotel.
- Registrar en la incidencia los extractos, las ejecuciones y el resultado.

## Si algo sale mal

Revertir el commit **no** deshace las filas escritas. Para recuperar el
estado anterior hay que restaurar la copia previa del almacén o volver a
ejecutar este runbook con el código anterior.
