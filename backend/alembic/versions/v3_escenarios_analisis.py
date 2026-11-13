from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "v3_escenarios_analisis"
down_revision: str | None = "v2_ejecuciones"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLAS_V3 = ["escenario", "analisis"]


def upgrade() -> None:
    op.create_table(
        "escenario",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("descripcion", sa.String(400), nullable=True),
        sa.Column("ajustes", postgresql.JSONB(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    op.create_table(
        "analisis",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column(
            "escenario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("escenario.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("parametros", postgresql.JSONB(), nullable=True),
        sa.Column("resultado", postgresql.JSONB(), nullable=True),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_analisis_tipo", "analisis", ["tipo"])

    op.add_column(
        "ejecucion",
        sa.Column(
            "escenario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("escenario.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column("ejecucion", sa.Column("violaciones", sa.Numeric(18, 6), nullable=True))
    op.create_index("ix_ejecucion_creado_en", "ejecucion", ["creado_en"])

    for tabla in TABLAS_V3:
        op.execute(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_index("ix_ejecucion_creado_en", table_name="ejecucion")
    op.drop_column("ejecucion", "violaciones")
    op.drop_column("ejecucion", "escenario_id")
    op.drop_index("ix_analisis_tipo", table_name="analisis")
    op.drop_table("analisis")
    op.drop_table("escenario")
