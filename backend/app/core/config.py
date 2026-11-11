from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Ubicación del archivo .env del backend
CARPETA_BACKEND = Path(__file__).resolve().parents[2]
ARCHIVO_ENV = CARPETA_BACKEND / ".env"


# Variables de entorno del backend
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ARCHIVO_ENV, extra="ignore")

    database_url: str
    test_database_url: str | None = None
    cors_origins: str = "http://localhost:5173"

    def lista_cors(self) -> list[str]:
        origenes = []
        for origen in self.cors_origins.split(","):
            origen_limpio = origen.strip()
            if origen_limpio != "":
                origenes.append(origen_limpio)
        return origenes


settings = Settings()
