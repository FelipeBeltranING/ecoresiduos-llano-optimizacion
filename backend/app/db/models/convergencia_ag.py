import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


# Tabla convergencia_ag: mejor costo y costo promedio por generación del AG
class ConvergenciaAG(Base):
    __tablename__ = "convergencia_ag"
    __table_args__ = (
        CheckConstraint("generacion >= 0", name="ck_convergencia_generacion_no_negativa"),
    )

    ejecucion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ejecucion.id", ondelete="CASCADE"), primary_key=True
    )
    generacion: Mapped[int] = mapped_column(Integer, primary_key=True)
    mejor_costo: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    costo_promedio: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
