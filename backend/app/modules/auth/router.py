from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.deps import get_current_active_user
from app.core.unit_of_work import UnitOfWork, get_uow
from app.modules.auth.service import AuthService
from app.modules.usuarios.schemas import UserCreate, UserPublic

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
):
    with uow:
        return AuthService(uow).register(user_in)


@router.post("/token")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    response: Response,
):
    with uow:
        token = AuthService(uow).authenticate(form_data.username, form_data.password)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,
    )
    return {"message": "Login exitoso"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"message": "Sesión cerrada"}


@router.get("/me", response_model=UserPublic)
def read_me(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    return current_user
