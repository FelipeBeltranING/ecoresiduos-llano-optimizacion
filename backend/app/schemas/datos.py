from pydantic import BaseModel


# Respuesta de la carga del caso base
class ResumenCasoBase(BaseModel):
    empresas: int
    plantas: int
    rutas: int
