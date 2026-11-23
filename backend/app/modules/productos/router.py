from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import require_role
from app.modules.productos import service as prod_service
from app.modules.productos.schemas import (
    ProductoCreate,
    ProductoRead,
    ProductosPaginados,
    ProductoStockUpdate,
    ProductoUpdate,
)
from app.modules.productos.service import ProductoService, get_producto_service
from app.modules.usuarios.schemas import UserPublic

router = APIRouter(prefix="/api/v1/productos", tags=["productos"])


@router.get("", response_model=ProductosPaginados)
def listar(
    service: Annotated[ProductoService, Depends(get_producto_service)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    categoria_id: Optional[int] = None,
    disponible: Optional[bool] = None,
):
    return service.listar(skip, limit, search, categoria_id, disponible)


@router.get("/{id}", response_model=ProductoRead)
def detalle(
    id: int,
    service: Annotated[ProductoService, Depends(get_producto_service)],
):
    try:
        return service.obtener(id)
    except prod_service.ProductoNoEncontrado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")


@router.post("", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear(
    data: ProductoCreate,
    _admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    service: Annotated[ProductoService, Depends(get_producto_service)],
):
    try:
        return service.crear(data)
    except prod_service.CategoriaNoEncontrada:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")


@router.put("/{id}", response_model=ProductoRead)
def actualizar(
    id: int,
    data: ProductoUpdate,
    _admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    service: Annotated[ProductoService, Depends(get_producto_service)],
):
    try:
        return service.actualizar(id, data)
    except prod_service.ProductoNoEncontrado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    except prod_service.CategoriaNoEncontrada:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")


@router.patch("/{id}/stock", response_model=ProductoRead)
def actualizar_stock(
    id: int,
    data: ProductoStockUpdate,
    _admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    service: Annotated[ProductoService, Depends(get_producto_service)],
):
    try:
        return service.actualizar_stock(id, data)
    except prod_service.ProductoNoEncontrado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    id: int,
    _admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    service: Annotated[ProductoService, Depends(get_producto_service)],
):
    try:
        service.eliminar(id)
    except prod_service.ProductoNoEncontrado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
