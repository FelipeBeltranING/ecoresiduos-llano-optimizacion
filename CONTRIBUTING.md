# Guía de contribución — Grupo Orion

Este documento resume cómo trabajamos en el repositorio. El detalle completo está en el
Documento Base del proyecto (secciones 6, 15 y 16).

## 1. Flujo de trabajo de una historia

1. Toma una tarjeta de la columna **Ready** del tablero y asígnatela.
2. Actualiza `develop` y crea tu rama desde ahí:
   ```bash
   git checkout develop && git pull
   git checkout -b feature/HU-07-modelo-exacto
   ```
3. Mueve la tarjeta a **En curso**. Haz commits pequeños con Conventional Commits.
4. Abre un Pull Request hacia `develop` con la plantilla. Enlaza la issue con `Closes #N`.
5. Mueve la tarjeta a **En revisión**. Se necesita **1 aprobación** y el **CI en verde**.
6. Merge con **squash**. La tarjeta pasa a **Hecho** cuando el PO verifica los criterios de aceptación.

## 2. Ramas

| Rama | Uso | Reglas |
| --- | --- | --- |
| `main` | Versión estable y desplegada | Protegida. Solo PR desde `develop` o `release/*`, con CI en verde |
| `develop` | Integración del sprint | Protegida. Solo por PR con 1 revisión |
| `feature/HU-xx-descripcion` | Una rama por historia de usuario | Sale de `develop` |
| `fix/descripcion` | Corrección de errores | Sale de `develop` |
| `chore/T-xx-descripcion` | Ítems técnicos (configuración, CI, despliegue) | Sale de `develop` |
| `release/v1.0.0` | Cierre de la entrega | Sale de `develop`, se integra en `main` |

## 3. Commits (Conventional Commits en español)

```
<tipo>(<ámbito>): <descripción en minúscula y en presente>
```

Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.

Ejemplos:

```
feat(genetico): agrega cruce de dos puntos por fila
test(exacto): verifica Z* del caso base
fix(rutas): rechaza distancias menores o iguales a 0
docs(readme): instrucciones de ejecución local
```

## 4. Convenciones de código

| Elemento | Convención | Ejemplo |
| --- | --- | --- |
| Python | PEP 8 con ruff; type hints obligatorios; `snake_case` | `def calcular_gap(z_ag: float, z_opt: float) -> float` |
| TypeScript | ESLint + Prettier; componentes en `PascalCase`; hooks `useX` | `MapaFlujos.tsx`, `useNodos.ts` |
| Versionado | SemVer con tags | `v0.1.0` (Sprint 1), `v1.0.0` (entrega) |
| Variables de entorno | `.env` no se versiona; `.env.example` sí | `DATABASE_URL`, `CORS_ORIGINS`, `VITE_API_URL` |

Nunca subas credenciales de Supabase al repositorio. Solo el backend usa `DATABASE_URL`.

## 5. Definition of Ready (DoR)

Una historia solo entra al Sprint Planning si cumple **todos** estos puntos:

1. Está escrita en formato Como / Quiero / Para y está asociada a una épica.
2. Tiene criterios de aceptación Dado / Cuando / Entonces claros, verificables y con datos concretos.
3. Está estimada en story points (máximo 13; si es mayor, se divide).
4. Sus dependencias están identificadas y resueltas o planificadas en el mismo sprint.
5. Tiene diagramas de clases y de secuencia esbozados (Documento Base, sección 12).
6. Si tiene interfaz, su mockup está aprobado por el PO (sección 13).
7. El contrato de API (endpoint, request y response) está definido (sección 9.4).
8. Los datos de prueba y los casos de prueba están identificados (secciones 14 y 17).
9. Tiene un responsable asignado y cabe en la capacidad restante del sprint.

## 6. Definition of Done (DoD)

### Historia de usuario

- Código integrado a `develop` mediante PR con al menos 1 revisión aprobada.
- CI en verde: ruff, ESLint, pytest, Vitest y build.
- Pruebas unitarias escritas; cobertura ≥ 80 % del módulo backend tocado.
- Todos los criterios de aceptación verificados por el PO, con evidencia (captura o video).
- Interfaz probada a 360, 768 y 1280 px sin errores en la consola.
- Endpoint documentado en Swagger/OpenAPI; migración Alembic incluida si cambió el esquema.
- Docstrings y comentarios donde la lógica no es obvia; tarjeta movida a **Hecho**.

### Sprint

- Todas las historias comprometidas cumplen el DoD o vuelven al backlog.
- Las pruebas de integración y la regresión de las historias anteriores pasan.
- El incremento está desplegado en la nube y se mostró en la Sprint Review.
- La retrospectiva está registrada con al menos 2 acciones de mejora.

### Release (entrega final, 12 de noviembre)

- Todas las historias Must están terminadas; las Should/Could no terminadas quedan documentadas.
- Pruebas E2E de los flujos principales en verde; plan de pruebas ejecutado y reportado.
- README con instrucciones de instalación y ejecución; tag `v1.0.0` en `main`.
- Informe técnico IEEE completo con resultados reales del sistema.
- Respaldo de la base de datos y video de demostración de respaldo.

## 7. Defectos

Repórtalos con la plantilla **Reporte de defecto**. Usa la etiqueta de severidad
(`sev: crítica`, `sev: alta`, `sev: media`, `sev: baja`). Los defectos críticos bloquean el merge.
