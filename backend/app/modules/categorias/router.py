from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import require_role
from app.modules.categorias import service as cat_service
from app.modules.categorias.schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.modules.categorias.service import CategoriaService, get_categoria_service
from app.modules.usuarios.schemas import UserPublic

router = APIRouter(prefix="/api/v1/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaRead])
def listar(service: Annotated[CategoriaService, Depends(get_categoria_service)]):
    return service.listar()


@router.get("/{id}", response_model=CategoriaRead)
def detalle(
    id: int,
    service: Annotated[CategoriaService, Depends(get_categoria_service)],
):
    try:
        return service.obtener(id)
    except cat_service.CategoriaNoEncontrada:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")


@router.post("", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear(
    data: CategoriaCreate,
    _admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    service: Annotated[CategoriaService, Depends(get_categoria_service)],
):
    try:
        return service.crear(data)
    except cat_service.NombreDuplicado:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre")


@router.put("/{id}", response_model=CategoriaRead)
def actualizar(
    id: int,
    data: CategoriaUpdate,
    _admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    service: Annotated[CategoriaService, Depends(get_categoria_service)],
):
    try:
        return service.actualizar(id, data)
    except cat_service.CategoriaNoEncontrada:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    except cat_service.NombreDuplicado:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    id: int,
    _admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    service: Annotated[CategoriaService, Depends(get_categoria_service)],
):
    try:
        service.eliminar(id)
    except cat_service.CategoriaNoEncontrada:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
