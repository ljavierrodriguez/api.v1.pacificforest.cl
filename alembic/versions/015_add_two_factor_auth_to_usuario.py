"""add two factor auth columns to usuario

Revision ID: 015_add_two_factor_auth_to_usuario
Revises: 014_improve_users_roles_and_seguridad
Create Date: 2026-11-11 11:38:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "015_add_two_factor_auth_to_usuario"
down_revision = "014_improve_users_roles_and_seguridad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE"
    )
    op.execute(
        "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS two_factor_secret VARCHAR(120)"
    )
    op.execute(
        "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS two_factor_backup_codes VARCHAR(1000)"
    )


def downgrade() -> None:
    op.drop_column("usuario", "two_factor_backup_codes")
    op.drop_column("usuario", "two_factor_secret")
    op.drop_column("usuario", "two_factor_enabled")

