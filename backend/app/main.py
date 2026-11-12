from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import (
    analisis,
    datos,
    ejecuciones,
    health,
    nodos,
    optimizacion,
    parametros,
    red,
    reportes,
    rutas,
    sensibilidad,
)
from app.core.config import settings

PREFIJO_API = "/api/v1"

# Aplicación principal
app = FastAPI(title="EcoResiduos del Llano API", version="1.0.0")

# CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.lista_cors(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers de la versión 1
app.include_router(health.router, prefix=PREFIJO_API)
app.include_router(datos.router, prefix=PREFIJO_API)
app.include_router(nodos.router, prefix=PREFIJO_API)
app.include_router(rutas.router, prefix=PREFIJO_API)
app.include_router(parametros.router, prefix=PREFIJO_API)
app.include_router(red.router, prefix=PREFIJO_API)
app.include_router(optimizacion.router, prefix=PREFIJO_API)
app.include_router(ejecuciones.router, prefix=PREFIJO_API)
app.include_router(sensibilidad.router, prefix=PREFIJO_API)
app.include_router(analisis.router, prefix=PREFIJO_API)
app.include_router(reportes.router, prefix=PREFIJO_API)
