import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

DUAL_OFERTA = "DUAL_OFERTA"
DUAL_CAPACIDAD = "DUAL_CAPACIDAD"
HOLGURA_CAPACIDAD = "HOLGURA_CAPACIDAD"
COSTO_REDUCIDO = "COSTO_REDUCIDO"


class SensibilidadResultado(Base):
    __tablename__ = "sensibilidad_resultado"
    __table_args__ = (
        CheckConstraint("num_nonnulls(nodo_id, ruta_id) = 1", name="ck_sensibilidad_nodo_o_ruta"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    ejecucion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ejecucion.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    nodo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nodo.id"), nullable=True
    )
    ruta_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ruta.id"), nullable=True
    )
    valor: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    rango_inf: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    rango_sup: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
