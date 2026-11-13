from pydantic import BaseModel


class ResumenCasoBase(BaseModel):
    empresas: int
    plantas: int
    rutas: int


class ResumenAcopios(BaseModel):
    acopios: int
    rutas: int
