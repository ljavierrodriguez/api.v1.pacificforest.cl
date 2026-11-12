"""Add two factor auth columns to usuario

Revision ID: 015
Revises: 014
Create Date: 2026-11-11 11:38:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "015"
down_revision = "014"
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
        if not _column_exists(bind, "usuario", "two_factor_enabled"):
            op.add_column(
                "usuario",
                sa.Column("two_factor_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            )
        if not _column_exists(bind, "usuario", "two_factor_secret"):
            op.add_column(
                "usuario",
                sa.Column("two_factor_secret", sa.String(length=120), nullable=True),
            )
        if not _column_exists(bind, "usuario", "two_factor_backup_codes"):
            op.add_column(
                "usuario",
                sa.Column("two_factor_backup_codes", sa.String(length=1000), nullable=True),
            )


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "usuario"):
        if _column_exists(bind, "usuario", "two_factor_backup_codes"):
            op.drop_column("usuario", "two_factor_backup_codes")
        if _column_exists(bind, "usuario", "two_factor_secret"):
            op.drop_column("usuario", "two_factor_secret")
        if _column_exists(bind, "usuario", "two_factor_enabled"):
            op.drop_column("usuario", "two_factor_enabled")
