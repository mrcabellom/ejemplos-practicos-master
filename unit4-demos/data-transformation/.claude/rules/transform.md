---
paths:
  - "src/bikes/**"
---

# Reglas de la transformación

Se cargan solo cuando Claude trabaja con archivos de `src/bikes/`.

- Un dato que no se puede limpiar se rechaza con su motivo; nunca se
  inventa ni se recorta un valor para que pase.
- Los motivos de rechazo van en español, cortos y en minúsculas
  (`fecha no válida`, `viaje duplicado`).
- Toda regla nueva de `rules.py` lleva su test en `tests/test_bikes.py`.
