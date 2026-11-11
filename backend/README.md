# Backend — FastAPI + SQLAlchemy 2.0 + Alembic + Supabase

Arquitectura por capas (router → servicio → repositorio). Los motores de `app/optimizacion/`
son Python puro: no importan FastAPI ni la base de datos, para probarlos de forma aislada.

```
app/
├── api/v1/routers/   # endpoints REST (prefijo /api/v1)
├── core/             # config (pydantic-settings)
├── db/               # engine, sesión, Base y modelos ORM
├── schemas/          # esquemas Pydantic (DTO)
├── repositories/     # acceso a datos
├── services/         # lógica de negocio
├── optimizacion/     # red.py, exacto/, genetico/, sensibilidad/
└── reportes/         # PDF y Excel
alembic/              # migraciones V1, V2, V3…
tests/                # unit/, integration/, data/
```

## Puesta en marcha

```bash
cd backend
py -3.12 -m venv .venv          # Linux / macOS: python3.12 -m venv .venv
.venv\Scripts\activate          # Linux / macOS: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # completar DATABASE_URL de Supabase
alembic upgrade head
uvicorn app.main:app --reload   # http://localhost:8000/docs
```

## Base de datos (Supabase, PostgreSQL 15)

- Driver: SQLAlchemy 2.0 + psycopg 3 (síncrono). `pydantic-settings` lee `backend/.env`.
- Conexión por el **Session pooler, puerto 5432**. No usar el Transaction pooler (6543):
  rompe los prepared statements de psycopg 3.
- Las tablas se crean **solo** con migraciones de Alembic. Cada migración activa RLS
  (`ENABLE ROW LEVEL SECURITY`) sin políticas en las tablas que crea: el backend entra como
  `postgres`, dueño de las tablas, y la API REST de Supabase queda cerrada.
- `backend/.env` nunca se sube al repositorio; solo `backend/.env.example`.

## Pruebas

```bash
ruff check .
pytest --cov=app
```

- `tests/unit/`: sin base de datos.
- `tests/integration/`: usan `TEST_DATABASE_URL`, aplican las migraciones y se saltan si la
  variable no está definida. **Nunca** se corren contra Supabase (el `conftest.py` lo impide).
- En CI, `TEST_DATABASE_URL` apunta al servicio `postgres:15` de GitHub Actions.
- Ruff no revisa `app/optimizacion/exacto/`, `genetico/` ni `sensibilidad/`: el equipo las
  ajusta al conectar sus motores.
