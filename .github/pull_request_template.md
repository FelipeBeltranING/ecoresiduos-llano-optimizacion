## Historia o ítem

Closes #<!-- número de la issue -->

**HU / T:** <!-- p. ej. HU-07 · Resolver el modelo de transporte con el método exacto -->

## Qué cambia

<!-- Resumen corto de lo que hace este PR y por qué. -->

## Cómo probarlo

<!-- Pasos para que el revisor lo verifique (comandos, endpoint, pantalla, datos). -->

## Evidencia

<!-- Capturas o video de los criterios de aceptación. Para interfaz: 360, 768 y 1280 px. -->

## Checklist — Definition of Done

- [ ] La rama sale de `develop` y el PR apunta a `develop`.
- [ ] CI en verde (ruff, ESLint, pytest, Vitest, build).
- [ ] Pruebas unitarias escritas; cobertura ≥ 80 % del módulo backend tocado.
- [ ] Todos los criterios de aceptación de la HU están cubiertos.
- [ ] Interfaz probada a 360, 768 y 1280 px sin errores en la consola (si aplica).
- [ ] Endpoint documentado en Swagger/OpenAPI (si aplica).
- [ ] Migración Alembic incluida si cambió el esquema (si aplica).
- [ ] Docstrings o comentarios donde la lógica no es obvia.
- [ ] Sin credenciales ni `.env` en el commit.
