"""Replace id_bodega with servicio in orden_servicio

Revision ID: 003
Revises: 002
Create Date: 2026-05-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "orden_servicio"):
        return

    servicio_exists = _column_exists(bind, "orden_servicio", "servicio")
    id_bodega_exists = _column_exists(bind, "orden_servicio", "id_bodega")

    if not servicio_exists:
        op.add_column("orden_servicio", sa.Column("servicio", sa.String(length=120), nullable=True))

    if id_bodega_exists:
        # Backfill servicio from bodega name if possible.
        op.execute(
            """
            UPDATE orden_servicio os
            SET servicio = COALESCE(b.nombre, 'BODEGA_' || os.id_bodega::text)
            FROM bodega b
            WHERE os.id_bodega = b.id_bodega
              AND (os.servicio IS NULL OR btrim(os.servicio) = '')
            """
        )

        # Drop FK constraints tied to id_bodega, regardless of exact name.
        inspector = sa.inspect(bind)
        for fk in inspector.get_foreign_keys("orden_servicio"):
            constrained_cols = fk.get("constrained_columns") or []
            fk_name = fk.get("name")
            if constrained_cols == ["id_bodega"] and fk_name:
                op.drop_constraint(fk_name, "orden_servicio", type_="foreignkey")

        op.drop_column("orden_servicio", "id_bodega")

    # Ensure servicio is always present after migration.
    op.execute(
        """
        UPDATE orden_servicio
        SET servicio = 'SIN_DEFINIR'
        WHERE servicio IS NULL OR btrim(servicio) = ''
        """
    )
    op.alter_column("orden_servicio", "servicio", existing_type=sa.String(length=120), nullable=False)


def downgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "orden_servicio"):
        return

    if not _column_exists(bind, "orden_servicio", "id_bodega"):
        op.add_column("orden_servicio", sa.Column("id_bodega", sa.Integer(), nullable=True))

    if _table_exists(bind, "bodega"):
        op.create_foreign_key(
            "orden_servicio_id_bodega_fkey",
            "orden_servicio",
            "bodega",
            ["id_bodega"],
            ["id_bodega"],
        )

    if _column_exists(bind, "orden_servicio", "servicio"):
        op.drop_column("orden_servicio", "servicio")
