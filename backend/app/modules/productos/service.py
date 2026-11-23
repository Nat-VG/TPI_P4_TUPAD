from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.unit_of_work import UnitOfWork
from app.modules.categorias.schemas import CategoriaRead
from app.modules.productos.models import Producto
from app.modules.productos.schemas import (
    ProductoCreate,
    ProductoRead,
    ProductosPaginados,
    ProductoStockUpdate,
    ProductoUpdate,
)


class ProductoNoEncontrado(Exception):
    pass


class CategoriaNoEncontrada(Exception):
    pass


class ProductoService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def _to_read(self, producto: Producto) -> ProductoRead:
        data = ProductoRead.model_validate(producto)
        if producto.categoria is not None:
            data.categoria = CategoriaRead.model_validate(producto.categoria)
        return data

    def _cargar(self, uow: UnitOfWork, id: int) -> Producto | None:
        stmt = (
            select(Producto)
            .where(Producto.id == id)
            .options(selectinload(Producto.categoria))
        )
        return uow.session.exec(stmt).first()

    def listar(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        categoria_id: int | None = None,
        disponible: bool | None = None,
    ) -> ProductosPaginados:
        with self.uow as uow:
            total, items = uow.productos.search(
                skip=skip,
                limit=limit,
                search=search,
                categoria_id=categoria_id,
                disponible=disponible,
            )
            # Cargar categoría de cada ítem
            reads: list[ProductoRead] = []
            for p in items:
                full = self._cargar(uow, p.id)
                if full:
                    reads.append(self._to_read(full))
            return ProductosPaginados(total=total, items=reads)

    def obtener(self, id: int) -> ProductoRead:
        with self.uow as uow:
            producto = self._cargar(uow, id)
            if producto is None or not producto.activo:
                raise ProductoNoEncontrado()
            return self._to_read(producto)

    def _categoria_ok(self, uow: UnitOfWork, categoria_id: int) -> None:
        cat = uow.categorias.get_by_id(categoria_id)
        if cat is None or not cat.activo:
            raise CategoriaNoEncontrada()

    def crear(self, data: ProductoCreate) -> ProductoRead:
        with self.uow as uow:
            self._categoria_ok(uow, data.categoria_id)
            producto = Producto(**data.model_dump())
            creado = uow.productos.add(producto)
            full = self._cargar(uow, creado.id)
            return self._to_read(full)

    def actualizar(self, id: int, data: ProductoUpdate) -> ProductoRead:
        with self.uow as uow:
            producto = uow.productos.get_by_id(id)
            if producto is None or not producto.activo:
                raise ProductoNoEncontrado()
            changes = data.model_dump(exclude_unset=True)
            if "categoria_id" in changes:
                self._categoria_ok(uow, changes["categoria_id"])
            for key, value in changes.items():
                setattr(producto, key, value)
            uow.productos.update(producto)
            full = self._cargar(uow, id)
            return self._to_read(full)

    def actualizar_stock(self, id: int, data: ProductoStockUpdate) -> ProductoRead:
        with self.uow as uow:
            producto = uow.productos.get_by_id(id)
            if producto is None or not producto.activo:
                raise ProductoNoEncontrado()
            producto.stock = data.stock
            producto.disponible = data.disponible
            uow.productos.update(producto)
            full = self._cargar(uow, id)
            return self._to_read(full)

    def eliminar(self, id: int) -> None:
        with self.uow as uow:
            producto = uow.productos.get_by_id(id)
            if producto is None or not producto.activo:
                raise ProductoNoEncontrado()
            producto.activo = False
            uow.productos.update(producto)


def get_producto_service() -> ProductoService:
    from app.modules.productos.unit_of_work import ProductoUnitOfWork

    return ProductoService(ProductoUnitOfWork())
