# Migraciones de Base de Datos

Este proyecto usa Alembic para manejar las migraciones de base de datos.

## Configuración Inicial

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
Asegúrate de que tu archivo `.env` tenga la configuración correcta de la base de datos.

## Ejecutar Migraciones

### Aplicar todas las migraciones pendientes:
```bash
python migrate.py
```

### Usando Alembic directamente:
```bash
# Aplicar migraciones
alembic upgrade head

# Ver historial de migraciones
alembic history

# Ver migración actual
alembic current

# Revertir a migración anterior
alembic downgrade -1
```

## Crear Nuevas Migraciones

### Crear migración automática (recomendado):
```bash
python migrate.py create "Descripción de los cambios"
```

### Crear migración manual:
```bash
alembic revision -m "Descripción de los cambios"
```

### Crear migración con autogenerate:
```bash
alembic revision --autogenerate -m "Descripción de los cambios"
```

## Migración Actual: Agregar id_forma_pago

La migración `001_add_id_forma_pago_to_proforma.py` agrega el campo `id_forma_pago` a la tabla `proforma`:

- **Agrega:** Columna `id_forma_pago` (INTEGER, nullable)
- **Agrega:** Foreign key constraint hacia `forma_pago.id_forma_pago`

### Para aplicar esta migración:
```bash
python migrate.py
```

### Para revertir esta migración:
```bash
alembic downgrade -1
```

## Estructura de Archivos

```
api.v1.pacificforest.cl/
├── alembic.ini                 # Configuración de Alembic
├── migrate.py                  # Script helper para migraciones
├── alembic/
│   ├── env.py                 # Configuración del entorno
│   ├── script.py.mako         # Template para nuevas migraciones
│   └── versions/              # Archivos de migración
│       └── 001_add_id_forma_pago_to_proforma.py
└── app/
    ├── models/                # Modelos SQLAlchemy
    └── db/                    # Configuración de base de datos
```

## Notas Importantes

- **Siempre hacer backup** de la base de datos antes de ejecutar migraciones en producción
- **Revisar las migraciones** generadas automáticamente antes de aplicarlas
- **Probar las migraciones** en un entorno de desarrollo primero
- **Las migraciones son irreversibles** en algunos casos, especialmente las que eliminan datos