from sqlmodel import Session

from app.core.database import engine
from app.modules.pedidos.repository import PedidoRepository
from app.modules.productos.repository import ProductoRepository


class PedidoUnitOfWork:
    """Misma sesión para pedidos y productos (descuento/restitución de stock)."""

    def __init__(self):
        self.session: Session | None = None

    def __enter__(self):
        self.session = Session(engine, expire_on_commit=False)
        self.pedidos = PedidoRepository(self.session)
        self.productos = ProductoRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.session is not None
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()


def get_pedido_uow() -> PedidoUnitOfWork:
    return PedidoUnitOfWork()
