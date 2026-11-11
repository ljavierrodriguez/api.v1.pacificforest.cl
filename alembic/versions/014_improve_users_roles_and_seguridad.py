"""Add rol to usuario and expand seguridad.modulo to VARCHAR(60)

Revision ID: 014
Revises: 013
Create Date: 2026-11-11 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "usuario"):
        if not _column_exists(bind, "usuario", "rol"):
            op.add_column(
                "usuario",
                sa.Column("rol", sa.String(length=50), nullable=False, server_default="PERSONALIZADO"),
            )

    if _table_exists(bind, "seguridad"):
        op.alter_column(
            "seguridad",
            "modulo",
            existing_type=sa.String(length=15),
            type_=sa.String(length=60),
            existing_nullable=False,
        )

    if _table_exists(bind, "usuario") and _table_exists(bind, "seguridad"):
        op.execute(
            sa.text(
                "UPDATE usuario SET rol = 'ADMINISTRADOR' "
                "WHERE (rol IS NULL OR rol = 'PERSONALIZADO') "
                "AND (LOWER(login) IN ('admin', 'administrador', 'lrodriguez') "
                "OR id_usuario IN (SELECT id_usuario FROM seguridad WHERE UPPER(modulo) IN ('SEGURIDAD', 'USUARIO') AND crear = TRUE))"
            )
        )


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "usuario") and _column_exists(bind, "usuario", "rol"):
        op.drop_column("usuario", "rol")

