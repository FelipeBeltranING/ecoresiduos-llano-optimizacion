from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "v2_ejecuciones"
down_revision: str | None = "v1_red_base"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLAS_V2 = ["ejecucion", "flujo_resultado", "sensibilidad_resultado", "convergencia_ag"]


# Tablas de ejecuciones y resultados de los motores
def upgrade() -> None:
    metodo = postgresql.ENUM("EXACTO", "GENETICO", name="metodo")

    op.create_table(
        "ejecucion",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("metodo", metodo, nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("costo_total", sa.Numeric(18, 2), nullable=True),
        sa.Column("tiempo_ms", sa.Numeric(12, 3), nullable=True),
        sa.Column("parametros", postgresql.JSONB(), nullable=True),
        sa.Column("snapshot_red", postgresql.JSONB(), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "flujo_resultado",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "ejecucion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ejecucion.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "origen_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodo.id"), nullable=False
        ),
        sa.Column(
            "destino_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodo.id"), nullable=True
        ),
        sa.Column("toneladas", sa.Numeric(12, 4), nullable=False),
        sa.Column("costo_unitario", sa.Numeric(14, 2), nullable=False),
        sa.CheckConstraint("toneladas >= 0", name="ck_flujo_toneladas_no_negativas"),
    )
    op.create_index("ix_flujo_resultado_ejecucion_id", "flujo_resultado", ["ejecucion_id"])

    op.create_table(
        "sensibilidad_resultado",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "ejecucion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ejecucion.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo", sa.String(40), nullable=False),
        sa.Column(
            "nodo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodo.id"), nullable=True
        ),
        sa.Column(
            "ruta_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ruta.id"), nullable=True
        ),
        sa.Column("valor", sa.Numeric(), nullable=False),
        sa.Column("rango_inf", sa.Numeric(), nullable=True),
        sa.Column("rango_sup", sa.Numeric(), nullable=True),
        sa.CheckConstraint(
            "num_nonnulls(nodo_id, ruta_id) = 1", name="ck_sensibilidad_nodo_o_ruta"
        ),
    )
    op.create_index(
        "ix_sensibilidad_resultado_ejecucion_id", "sensibilidad_resultado", ["ejecucion_id"]
    )

    op.create_table(
        "convergencia_ag",
        sa.Column(
            "ejecucion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ejecucion.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("generacion", sa.Integer(), primary_key=True),
        sa.Column("mejor_costo", sa.Numeric(18, 2), nullable=False),
        sa.Column("costo_promedio", sa.Numeric(18, 2), nullable=False),
        sa.CheckConstraint("generacion >= 0", name="ck_convergencia_generacion_no_negativa"),
    )

    # Seguridad a nivel de fila: cierra la API REST de Supabase
    for tabla in TABLAS_V2:
        op.execute(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY")


# Reversión de la migración
def downgrade() -> None:
    op.drop_table("convergencia_ag")
    op.drop_index("ix_sensibilidad_resultado_ejecucion_id", table_name="sensibilidad_resultado")
    op.drop_table("sensibilidad_resultado")
    op.drop_index("ix_flujo_resultado_ejecucion_id", table_name="flujo_resultado")
    op.drop_table("flujo_resultado")
    op.drop_table("ejecucion")
    op.execute("DROP TYPE IF EXISTS metodo")
