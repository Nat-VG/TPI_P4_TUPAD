from sqlmodel import Session

from app.core.database import engine
from app.modules.categorias.repository import CategoriaRepository
from app.modules.productos.repository import ProductoRepository
from app.modules.usuarios.repository import UsuarioRepository


class UnitOfWork:
    """UoW base. Commit/rollback en __exit__. Los services no llaman commit."""

    def __init__(self):
        self.session: Session | None = None

    def __enter__(self):
        self.session = Session(engine, expire_on_commit=False)
        self.usuarios = UsuarioRepository(self.session)
        self.categorias = CategoriaRepository(self.session)
        self.productos = ProductoRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.session is not None
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()


def get_uow() -> UnitOfWork:
    return UnitOfWork()
