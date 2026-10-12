# caveman-copilot

Ejemplo mínimo del skill [Caveman](https://github.com/JuliusBrussee/caveman) en GitHub Copilot. Con él, Copilot
responde de forma escueta: menos tokens y el mismo contenido técnico.

## Cómo funciona

`.github/skills/caveman/SKILL.md` es el skill oficial de Caveman, copiado sin cambios de
`plugins/caveman/skills/caveman/SKILL.md` en el repositorio original. Copilot (los *agent skills* de VS Code)
descubre los skills de `.github/skills/` y carga este cuando se le pide.

## Probarlo

1. Abre esta carpeta en VS Code con GitHub Copilot Chat en modo agente.
2. Abre `example.py`.
3. Pregunta: `/caveman Why does example.py crash and how do I fix it?`
4. Compara la respuesta con la de la misma pregunta sin `/caveman`.

Para desactivarlo, escribe `stop caveman` o `normal mode`.

## Un par de hooks de broma

`.github/hooks/hooks.json` define dos hooks muy simples. Al empezar la sesión y con cada prompt, añaden una línea a
`caveman-log.txt` en la raíz de esta carpeta. Git ignora ese fichero.

Los hooks funcionan en **Copilot CLI** y en el **agente en la nube de Copilot**. Según la
[documentación de hooks](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-hooks-reference),
Copilot Chat en VS Code no aparece entre los entornos compatibles, así que se prueban con la CLI:

```bash
copilot
```

Envía un prompt y después revisa `caveman-log.txt`.

## Otras formas de instalarlo (según el INSTALL.md original)

Para que esté siempre activo, en lugar de activarlo en cada petición, el instalador oficial escribe las mismas reglas
en `.github/copilot-instructions.md`:

```bash
npx -y github:JuliusBrussee/caveman -- --only copilot --with-init
```

Nota: el README original advierte que Caveman no ahorra nada si se paga Copilot por petición *premium* en lugar de
por token. Generar menos tokens de salida no reduce ese precio.
