from datetime import datetime, timezone

from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.modules.pedidos.models import (
    TRANSICIONES,
    DetallePedido,
    Pedido,
)
from app.modules.pedidos.schemas import (
    CambioEstado,
    DetallePedidoRead,
    PedidoCreate,
    PedidoRead,
    PedidosPaginados,
    ResumenPedidos,
)
from app.modules.pedidos.unit_of_work import PedidoUnitOfWork
from app.modules.usuarios.schemas import UserPublic


class PedidoNoEncontrado(Exception):
    pass


class ProductoNoEncontrado(Exception):
    pass


class ProductoNoDisponible(Exception):
    pass


class StockInsuficiente(Exception):
    pass


class ProductoRepetido(Exception):
    pass


class TransicionInvalida(Exception):
    pass


class PedidoAjeno(Exception):
    pass


class PedidoService:
    def __init__(self, uow: PedidoUnitOfWork):
        self.uow = uow

    def _cargar(self, uow: PedidoUnitOfWork, id: int) -> Pedido | None:
        stmt = (
            select(Pedido)
            .where(Pedido.id == id)
            .options(selectinload(Pedido.items))
        )
        return uow.session.exec(stmt).first()

    def _to_read(self, pedido: Pedido) -> PedidoRead:
        return PedidoRead(
            id=pedido.id,
            usuario_id=pedido.usuario_id,
            estado=pedido.estado,
            forma_pago=pedido.forma_pago,
            direccion_entrega=pedido.direccion_entrega,
            notas=pedido.notas,
            total=pedido.total,
            created_at=pedido.created_at,
            updated_at=pedido.updated_at,
            items=[
                DetallePedidoRead(
                    producto_id=i.producto_id,
                    nombre_producto=i.nombre_producto,
                    precio_unitario=i.precio_unitario,
                    cantidad=i.cantidad,
                    subtotal=i.subtotal,
                )
                for i in pedido.items
            ],
        )

    def crear(self, data: PedidoCreate, usuario: UserPublic) -> PedidoRead:
        ids = [item.producto_id for item in data.items]
        if len(ids) != len(set(ids)):
            raise ProductoRepetido()

        with self.uow as uow:
            pedido = Pedido(
                usuario_id=usuario.id,
                estado="PENDIENTE",
                forma_pago=data.forma_pago,
                direccion_entrega=data.direccion_entrega,
                notas=data.notas,
                total=0,
            )
            uow.pedidos.add(pedido)
            total = 0.0

            for item in data.items:
                producto = uow.productos.get_by_id(item.producto_id)
                if producto is None or not producto.activo:
                    raise ProductoNoEncontrado()
                if not producto.disponible:
                    raise ProductoNoDisponible()
                if producto.stock < item.cantidad:
                    raise StockInsuficiente()

                producto.stock -= item.cantidad
                uow.productos.update(producto)

                subtotal = round(producto.precio_base * item.cantidad, 2)
                detalle = DetallePedido(
                    pedido_id=pedido.id,
                    producto_id=producto.id,
                    cantidad=item.cantidad,
                    nombre_producto=producto.nombre,
                    precio_unitario=producto.precio_base,
                    subtotal=subtotal,
                )
                uow.session.add(detalle)
                total += subtotal

            pedido.total = round(total, 2)
            pedido.updated_at = datetime.now(timezone.utc)
            uow.session.flush()
            full = self._cargar(uow, pedido.id)
            return self._to_read(full)

    def listar(
        self,
        usuario: UserPublic,
        skip: int = 0,
        limit: int = 20,
        estado: str | None = None,
    ) -> PedidosPaginados:
        with self.uow as uow:
            filtro_usuario = None if usuario.role == "admin" else usuario.id
            total, items = uow.pedidos.list_by_usuario(
                filtro_usuario, skip=skip, limit=limit, estado=estado
            )
            reads = []
            for p in items:
                full = self._cargar(uow, p.id)
                if full:
                    reads.append(self._to_read(full))
            return PedidosPaginados(total=total, items=reads)

    def obtener(self, id: int, usuario: UserPublic) -> PedidoRead:
        with self.uow as uow:
            pedido = self._cargar(uow, id)
            if pedido is None:
                raise PedidoNoEncontrado()
            if usuario.role != "admin" and pedido.usuario_id != usuario.id:
                raise PedidoAjeno()
            return self._to_read(pedido)

    def _restituir_stock(self, uow: PedidoUnitOfWork, pedido: Pedido) -> None:
        for item in pedido.items:
            producto = uow.productos.get_by_id(item.producto_id)
            if producto is not None:
                producto.stock += item.cantidad
                uow.productos.update(producto)

    def cambiar_estado(
        self, id: int, data: CambioEstado, _admin: UserPublic
    ) -> PedidoRead:
        with self.uow as uow:
            pedido = self._cargar(uow, id)
            if pedido is None:
                raise PedidoNoEncontrado()
            permitidos = TRANSICIONES.get(pedido.estado, set())
            if data.estado not in permitidos:
                raise TransicionInvalida()
            if data.estado == "CANCELADO":
                self._restituir_stock(uow, pedido)
            pedido.estado = data.estado
            pedido.updated_at = datetime.now(timezone.utc)
            uow.session.add(pedido)
            uow.session.flush()
            full = self._cargar(uow, id)
            return self._to_read(full)

    def cancelar_propio(self, id: int, usuario: UserPublic) -> PedidoRead:
        with self.uow as uow:
            pedido = self._cargar(uow, id)
            if pedido is None:
                raise PedidoNoEncontrado()
            if pedido.usuario_id != usuario.id:
                raise PedidoAjeno()
            if pedido.estado != "PENDIENTE":
                raise TransicionInvalida()
            self._restituir_stock(uow, pedido)
            pedido.estado = "CANCELADO"
            pedido.updated_at = datetime.now(timezone.utc)
            uow.session.add(pedido)
            uow.session.flush()
            full = self._cargar(uow, id)
            return self._to_read(full)

    def resumen(self) -> ResumenPedidos:
        with self.uow as uow:
            data = uow.pedidos.resumen()
            return ResumenPedidos(**data)


def get_pedido_service() -> PedidoService:
    return PedidoService(PedidoUnitOfWork())
