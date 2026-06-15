"""Refactor packing list to support multiple dispatch guides

Revision ID: 005
Revises: 004
Create Date: 2026-06-11 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def _fk_exists(bind, table_name: str, fk_name: str) -> bool:
    inspector = sa.inspect(bind)
    return any((fk.get("name") == fk_name) for fk in inspector.get_foreign_keys(table_name))


def upgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "packing_lists"):
        return

    if not _table_exists(bind, "packing_list_guias"):
        op.create_table(
            "packing_list_guias",
            sa.Column("id_packing_list_guia", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "id_packing_list",
                sa.Integer(),
                sa.ForeignKey("packing_lists.id_packing_list", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("guia_despacho", sa.String(length=100), nullable=False),
            sa.Column("fecha_despacho", sa.Date(), nullable=False),
            sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
        )
        op.create_index(
            "ix_packing_list_guias_id_packing_list",
            "packing_list_guias",
            ["id_packing_list"],
        )

    if _table_exists(bind, "packing_list_detalles") and not _column_exists(
        bind,
        "packing_list_detalles",
        "id_packing_list_guia",
    ):
        op.add_column(
            "packing_list_detalles",
            sa.Column("id_packing_list_guia", sa.Integer(), nullable=True),
        )

    if _table_exists(bind, "packing_list_detalles") and not _fk_exists(
        bind,
        "packing_list_detalles",
        "fk_packing_list_detalles_guia",
    ):
        op.create_foreign_key(
            "fk_packing_list_detalles_guia",
            "packing_list_detalles",
            "packing_list_guias",
            ["id_packing_list_guia"],
            ["id_packing_list_guia"],
            ondelete="CASCADE",
        )

    # 1) Create one default guide for each existing packing list.
    op.execute(
        """
        INSERT INTO packing_list_guias (id_packing_list, guia_despacho, fecha_despacho, orden)
        SELECT
            pl.id_packing_list,
            COALESCE(NULLIF(BTRIM(pl.guia_despacho), ''), 'SIN GUIA'),
            COALESCE(pl.fecha_despacho, CURRENT_DATE),
            0
        FROM packing_lists pl
        WHERE NOT EXISTS (
            SELECT 1
            FROM packing_list_guias g
            WHERE g.id_packing_list = pl.id_packing_list
        )
        """
    )

    # 2) Re-assign all existing details to the created guide.
    op.execute(
        """
        UPDATE packing_list_detalles d
        SET id_packing_list_guia = g.id_packing_list_guia
        FROM packing_list_guias g
        WHERE d.packing_list_id = g.id_packing_list
          AND d.id_packing_list_guia IS NULL
        """
    )

    # 3) Enforce NOT NULL once data is populated.
    if _table_exists(bind, "packing_list_detalles") and _column_exists(
        bind,
        "packing_list_detalles",
        "id_packing_list_guia",
    ):
        op.alter_column(
            "packing_list_detalles",
            "id_packing_list_guia",
            existing_type=sa.Integer(),
            nullable=False,
        )

    # 4) Drop old guide columns from packing list header.
    if _column_exists(bind, "packing_lists", "guia_despacho"):
        op.drop_column("packing_lists", "guia_despacho")

    if _column_exists(bind, "packing_lists", "fecha_despacho"):
        op.drop_column("packing_lists", "fecha_despacho")


def downgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "packing_lists"):
        return

    if not _column_exists(bind, "packing_lists", "guia_despacho"):
        op.add_column("packing_lists", sa.Column("guia_despacho", sa.String(length=100), nullable=True))

    if not _column_exists(bind, "packing_lists", "fecha_despacho"):
        op.add_column("packing_lists", sa.Column("fecha_despacho", sa.Date(), nullable=True))

    # Restore legacy guide fields from the first guide available.
    op.execute(
        """
        WITH first_guide AS (
            SELECT DISTINCT ON (g.id_packing_list)
                g.id_packing_list,
                g.guia_despacho,
                g.fecha_despacho
            FROM packing_list_guias g
            ORDER BY g.id_packing_list, g.orden, g.id_packing_list_guia
        )
        UPDATE packing_lists pl
        SET guia_despacho = fg.guia_despacho,
            fecha_despacho = fg.fecha_despacho
        FROM first_guide fg
        WHERE pl.id_packing_list = fg.id_packing_list
        """
    )

    if _table_exists(bind, "packing_list_detalles") and _column_exists(
        bind,
        "packing_list_detalles",
        "id_packing_list_guia",
    ):
        if _fk_exists(bind, "packing_list_detalles", "fk_packing_list_detalles_guia"):
            op.drop_constraint("fk_packing_list_detalles_guia", "packing_list_detalles", type_="foreignkey")

        op.drop_column("packing_list_detalles", "id_packing_list_guia")

    if _table_exists(bind, "packing_list_guias"):
        op.drop_index("ix_packing_list_guias_id_packing_list", table_name="packing_list_guias")
        op.drop_table("packing_list_guias")
