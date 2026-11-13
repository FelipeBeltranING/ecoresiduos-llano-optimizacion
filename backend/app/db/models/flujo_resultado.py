import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class FlujoResultado(Base):
    __tablename__ = "flujo_resultado"
    __table_args__ = (CheckConstraint("toneladas >= 0", name="ck_flujo_toneladas_no_negativas"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    ejecucion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ejecucion.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    origen_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nodo.id"), nullable=False
    )
    destino_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nodo.id"), nullable=True
    )
    toneladas: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    costo_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
