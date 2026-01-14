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


def upgrade() -> None:
    # ========================================
    # Add snapshot columns to proforma table
    # ========================================
    
    # Company snapshot fields
    op.add_column('proforma', sa.Column('empresa_nombre_fantasia', sa.String(200), nullable=True))
    op.add_column('proforma', sa.Column('empresa_razon_social', sa.String(200), nullable=True))
    op.add_column('proforma', sa.Column('empresa_rut', sa.String(15), nullable=True))
    op.add_column('proforma', sa.Column('empresa_direccion', sa.String(200), nullable=True))
    op.add_column('proforma', sa.Column('empresa_giro', sa.String(200), nullable=True))
    
    # Billing address snapshot fields
    op.add_column('proforma', sa.Column('direccion_facturar_texto', sa.String(200), nullable=True))
    op.add_column('proforma', sa.Column('direccion_facturar_ciudad', sa.String(100), nullable=True))
    op.add_column('proforma', sa.Column('direccion_facturar_pais', sa.String(100), nullable=True))
    op.add_column('proforma', sa.Column('direccion_facturar_fono_1', sa.String(15), nullable=True))
    
    # Consignment address snapshot fields
    op.add_column('proforma', sa.Column('direccion_consignar_texto', sa.String(200), nullable=True))
    op.add_column('proforma', sa.Column('direccion_consignar_ciudad', sa.String(100), nullable=True))
    op.add_column('proforma', sa.Column('direccion_consignar_pais', sa.String(100), nullable=True))
    op.add_column('proforma', sa.Column('direccion_consignar_fono_1', sa.String(15), nullable=True))
    
    # Notification address snapshot fields
    op.add_column('proforma', sa.Column('direccion_notificar_texto', sa.String(200), nullable=True))
    op.add_column('proforma', sa.Column('direccion_notificar_ciudad', sa.String(100), nullable=True))
    op.add_column('proforma', sa.Column('direccion_notificar_pais', sa.String(100), nullable=True))
    op.add_column('proforma', sa.Column('direccion_notificar_fono_1', sa.String(15), nullable=True))
    
    # ================================================
    # Add snapshot columns to detalle_proforma table
    # ================================================
    
    # Product snapshot fields
    op.add_column('detalle_proforma', sa.Column('producto_nombre_esp', sa.String(100), nullable=True))
    op.add_column('detalle_proforma', sa.Column('producto_nombre_ing', sa.String(100), nullable=True))
    op.add_column('detalle_proforma', sa.Column('producto_obs_calidad', sa.String(2000), nullable=True))
    op.add_column('detalle_proforma', sa.Column('producto_especie', sa.String(100), nullable=True))
    
    # ========================================
    # Backfill existing records with current master data
    # ========================================
    
    # Backfill proforma empresa snapshots
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
    """)
    
    # Backfill proforma billing address snapshots
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
    """)
    
    # Backfill proforma consignment address snapshots
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
    """)
    
    # Backfill proforma notification address snapshots
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
    """)
    
    # Backfill detalle_proforma product snapshots
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
    """)


def downgrade() -> None:
    # Drop snapshot columns from detalle_proforma
    op.drop_column('detalle_proforma', 'producto_especie')
    op.drop_column('detalle_proforma', 'producto_obs_calidad')
    op.drop_column('detalle_proforma', 'producto_nombre_ing')
    op.drop_column('detalle_proforma', 'producto_nombre_esp')
    
    # Drop notification address snapshot columns from proforma
    op.drop_column('proforma', 'direccion_notificar_fono_1')
    op.drop_column('proforma', 'direccion_notificar_pais')
    op.drop_column('proforma', 'direccion_notificar_ciudad')
    op.drop_column('proforma', 'direccion_notificar_texto')
    
    # Drop consignment address snapshot columns from proforma
    op.drop_column('proforma', 'direccion_consignar_fono_1')
    op.drop_column('proforma', 'direccion_consignar_pais')
    op.drop_column('proforma', 'direccion_consignar_ciudad')
    op.drop_column('proforma', 'direccion_consignar_texto')
    
    # Drop billing address snapshot columns from proforma
    op.drop_column('proforma', 'direccion_facturar_fono_1')
    op.drop_column('proforma', 'direccion_facturar_pais')
    op.drop_column('proforma', 'direccion_facturar_ciudad')
    op.drop_column('proforma', 'direccion_facturar_texto')
    
    # Drop company snapshot columns from proforma
    op.drop_column('proforma', 'empresa_giro')
    op.drop_column('proforma', 'empresa_direccion')
    op.drop_column('proforma', 'empresa_rut')
    op.drop_column('proforma', 'empresa_razon_social')
    op.drop_column('proforma', 'empresa_nombre_fantasia')
