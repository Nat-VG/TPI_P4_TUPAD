from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.productos.models import Producto


class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=100, unique=True, index=True)
    descripcion: str = Field(default="", max_length=255)
    activo: bool = Field(default=True)

    productos: list["Producto"] = Relationship(back_populates="categoria")
