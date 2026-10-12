# Demo 01 · Una instrucción no es un control

## Qué se ve

El `AGENTS.md` del repositorio de práctica dice No subas credenciales al repositorio. Eso es una **instrucción**: el agente puede no cumplirla. Al intentar el commit de un token, un hook de `pre-commit` lo **bloquea**. Eso es un **control**.

El token es falso: se genera al ejecutar y solo se escribe dentro de `_repo/`.

## Ejecutar

```bash
uv run python 01-instruction-vs-control/run_demo.py --pause
```

| Paso | Qué sale |
|---|---|
| 1 | El contenido de `AGENTS.md`: la instrucción |
| 2 | El «asistente» escribe un token en `settings_local.py` y el commit **se bloquea** |
| 3 | El token se lee de una variable de entorno y el commit **pasa** |

## Cómo funciona

`template/check_secrets.py` busca patrones de secretos en los ficheros preparados para el commit. El script lo instala como hook de `pre-commit` en `_repo/`. Es una versión mínima de lo que hace un escáner real como [gitleaks](https://github.com/gitleaks/gitleaks), pero sin descargas.

## Para tener en cuenta

- Los hooks locales se pueden saltar con `git commit --no-verify`. Por eso el mismo control debe ejecutarse también en CI.
- La misma idea vale para otros controles: credenciales de solo lectura en desarrollo y un test o linter que revise los nombres del esquema.
