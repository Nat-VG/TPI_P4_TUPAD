from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.pedidos.models import Pedido


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    full_name: str = Field(max_length=120)
    email: str = Field(index=True, unique=True, max_length=254)
    hashed_password: str
    role: str = Field(default="user", max_length=20)
    disabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)

    pedidos: list["Pedido"] = Relationship(back_populates="usuario")
