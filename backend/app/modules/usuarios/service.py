from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.core.unit_of_work import UnitOfWork
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import Token, UserCreate, UserPublic


class UsuarioService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def register(self, user_in: UserCreate) -> UserPublic:
        if self.uow.usuarios.get_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está en uso",
            )
        if self.uow.usuarios.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado",
            )
        usuario = Usuario(
            username=user_in.username,
            full_name=user_in.full_name,
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            role="user",
        )
        return UserPublic.model_validate(self.uow.usuarios.add(usuario))

    def authenticate(self, username: str, password: str) -> Token:
        user = self.uow.usuarios.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cuenta de usuario desactivada",
            )
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def list_all(self) -> list[UserPublic]:
        return [UserPublic.model_validate(u) for u in self.uow.usuarios.get_all()]

    def set_disabled(
        self, user_id: int, disabled: bool, admin_id: int
    ) -> UserPublic:
        user = self.uow.usuarios.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        if disabled and user.id == admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No podés desactivar tu propia cuenta",
            )
        user.disabled = disabled
        return UserPublic.model_validate(self.uow.usuarios.update(user))
