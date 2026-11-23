from app.core.unit_of_work import UnitOfWork
from app.modules.categorias.models import Categoria
from app.modules.categorias.schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate


class CategoriaNoEncontrada(Exception):
    pass


class NombreDuplicado(Exception):
    pass


class CategoriaService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def listar(self) -> list[CategoriaRead]:
        with self.uow as uow:
            return [
                CategoriaRead.model_validate(c) for c in uow.categorias.list_activas()
            ]

    def obtener(self, id: int) -> CategoriaRead:
        with self.uow as uow:
            cat = uow.categorias.get_by_id(id)
            if cat is None or not cat.activo:
                raise CategoriaNoEncontrada()
            return CategoriaRead.model_validate(cat)

    def crear(self, data: CategoriaCreate) -> CategoriaRead:
        with self.uow as uow:
            if uow.categorias.get_by_nombre(data.nombre):
                raise NombreDuplicado()
            cat = Categoria(nombre=data.nombre, descripcion=data.descripcion)
            return CategoriaRead.model_validate(uow.categorias.add(cat))

    def actualizar(self, id: int, data: CategoriaUpdate) -> CategoriaRead:
        with self.uow as uow:
            cat = uow.categorias.get_by_id(id)
            if cat is None or not cat.activo:
                raise CategoriaNoEncontrada()
            if data.nombre is not None and data.nombre != cat.nombre:
                otro = uow.categorias.get_by_nombre(data.nombre)
                if otro and otro.id != cat.id:
                    raise NombreDuplicado()
                cat.nombre = data.nombre
            if data.descripcion is not None:
                cat.descripcion = data.descripcion
            return CategoriaRead.model_validate(uow.categorias.update(cat))

    def eliminar(self, id: int) -> None:
        with self.uow as uow:
            cat = uow.categorias.get_by_id(id)
            if cat is None or not cat.activo:
                raise CategoriaNoEncontrada()
            cat.activo = False
            uow.categorias.update(cat)
            # Baja también los productos de la categoría
            for producto in list(cat.productos):
                if producto.activo:
                    producto.activo = False
                    uow.productos.update(producto)


def get_categoria_service() -> CategoriaService:
    from app.modules.categorias.unit_of_work import CategoriaUnitOfWork

    return CategoriaService(CategoriaUnitOfWork())
