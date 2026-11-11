import uuid
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


# Tabla ruta: arcos dirigidos entre dos nodos
class Ruta(Base):
    __tablename__ = "ruta"
    __table_args__ = (
        UniqueConstraint("origen_id", "destino_id", name="uq_ruta_origen_destino"),
        CheckConstraint("origen_id <> destino_id", name="ck_ruta_origen_distinto_destino"),
        CheckConstraint("distancia_km > 0", name="ck_ruta_distancia_positiva"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    origen_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nodo.id", ondelete="CASCADE"), nullable=False
    )
    destino_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nodo.id", ondelete="CASCADE"), nullable=False, index=True
    )
    distancia_km: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    costo_km_t: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    habilitada: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    # Polilínea codificada del trazado vial (OSRM) y origen de la distancia
    geometria: Mapped[str | None] = mapped_column(Text, nullable=True)
    duracion_min: Mapped[Decimal | None] = mapped_column(Numeric(8, 1), nullable=True)
    fuente_distancia: Mapped[str | None] = mapped_column(String(12), nullable=True)
