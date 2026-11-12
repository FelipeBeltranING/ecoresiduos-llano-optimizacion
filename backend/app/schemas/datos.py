from pydantic import BaseModel


# Respuesta de la carga del caso base
class ResumenCasoBase(BaseModel):
    empresas: int
    plantas: int
    rutas: int


# Respuesta de la carga de los centros de acopio (HU-17)
class ResumenAcopios(BaseModel):
    acopios: int
    rutas: int
