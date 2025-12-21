from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic, Type
from math import ceil

T = TypeVar('T')


class PaginationInfo(BaseModel):
    page: int = Field(..., description="Número de página actual")
    page_size: int = Field(..., description="Tamaño de página")
    total_items: int = Field(..., description="Total de elementos")
    total_pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Indica si hay página siguiente")
    has_prev: bool = Field(..., description="Indica si hay página anterior")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="Lista de elementos")
    pagination: PaginationInfo = Field(..., description="Información de paginación")


def create_paginated_response_model(item_model: Type[BaseModel]) -> Type[PaginatedResponse]:
    """
    Crea un modelo de respuesta paginada específico para un tipo de elemento
    """
    class SpecificPaginatedResponse(PaginatedResponse[item_model]):
        pass
    
    # Establecer el nombre del modelo para la documentación
    SpecificPaginatedResponse.__name__ = f"PaginatedResponse{item_model.__name__}"
    
    return SpecificPaginatedResponse


def create_paginated_response(
    items: List[T], 
    page: int, 
    page_size: int, 
    total_items: int
) -> dict:
    """
    Crea una respuesta paginada con la estructura estándar
    """
    total_pages = ceil(total_items / page_size) if page_size > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
    }