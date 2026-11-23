from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import get_current_active_user, require_role
from app.modules.pedidos import service as ped_service
from app.modules.pedidos.schemas import (
    CambioEstado,
    PedidoCreate,
    PedidoRead,
    PedidosPaginados,
    ResumenPedidos,
)
from app.modules.pedidos.service import PedidoService, get_pedido_service
from app.modules.usuarios.schemas import UserPublic

router = APIRouter(prefix="/api/v1/pedidos", tags=["pedidos"])


def _map_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ped_service.PedidoNoEncontrado):
        return HTTPException(status_code=404, detail="Pedido no encontrado")
    if isinstance(exc, ped_service.ProductoNoEncontrado):
        return HTTPException(status_code=404, detail="Producto no encontrado")
    if isinstance(exc, ped_service.PedidoAjeno):
        return HTTPException(status_code=403, detail="No podés acceder a este pedido")
    if isinstance(exc, ped_service.StockInsuficiente):
        return HTTPException(status_code=400, detail="Stock insuficiente")
    if isinstance(exc, ped_service.ProductoNoDisponible):
        return HTTPException(status_code=400, detail="Producto no disponible")
    if isinstance(exc, ped_service.ProductoRepetido):
        return HTTPException(status_code=400, detail="Hay productos repetidos en el pedido")
    if isinstance(exc, ped_service.TransicionInvalida):
        return HTTPException(status_code=400, detail="Transición de estado inválida")
    return HTTPException(status_code=400, detail=str(exc))


@router.post("", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear(
    data: PedidoCreate,
    user: Annotated[UserPublic, Depends(get_current_active_user)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
):
    try:
        return service.crear(data, user)
    except Exception as e:
        if type(e).__module__.endswith("pedidos.service"):
            raise _map_error(e)
        raise


@router.get("", response_model=PedidosPaginados)
def listar(
    user: Annotated[UserPublic, Depends(get_current_active_user)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    estado: Optional[str] = None,
):
    return service.listar(user, skip, limit, estado)


@router.get("/resumen", response_model=ResumenPedidos)
def resumen(
    _admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
):
    return service.resumen()


@router.get("/{id}", response_model=PedidoRead)
def detalle(
    id: int,
    user: Annotated[UserPublic, Depends(get_current_active_user)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
):
    try:
        return service.obtener(id, user)
    except Exception as e:
        if type(e).__module__.endswith("pedidos.service"):
            raise _map_error(e)
        raise


@router.patch("/{id}/estado", response_model=PedidoRead)
def cambiar_estado(
    id: int,
    data: CambioEstado,
    admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
):
    try:
        return service.cambiar_estado(id, data, admin)
    except Exception as e:
        if type(e).__module__.endswith("pedidos.service"):
            raise _map_error(e)
        raise


@router.patch("/{id}/cancelar", response_model=PedidoRead)
def cancelar(
    id: int,
    user: Annotated[UserPublic, Depends(get_current_active_user)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
):
    try:
        return service.cancelar_propio(id, user)
    except Exception as e:
        if type(e).__module__.endswith("pedidos.service"):
            raise _map_error(e)
        raise
