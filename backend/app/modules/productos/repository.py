from sqlmodel import Session, col, func, select

from app.core.base_repository import BaseRepository
from app.modules.productos.models import Producto


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session):
        super().__init__(Producto, session)

    def search(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        categoria_id: int | None = None,
        disponible: bool | None = None,
        solo_activos: bool = True,
    ) -> tuple[int, list[Producto]]:
        stmt = select(Producto)
        count_stmt = select(func.count()).select_from(Producto)

        if solo_activos:
            stmt = stmt.where(Producto.activo.is_(True))
            count_stmt = count_stmt.where(Producto.activo.is_(True))
        if search:
            like = f"%{search.lower()}%"
            stmt = stmt.where(func.lower(Producto.nombre).like(like))
            count_stmt = count_stmt.where(func.lower(Producto.nombre).like(like))
        if categoria_id is not None:
            stmt = stmt.where(Producto.categoria_id == categoria_id)
            count_stmt = count_stmt.where(Producto.categoria_id == categoria_id)
        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)
            count_stmt = count_stmt.where(Producto.disponible == disponible)

        total = self.session.exec(count_stmt).one()
        items = list(
            self.session.exec(
                stmt.order_by(col(Producto.id)).offset(skip).limit(limit)
            ).all()
        )
        return total, items
