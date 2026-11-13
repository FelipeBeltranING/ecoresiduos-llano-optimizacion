import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Metodo(enum.StrEnum):
    EXACTO = "EXACTO"
    GENETICO = "GENETICO"


class Ejecucion(Base):
    __tablename__ = "ejecucion"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    metodo: Mapped[Metodo] = mapped_column(Enum(Metodo, name="metodo"), nullable=False)
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    costo_total: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    tiempo_ms: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    parametros: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    snapshot_red: Mapped[dict] = mapped_column(JSONB, nullable=False)
    escenario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("escenario.id", ondelete="SET NULL"), nullable=True
    )
    violaciones: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
