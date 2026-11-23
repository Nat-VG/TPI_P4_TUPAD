from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import require_role
from app.core.unit_of_work import UnitOfWork, get_uow
from app.modules.usuarios.schemas import UserPublic
from app.modules.usuarios.service import UsuarioService

router = APIRouter(prefix="/api/v1/auth/admin/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UserPublic])
def list_users(
    _admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
):
    with uow:
        return UsuarioService(uow).list_all()


@router.post("/{user_id}/activar", response_model=UserPublic)
def activate_user(
    user_id: int,
    admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
):
    with uow:
        return UsuarioService(uow).set_disabled(
            user_id, disabled=False, admin_id=admin.id
        )


@router.post("/{user_id}/desactivar", response_model=UserPublic)
def deactivate_user(
    user_id: int,
    admin: Annotated[UserPublic, Depends(require_role(["admin"]))],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
):
    with uow:
        return UsuarioService(uow).set_disabled(
            user_id, disabled=True, admin_id=admin.id
        )
