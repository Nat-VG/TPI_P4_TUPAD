from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.productos.models import Producto
    from app.modules.usuarios.models import Usuario

ESTADOS = ("PENDIENTE", "EN_PREPARACION", "ENTREGADO", "CANCELADO")
ESTADOS_TERMINALES = ("ENTREGADO", "CANCELADO")
TRANSICIONES: dict[str, set[str]] = {
    "PENDIENTE": {"EN_PREPARACION", "CANCELADO"},
    "EN_PREPARACION": {"ENTREGADO", "CANCELADO"},
    "ENTREGADO": set(),
    "CANCELADO": set(),
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Pedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    estado: str = Field(default="PENDIENTE", max_length=20, index=True)
    forma_pago: str = Field(max_length=20)
    direccion_entrega: str = Field(min_length=5, max_length=200)
    notas: Optional[str] = Field(default=None, max_length=255)
    total: float = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    usuario: Optional["Usuario"] = Relationship(back_populates="pedidos")
    items: list["DetallePedido"] = Relationship(back_populates="pedido")


class DetallePedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    producto_id: int = Field(foreign_key="producto.id", index=True)
    cantidad: int = Field(ge=1)
    nombre_producto: str = Field(max_length=150)
    precio_unitario: float = Field(ge=0)
    subtotal: float = Field(ge=0)

    pedido: Optional[Pedido] = Relationship(back_populates="items")
    producto: Optional["Producto"] = Relationship(back_populates="detalles")
