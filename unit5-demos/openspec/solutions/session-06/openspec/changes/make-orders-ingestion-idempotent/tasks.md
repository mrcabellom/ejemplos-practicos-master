# Tasks

## 1. Sustitución atómica

- [ ] 1.1 Sustituir las filas del `_source_file` con DELETE + INSERT en una transacción, pasando el nombre del fichero como parámetro; verificar con un test que dos cargas de 2026-10-01 dejan 10 filas
- [ ] 1.2 Verificar con un test que un `2026-10-02.csv` corregido sin O-1011 deja 4 filas en bronze y O-1011 no llega a silver
- [ ] 1.3 Verificar con un test (con un fichero corregido sin la columna `status`, que hace fallar el INSERT) que bronze conserva las 5 filas anteriores

## 2. Comprobación final

- [ ] 2.1 Verificar que `uv run python run_pipeline.py --date 2026-10-02` ejecutado dos veces deja 5 filas de `2026-10-02.csv` en bronze, y que `uv run pytest` pasa completo
