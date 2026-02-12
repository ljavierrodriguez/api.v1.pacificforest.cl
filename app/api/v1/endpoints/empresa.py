from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
import base64
import os
import shutil
from datetime import datetime

from app.db.session import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaRead, EmpresaUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para Empresa
PaginatedEmpresaResponse = create_paginated_response_model(EmpresaRead)

router = APIRouter(prefix="/empresa", tags=["empresa"])


def _save_logo_file(file: UploadFile, item_id: int) -> str:
    # Validar que sea una imagen
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Crear directorio si no existe
    upload_dir = os.path.join(os.getcwd(), "app", "static", "logos")
    os.makedirs(upload_dir, exist_ok=True)

    # Generar nombre unico para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".png"
    filename = f"empresa_{item_id}_{timestamp}{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    # Guardar el archivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Ruta corta para BD (<= 100 chars)
    return f"/static/logos/{filename}"


def _logo_with_base(url_logo: str | None, base_url: str) -> str | None:
    if not url_logo:
        return url_logo
    if url_logo.startswith("http://") or url_logo.startswith("https://"):
        return url_logo
    if url_logo.startswith("/"):
        return base_url.rstrip("/") + url_logo
    return url_logo


def _is_data_url(value: str | None) -> bool:
    return isinstance(value, str) and value.startswith("data:image/")


def _save_logo_data_url(data_url: str, item_id: int) -> str:
    try:
        header, encoded = data_url.split(",", 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Logo en formato base64 invalido")

    if ";base64" not in header:
        raise HTTPException(status_code=400, detail="Logo en formato base64 invalido")

    mime = header.split(";", 1)[0].replace("data:", "")
    ext = ".png"
    if mime == "image/jpeg":
        ext = ".jpg"
    elif mime == "image/webp":
        ext = ".webp"
    elif mime == "image/gif":
        ext = ".gif"

    upload_dir = os.path.join(os.getcwd(), "app", "static", "logos")
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"empresa_{item_id}_{timestamp}{ext}"
    file_path = os.path.join(upload_dir, filename)

    try:
        decoded = base64.b64decode(encoded)
    except Exception:
        raise HTTPException(status_code=400, detail="Logo en formato base64 invalido")

    with open(file_path, "wb") as buffer:
        buffer.write(decoded)

    return f"/static/logos/{filename}"


@router.post("/", response_model=EmpresaRead, summary="POST Empresa", description="Crear una empresa y opcionalmente subir el logo.")
async def create_empresa(request: Request, db: Session = Depends(get_db)):
    def _to_bool(value: str | bool | None, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "t", "yes", "y", "on")

    def _to_int(value: str | int | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        try:
            return int(str(value))
        except ValueError:
            return None

    content_type = (request.headers.get("content-type") or "").lower()
    data: dict = {}
    file: UploadFile | None = None

    if "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        data = dict(form)
        file_value = form.get("file")
        if isinstance(file_value, UploadFile):
            file = file_value
    else:
        try:
            data = await request.json()
        except Exception:
            data = {}

    rut = data.get("rut")
    nombre_fantasia = data.get("nombre_fantasia")
    razon_social = data.get("razon_social")
    direccion = data.get("direccion")
    id_ciudad = _to_int(data.get("id_ciudad"))

    if not rut or not nombre_fantasia or not razon_social or not direccion or id_ciudad is None:
        raise HTTPException(status_code=422, detail="Faltan campos obligatorios")

    telefono_1 = data.get("telefono_1")
    telefono_2 = data.get("telefono_2")
    giro = data.get("giro")
    es_vigente = _to_bool(data.get("es_vigente"), True)
    en_proforma = _to_bool(data.get("en_proforma"), False)
    en_odc = _to_bool(data.get("en_odc"), False)
    por_defecto = _to_bool(data.get("por_defecto"), False)
    url_logo = data.get("url_logo")

    logo_data_url = url_logo if _is_data_url(url_logo) else None
    obj = Empresa(
        rut=rut,
        nombre_fantasia=nombre_fantasia,
        razon_social=razon_social,
        direccion=direccion,
        telefono_1=telefono_1,
        telefono_2=telefono_2,
        giro=giro,
        id_ciudad=id_ciudad,
        es_vigente=es_vigente,
        en_proforma=en_proforma,
        en_odc=en_odc,
        por_defecto=por_defecto,
        url_logo="" if logo_data_url else (url_logo or ""),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    if file:
        url_logo_saved = _save_logo_file(file, obj.id_empresa)
        obj.url_logo = url_logo_saved
        db.add(obj)
        db.commit()
        db.refresh(obj)
    elif logo_data_url:
        url_logo_saved = _save_logo_data_url(logo_data_url, obj.id_empresa)
        obj.url_logo = url_logo_saved
        db.add(obj)
        db.commit()
        db.refresh(obj)

    obj.url_logo = _logo_with_base(obj.url_logo, str(request.base_url))
    return obj


@router.get("/", response_model=PaginatedEmpresaResponse, summary='GET Empresas', description='Obtener lista paginada de empresas.')
def list_empresa(
    request: Request,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Empresa).count()
    
    # Obtener elementos de la página actual
    items = db.query(Empresa).offset(skip).limit(page_size).all()
    base_url = str(request.base_url)
    for item in items:
        item.url_logo = _logo_with_base(item.url_logo, base_url)
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=EmpresaRead, summary='GET Empresa', description='Obtener una empresa específica por su ID.')
def get_empresa(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")
    item.url_logo = _logo_with_base(item.url_logo, str(request.base_url))
    return item


@router.put("/{item_id}", response_model=EmpresaRead, summary='PUT Empresa', description='Actualizar una empresa existente.')
def update_empresa(item_id: int, payload: EmpresaUpdate, request: Request, db: Session = Depends(get_db)):
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")
    data = payload.model_dump(exclude_unset=True)
    if "url_logo" in data and _is_data_url(data["url_logo"]):
        data["url_logo"] = _save_logo_data_url(data["url_logo"], item_id)
    for k, v in data.items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    item.url_logo = _logo_with_base(item.url_logo, str(request.base_url))
    return item


@router.delete("/{item_id}", summary='DELETE Empresa', description='Eliminar una empresa por su ID.')
def delete_empresa(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")
    
    # No permitir eliminar la empresa por defecto
    if item.por_defecto:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar la empresa por defecto"
        )
    
    # Verificar si tiene proformas asociadas (necesito importar el modelo)
    from app.models.proforma import Proforma
    proformas_count = db.query(Proforma).filter(Proforma.id_empresa == item_id).count()
    
    if proformas_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la empresa porque tiene {proformas_count} proforma(s) asociada(s)"
        )
    
    db.delete(item)
    db.commit()
    return {"ok": True}


@router.post("/{item_id}/logo", summary="Subir logo de la empresa", description="Sube el logo y actualiza url_logo con la ruta corta.")
def upload_logo_empresa(item_id: int, file: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db)):
    # Verificar que la empresa existe
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")

    url_logo = _save_logo_file(file, item_id)
    item.url_logo = url_logo
    db.add(item)
    db.commit()
    db.refresh(item)

    if request:
        url_logo = _logo_with_base(url_logo, str(request.base_url))
    return {"url_logo": url_logo, "message": "Logo subido exitosamente"}
