from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)

if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_all_tables() -> None:
    import app.modules.categorias.models  # noqa: F401
    import app.modules.pedidos.models  # noqa: F401
    import app.modules.productos.models  # noqa: F401
    import app.modules.usuarios.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def session_factory() -> Session:
    return Session(engine, expire_on_commit=False)
