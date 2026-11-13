from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "v1_red_base"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLAS_V1 = ["nodo", "ruta", "parametro_global"]


def upgrade() -> None:
    tipo_nodo = postgresql.ENUM("FUENTE", "ACOPIO", "PLANTA", name="tipo_nodo")

    op.create_table(
        "nodo",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("codigo", sa.String(10), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("tipo", tipo_nodo, nullable=False),
        sa.Column("municipio", sa.String(80), nullable=False),
        sa.Column("tipo_residuo", sa.String(60), nullable=True),
        sa.Column("oferta_t", sa.Numeric(12, 2), nullable=True),
        sa.Column("capacidad_t", sa.Numeric(12, 2), nullable=True),
        sa.Column(
            "costo_operacion_t", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")
        ),
        sa.Column("latitud", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitud", sa.Numeric(9, 6), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("codigo", name="uq_nodo_codigo"),
        sa.CheckConstraint("oferta_t >= 0", name="ck_nodo_oferta_no_negativa"),
        sa.CheckConstraint("capacidad_t > 0", name="ck_nodo_capacidad_positiva"),
        sa.CheckConstraint("costo_operacion_t >= 0", name="ck_nodo_costo_operacion_no_negativo"),
    )
    op.create_index("ix_nodo_tipo", "nodo", ["tipo"])

    op.create_table(
        "ruta",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "origen_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("nodo.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "destino_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("nodo.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("distancia_km", sa.Numeric(8, 2), nullable=True),
        sa.Column("costo_km_t", sa.Numeric(10, 2), nullable=True),
        sa.Column("habilitada", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("origen_id", "destino_id", name="uq_ruta_origen_destino"),
        sa.CheckConstraint("origen_id <> destino_id", name="ck_ruta_origen_distinto_destino"),
        sa.CheckConstraint("distancia_km > 0", name="ck_ruta_distancia_positiva"),
    )
    op.create_index("ix_ruta_destino_id", "ruta", ["destino_id"])

    tabla_parametros = op.create_table(
        "parametro_global",
        sa.Column("clave", sa.String(60), primary_key=True),
        sa.Column("valor", sa.Numeric(), nullable=False),
        sa.Column("unidad", sa.String(30), nullable=True),
        sa.Column("descripcion", sa.String(200), nullable=True),
    )

    op.bulk_insert(
        tabla_parametros,
        [
            {
                "clave": "costo_km_t",
                "valor": 350,
                "unidad": "COP/t·km",
                "descripcion": "Costo de transporte por tonelada-kilómetro (k)",
            },
            {
                "clave": "tarifa_recepcion_t",
                "valor": 0,
                "unidad": "COP/t",
                "descripcion": "Tarifa de recepción por tonelada",
            },
            {
                "clave": "penalizacion_ficticia",
                "valor": 1000000,
                "unidad": "COP/t",
                "descripcion": "Costo M por tonelada enviada a la planta ficticia",
            },
            {
                "clave": "lambda_ag",
                "valor": 1000000,
                "unidad": None,
                "descripcion": "Factor de penalización lambda del Algoritmo Genético",
            },
        ],
    )

    for tabla in TABLAS_V1:
        op.execute(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_table("parametro_global")
    op.drop_index("ix_ruta_destino_id", table_name="ruta")
    op.drop_table("ruta")
    op.drop_index("ix_nodo_tipo", table_name="nodo")
    op.drop_table("nodo")
    op.execute("DROP TYPE IF EXISTS tipo_nodo")
