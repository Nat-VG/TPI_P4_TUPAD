from datetime import datetime, timezone

from sqlmodel import Session, col, func, select

from app.core.base_repository import BaseRepository
from app.modules.pedidos.models import Pedido


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session):
        super().__init__(Pedido, session)

    def list_by_usuario(
        self,
        usuario_id: int | None,
        *,
        skip: int = 0,
        limit: int = 20,
        estado: str | None = None,
    ) -> tuple[int, list[Pedido]]:
        stmt = select(Pedido)
        count_stmt = select(func.count()).select_from(Pedido)
        if usuario_id is not None:
            stmt = stmt.where(Pedido.usuario_id == usuario_id)
            count_stmt = count_stmt.where(Pedido.usuario_id == usuario_id)
        if estado:
            stmt = stmt.where(Pedido.estado == estado)
            count_stmt = count_stmt.where(Pedido.estado == estado)
        total = self.session.exec(count_stmt).one()
        items = list(
            self.session.exec(
                stmt.order_by(col(Pedido.id).desc()).offset(skip).limit(limit)
            ).all()
        )
        return total, items

    def count_by_estado(self, estado: str) -> int:
        return self.session.exec(
            select(func.count()).select_from(Pedido).where(Pedido.estado == estado)
        ).one()

    def resumen(self) -> dict:
        hoy = datetime.now(timezone.utc).date()
        todos = list(self.session.exec(select(Pedido)).all())
        pedidos_hoy = 0
        for p in todos:
            created = p.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            if created.astimezone(timezone.utc).date() == hoy:
                pedidos_hoy += 1
        ingresos = self.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0.0)).where(
                Pedido.estado == "ENTREGADO"
            )
        ).one()
        return {
            "pendientes": self.count_by_estado("PENDIENTE"),
            "en_preparacion": self.count_by_estado("EN_PREPARACION"),
            "entregados": self.count_by_estado("ENTREGADO"),
            "cancelados": self.count_by_estado("CANCELADO"),
            "pedidos_hoy": pedidos_hoy,
            "ingresos_entregados": float(ingresos or 0),
        }
