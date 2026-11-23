"""
Carga datos iniciales. Se puede correr varias veces sin duplicar.

Uso:
    python -m app.db.seed
"""

from sqlmodel import Session, select

from app.core.database import create_all_tables, engine
from app.core.security import hash_password
from app.modules.categorias.models import Categoria
from app.modules.productos.models import Producto
from app.modules.usuarios.models import Usuario

ADMIN = {
    "username": "admin",
    "full_name": "Administrador Food Store",
    "email": "admin@foodstore.com",
    "password": "Admin1234!",
    "role": "admin",
}

CATEGORIAS = [
    ("Hamburguesas", "Clásicas, dobles y veggies"),
    ("Bebidas", "Gaseosas y aguas"),
    ("Acompañamientos", "Papas y nuggets"),
]

PRODUCTOS = [
    ("Hamburguesa Clásica", "Medallón, cheddar y lechuga", 8500, 1, 30),
    ("Hamburguesa Doble", "Doble medallón y cheddar", 11500, 1, 20),
    ("Hamburguesa Veggie", "Medallón de garbanzo", 9000, 1, 15),
    ("Coca-Cola 500ml", "Gaseosa", 2500, 2, 50),
    ("Agua 500ml", "Sin gas", 1800, 2, 40),
    ("Papas fritas", "Porción mediana", 3500, 3, 35),
    ("Aros de cebolla", "Porción", 4000, 3, 25),
    ("Nuggets x6", "Pollo crispy", 4500, 3, 28),
]


def run() -> None:
    print("=== Seed Food Store ===")
    create_all_tables()

    with Session(engine) as session:
        admin = session.exec(
            select(Usuario).where(Usuario.username == ADMIN["username"])
        ).first()
        if admin:
            print(f"  [=] Admin ya existe: {ADMIN['username']}")
        else:
            session.add(
                Usuario(
                    username=ADMIN["username"],
                    full_name=ADMIN["full_name"],
                    email=ADMIN["email"],
                    hashed_password=hash_password(ADMIN["password"]),
                    role=ADMIN["role"],
                )
            )
            print(f"  [+] Admin: {ADMIN['username']} / {ADMIN['password']}")

        cat_ids: dict[str, int] = {}
        for nombre, descripcion in CATEGORIAS:
            cat = session.exec(
                select(Categoria).where(Categoria.nombre == nombre)
            ).first()
            if cat:
                print(f"  [=] Categoría: {nombre}")
            else:
                cat = Categoria(nombre=nombre, descripcion=descripcion)
                session.add(cat)
                session.flush()
                print(f"  [+] Categoría: {nombre}")
            cat_ids[nombre] = cat.id

        # Mapear índice 1/2/3 del seed a nombres
        idx_a_nombre = {1: "Hamburguesas", 2: "Bebidas", 3: "Acompañamientos"}

        for nombre, descripcion, precio, cat_idx, stock in PRODUCTOS:
            existe = session.exec(
                select(Producto).where(Producto.nombre == nombre)
            ).first()
            if existe:
                print(f"  [=] Producto: {nombre}")
                continue
            session.add(
                Producto(
                    nombre=nombre,
                    descripcion=descripcion,
                    precio_base=precio,
                    imagen_url="",
                    stock=stock,
                    disponible=True,
                    categoria_id=cat_ids[idx_a_nombre[cat_idx]],
                )
            )
            print(f"  [+] Producto: {nombre} (stock={stock})")

        session.commit()

    print("\nListo. Admin: admin / Admin1234!")
    print()


if __name__ == "__main__":
    run()
