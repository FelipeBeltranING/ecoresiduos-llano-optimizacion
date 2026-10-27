# Backend — FastAPI + SQLAlchemy 2.0 + Alembic

Arquitectura por capas (router → servicio → repositorio). Los motores de `app/optimizacion/`
son Python puro: no importan FastAPI ni la base de datos, para probarlos de forma aislada.

```
app/
├── api/v1/routers/   # endpoints REST (prefijo /api/v1)
├── core/             # config (pydantic-settings), errores, logging
├── db/               # engine, sesión, Base y modelos ORM
├── schemas/          # esquemas Pydantic (DTO)
├── repositories/     # acceso a datos
├── services/         # lógica de negocio
├── optimizacion/     # red.py, exacto/, genetico/, sensibilidad/
└── reportes/         # PDF y Excel
alembic/              # migraciones V1, V2, V3…
tests/                # unit/, integration/, data/
```

**Pendiente en T-01 (Julián Báez):** `pyproject.toml`, `app/main.py`, `core/config.py`,
`db/session.py`, `alembic init` y la migración V1 (`nodo`, `ruta`, `parametro_global`).
