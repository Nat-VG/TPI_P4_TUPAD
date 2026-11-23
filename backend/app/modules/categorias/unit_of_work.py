from app.core.unit_of_work import UnitOfWork


class CategoriaUnitOfWork(UnitOfWork):
    pass


def get_categoria_uow() -> CategoriaUnitOfWork:
    return CategoriaUnitOfWork()
