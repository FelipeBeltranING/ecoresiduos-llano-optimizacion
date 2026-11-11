import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


# Tipos de nodo de la red
class TipoNodo(enum.StrEnum):
    FUENTE = "FUENTE"
    ACOPIO = "ACOPIO"
    PLANTA = "PLANTA"


# Tabla nodo: empresas, centros de acopio y plantas
class Nodo(Base):
    __tablename__ = "nodo"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_nodo_codigo"),
        CheckConstraint("oferta_t >= 0", name="ck_nodo_oferta_no_negativa"),
        CheckConstraint("capacidad_t > 0", name="ck_nodo_capacidad_positiva"),
        CheckConstraint("costo_operacion_t >= 0", name="ck_nodo_costo_operacion_no_negativo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[TipoNodo] = mapped_column(
        Enum(TipoNodo, name="tipo_nodo"), nullable=False, index=True
    )
    municipio: Mapped[str] = mapped_column(String(80), nullable=False)
    tipo_residuo: Mapped[str | None] = mapped_column(String(60), nullable=True)
    oferta_t: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    capacidad_t: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    costo_operacion_t: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    latitud: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitud: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
