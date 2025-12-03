# Preparar el entorno

```bash
python -m venv venv
```

# activar el entorno virtual

```bash
source venv/bin/activate
```

# Instalar Dependencias

```bash
pip install -r requirements.txt
```

# Crear la base de datos en PostgreSQL

```sql
CREATE DATABASE pfidb1;
```

# Copiar el archivo .env.example y renombrarlo a .env

```bash
cp .env.example .env
```

# Iniciar el proyecto

```bash
uvicorn app.main:app --realod
```