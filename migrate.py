#!/usr/bin/env python3
"""
Script para ejecutar migraciones de Alembic
"""
import os
import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    """Ejecuta las migraciones de Alembic"""
    # Obtener el directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Configurar Alembic
    alembic_cfg = Config(os.path.join(current_dir, "alembic.ini"))
    
    try:
        print("🔄 Ejecutando migraciones de base de datos...")
        
        # Ejecutar upgrade a la última versión
        command.upgrade(alembic_cfg, "head")
        
        print("✅ Migraciones ejecutadas exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al ejecutar migraciones: {e}")
        sys.exit(1)

def create_migration(message: str):
    """Crea una nueva migración"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    alembic_cfg = Config(os.path.join(current_dir, "alembic.ini"))
    
    try:
        print(f"🔄 Creando migración: {message}")
        
        # Crear nueva migración con autogenerate
        command.revision(alembic_cfg, message=message, autogenerate=True)
        
        print("✅ Migración creada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al crear migración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "create" and len(sys.argv) > 2:
            create_migration(" ".join(sys.argv[2:]))
        else:
            print("Uso: python migrate.py [create <mensaje>]")
    else:
        run_migrations()