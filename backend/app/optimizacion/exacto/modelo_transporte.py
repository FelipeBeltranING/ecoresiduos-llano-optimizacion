from app.optimizacion.exacto.transbordo import ModeloTransbordo
from app.optimizacion.red import RedLogistica


# Adaptador del contrato histórico: el cálculo vive en transbordo.py
class ModeloTransporte:
    def __init__(self, red: RedLogistica) -> None:
        self.red = red
        self.modelo = ModeloTransbordo(red)

    def resolver(self) -> dict:
        return self.modelo.resolver()
