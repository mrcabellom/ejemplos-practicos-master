Vigila la bandeja de entregas sin cambiar código.

1. Ejecuta `python tasks.py pipeline`.
2. Responde en una sola línea:
   - si pasa: «OK: N viajes, M entregas, última: week-X.csv»;
   - si no cumple: «FALLA: » y el primer problema de la lista;
   - si la transformación se rompe: «SE ROMPE: » y la última línea del error.
3. No edites archivos, no toques `inbox/` y no lances `deliver`.
4. Si el pipeline pasa después de haber fallado en una iteración anterior,
   dilo y detén el bucle.
