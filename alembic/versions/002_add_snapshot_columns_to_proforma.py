"""Add snapshot columns to proforma and detalle_proforma tables

Revision ID: 002
Revises: 001
Create Date: 2025-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    if not _table_exists(bind, table_name):
        return False
    inspector = sa.inspect(bind)
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()

    def add_col_if_missing(table_name, col_name, col_type):
        if _table_exists(bind, table_name) and not _column_exists(bind, table_name, col_name):
            op.add_column(table_name, sa.Column(col_name, col_type, nullable=True))

    # Company snapshot fields
    add_col_if_missing('proforma', 'empresa_nombre_fantasia', sa.String(200))
    add_col_if_missing('proforma', 'empresa_razon_social', sa.String(200))
    add_col_if_missing('proforma', 'empresa_rut', sa.String(15))
    add_col_if_missing('proforma', 'empresa_direccion', sa.String(200))
    add_col_if_missing('proforma', 'empresa_giro', sa.String(200))
    
    # Billing address snapshot fields
    add_col_if_missing('proforma', 'direccion_facturar_texto', sa.String(200))
    add_col_if_missing('proforma', 'direccion_facturar_ciudad', sa.String(100))
    add_col_if_missing('proforma', 'direccion_facturar_pais', sa.String(100))
    add_col_if_missing('proforma', 'direccion_facturar_fono_1', sa.String(15))
    
    # Consignment address snapshot fields
    add_col_if_missing('proforma', 'direccion_consignar_texto', sa.String(200))
    add_col_if_missing('proforma', 'direccion_consignar_ciudad', sa.String(100))
    add_col_if_missing('proforma', 'direccion_consignar_pais', sa.String(100))
    add_col_if_missing('proforma', 'direccion_consignar_fono_1', sa.String(15))
    
    # Notification address snapshot fields
    add_col_if_missing('proforma', 'direccion_notificar_texto', sa.String(200))
    add_col_if_missing('proforma', 'direccion_notificar_ciudad', sa.String(100))
    add_col_if_missing('proforma', 'direccion_notificar_pais', sa.String(100))
    add_col_if_missing('proforma', 'direccion_notificar_fono_1', sa.String(15))
    
    # Product snapshot fields
    add_col_if_missing('detalle_proforma', 'producto_nombre_esp', sa.String(100))
    add_col_if_missing('detalle_proforma', 'producto_nombre_ing', sa.String(100))
    add_col_if_missing('detalle_proforma', 'producto_obs_calidad', sa.String(2000))
    add_col_if_missing('detalle_proforma', 'producto_especie', sa.String(100))
    
    # Backfill proforma empresa snapshots
    if _table_exists(bind, "proforma") and _table_exists(bind, "empresa"):
        op.execute("""
            UPDATE proforma p
            SET 
                empresa_nombre_fantasia = e.nombre_fantasia,
                empresa_razon_social = e.razon_social,
                empresa_rut = e.rut,
                empresa_direccion = e.direccion,
                empresa_giro = e.giro
            FROM empresa e
            WHERE p.id_empresa = e.id_empresa
              AND (p.empresa_nombre_fantasia IS NULL OR p.empresa_razon_social IS NULL)
        """)
    
    # Backfill proforma billing address snapshots
    if _table_exists(bind, "proforma") and _table_exists(bind, "direccion") and _table_exists(bind, "ciudad") and _table_exists(bind, "pais"):
        op.execute("""
            UPDATE proforma p
            SET 
                direccion_facturar_texto = d.direccion,
                direccion_facturar_ciudad = c.nombre,
                direccion_facturar_pais = pa.nombre,
                direccion_facturar_fono_1 = d.fono_1
            FROM direccion d
            JOIN ciudad c ON d.id_ciudad = c.id_ciudad
            JOIN pais pa ON c.id_pais = pa.id_pais
            WHERE p.id_direccion_facturar = d.id_direccion
              AND p.direccion_facturar_texto IS NULL
        """)
    
    # Backfill proforma consignment address snapshots
    if _table_exists(bind, "proforma") and _table_exists(bind, "direccion") and _table_exists(bind, "ciudad") and _table_exists(bind, "pais"):
        op.execute("""
            UPDATE proforma p
            SET 
                direccion_consignar_texto = d.direccion,
                direccion_consignar_ciudad = c.nombre,
                direccion_consignar_pais = pa.nombre,
                direccion_consignar_fono_1 = d.fono_1
            FROM direccion d
            JOIN ciudad c ON d.id_ciudad = c.id_ciudad
            JOIN pais pa ON c.id_pais = pa.id_pais
            WHERE p.id_direccion_consignar = d.id_direccion
              AND p.direccion_consignar_texto IS NULL
        """)
    
    # Backfill proforma notification address snapshots
    if _table_exists(bind, "proforma") and _table_exists(bind, "direccion") and _table_exists(bind, "ciudad") and _table_exists(bind, "pais"):
        op.execute("""
            UPDATE proforma p
            SET 
                direccion_notificar_texto = d.direccion,
                direccion_notificar_ciudad = c.nombre,
                direccion_notificar_pais = pa.nombre,
                direccion_notificar_fono_1 = d.fono_1
            FROM direccion d
            JOIN ciudad c ON d.id_ciudad = c.id_ciudad
            JOIN pais pa ON c.id_pais = pa.id_pais
            WHERE p.id_direccion_notificar = d.id_direccion
              AND p.direccion_notificar_texto IS NULL
        """)
    
    # Backfill detalle_proforma product snapshots
    if _table_exists(bind, "detalle_proforma") and _table_exists(bind, "producto"):
        op.execute("""
            UPDATE detalle_proforma dp
            SET 
                producto_nombre_esp = pr.nombre_producto_esp,
                producto_nombre_ing = pr.nombre_producto_ing,
                producto_obs_calidad = pr.obs_calidad,
                producto_especie = e.nombre_esp
            FROM producto pr
            LEFT JOIN especie e ON pr.id_especie = e.id_especie
            WHERE dp.id_producto = pr.id_producto
              AND dp.producto_nombre_esp IS NULL
        """)


def downgrade() -> None:
    bind = op.get_bind()

    def drop_col_if_exists(table_name, col_name):
        if _table_exists(bind, table_name) and _column_exists(bind, table_name, col_name):
            op.drop_column(table_name, col_name)

    drop_col_if_exists('detalle_proforma', 'producto_especie')
    drop_col_if_exists('detalle_proforma', 'producto_obs_calidad')
    drop_col_if_exists('detalle_proforma', 'producto_nombre_ing')
    drop_col_if_exists('detalle_proforma', 'producto_nombre_esp')
    
    drop_col_if_exists('proforma', 'direccion_notificar_fono_1')
    drop_col_if_exists('proforma', 'direccion_notificar_pais')
    drop_col_if_exists('proforma', 'direccion_notificar_ciudad')
    drop_col_if_exists('proforma', 'direccion_notificar_texto')
    
    drop_col_if_exists('proforma', 'direccion_consignar_fono_1')
    drop_col_if_exists('proforma', 'direccion_consignar_pais')
    drop_col_if_exists('proforma', 'direccion_consignar_ciudad')
    drop_col_if_exists('proforma', 'direccion_consignar_texto')
    
    drop_col_if_exists('proforma', 'direccion_facturar_fono_1')
    drop_col_if_exists('proforma', 'direccion_facturar_pais')
    drop_col_if_exists('proforma', 'direccion_facturar_ciudad')
    drop_col_if_exists('proforma', 'direccion_facturar_texto')
    
    drop_col_if_exists('proforma', 'empresa_giro')
    drop_col_if_exists('proforma', 'empresa_direccion')
    drop_col_if_exists('proforma', 'empresa_rut')
    drop_col_if_exists('proforma', 'empresa_razon_social')
    drop_col_if_exists('proforma', 'empresa_nombre_fantasia')

