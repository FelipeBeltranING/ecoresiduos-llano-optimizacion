from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "v4_rutas_reales"
down_revision: str | None = "v3_escenarios_analisis"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("ruta", sa.Column("geometria", sa.Text(), nullable=True))
    op.add_column("ruta", sa.Column("duracion_min", sa.Numeric(8, 1), nullable=True))
    op.add_column("ruta", sa.Column("fuente_distancia", sa.String(12), nullable=True))


def downgrade() -> None:
    op.drop_column("ruta", "fuente_distancia")
    op.drop_column("ruta", "duracion_min")
    op.drop_column("ruta", "geometria")
