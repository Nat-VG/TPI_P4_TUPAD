from app.core.unit_of_work import UnitOfWork


class ProductoUnitOfWork(UnitOfWork):
    pass


def get_producto_uow() -> ProductoUnitOfWork:
    return ProductoUnitOfWork()
