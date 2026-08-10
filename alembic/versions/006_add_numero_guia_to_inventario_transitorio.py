"""Add numero_guia to inventario_transitorio

Revision ID: 006
Revises: 005
Create Date: 2026-08-10 12:36:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    if not _column_exists(bind, "inventario_transitorio", "numero_guia"):
        op.add_column(
            "inventario_transitorio",
            sa.Column("numero_guia", sa.String(length=100), nullable=True)
        )


def downgrade() -> None:
    bind = op.get_bind()
    if _column_exists(bind, "inventario_transitorio", "numero_guia"):
        op.drop_column("inventario_transitorio", "numero_guia")
