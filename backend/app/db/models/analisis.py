import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

TIPO_COMPARACION = "COMPARACION"
TIPO_ESCALABILIDAD = "ESCALABILIDAD"
ESTADO_EN_CURSO = "En curso"
ESTADO_TERMINADO = "Terminado"
ESTADO_ERROR = "Error"


class Analisis(Base):
    __tablename__ = "analisis"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    escenario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("escenario.id", ondelete="SET NULL"), nullable=True
    )
    parametros: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    resultado: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
