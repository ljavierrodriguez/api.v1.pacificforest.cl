from typing import Union
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import timedelta
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine_db
from app.core.security import create_access_token, get_current_user_from_cookie
from fastapi.templating import Jinja2Templates
from app.api.v1 import router

# Intentar crear tablas (si la base de datos no está accesible, ignorar durante import)
try:
    Base.metadata.create_all(bind=engine_db)
except Exception:
    # Evitar fallos durante import (bases no creadas, referencias circulares y similares).
    # En producción usar migraciones (Alembic) o crear tablas explícitamente.
    pass

# --- Usuario de ejemplo ---
fake_admin_user = {
    "username": "admin",
    "password": "4dM1nP@ssw0rd!",
    "role": "admin"
}

app = FastAPI(
    #docs_url=None,  # Cambia la ruta de Swagger UI
    redoc_url=None  # Cambia la ruta de ReDoc
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos: ["http://localhost:3000", "https://tudominio.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos: GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permite todos los headers, incluyendo Authorization
)

# Incluir las rutas de la versión 1 de la API
app.include_router(router, prefix="/api/v1")

templates = Jinja2Templates(directory="templates")

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_form(request: Request):
    user = get_current_user_from_cookie(request)
    if user:  # ya logueado
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", include_in_schema=False)
def login(username: str = Form(...), password: str = Form(...)):
    if username == fake_admin_user["username"] and password == fake_admin_user["password"]:
        token = create_access_token(
            data={"sub": username, "role": fake_admin_user["role"]},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
    return HTMLResponse("<h3>Usuario o contraseña incorrectos</h3>", status_code=401)

@app.get("/", include_in_schema=False)
def protected_redoc(request: Request):
    user = get_current_user_from_cookie(request)
    if not user or user["role"] != "admin":
        return RedirectResponse(url="/login")

    # Mostrar Redoc
    return get_redoc_html(openapi_url="/openapi.json", title="Mi API Docs")

@app.get("/openapi.json", include_in_schema=False)
def openapi(request: Request):
    user = get_current_user_from_cookie(request)
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    return get_openapi(title="Mi API", version="1.0.0", routes=app.routes)

# ----------------------------
# Logout
# ----------------------------
@app.get("/logout", include_in_schema=False)
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response