from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


# Tabla parametro_global: coeficientes del negocio
class ParametroGlobal(Base):
    __tablename__ = "parametro_global"

    clave: Mapped[str] = mapped_column(String(60), primary_key=True)
    valor: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    unidad: Mapped[str | None] = mapped_column(String(30), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(String(200), nullable=True)
