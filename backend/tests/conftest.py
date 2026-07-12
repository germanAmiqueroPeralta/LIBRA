"""
conftest.py
Fixtures compartidas para pruebas unitarias e de integración.
Cada prueba usa una base de datos SQLite en memoria, aislada e independiente.
"""
import sys
import os

# Permite importar los módulos del backend (app, models, services, etc.)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import get_connection, init_db
from repositories.libro_repository import LibroRepository
from repositories.pedido_repository import PedidoRepository
from repositories.venta_repository import VentaRepository
from services.libro_service import LibroService
from services.venta_service import VentaService
from app import create_app


@pytest.fixture
def db_connection():
    """Conexión SQLite en memoria, con el esquema ya creado."""
    conn = get_connection(":memory:")
    _crear_esquema(conn)
    yield conn
    conn.close()


def _crear_esquema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            isbn TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            precio REAL NOT NULL CHECK (precio >= 0),
            stock INTEGER NOT NULL CHECK (stock >= 0),
            categoria TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS detalle_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            isbn TEXT NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas (id),
            FOREIGN KEY (isbn) REFERENCES libros (isbn)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL CHECK (estado IN ('pendiente', 'confirmado')),
            total REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS detalle_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            isbn TEXT NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
            FOREIGN KEY (isbn) REFERENCES libros (isbn)
        )
    """)
    conn.commit()


@pytest.fixture
def libro_repository(db_connection):
    return LibroRepository(db_connection)


@pytest.fixture
def pedido_repository(db_connection):
    return PedidoRepository(db_connection)


@pytest.fixture
def venta_repository(db_connection):
    return VentaRepository(db_connection)


@pytest.fixture
def libro_service(libro_repository):
    return LibroService(libro_repository)


@pytest.fixture
def venta_service(venta_repository, libro_repository):
    return VentaService(venta_repository, libro_repository)


@pytest.fixture
def libro_ejemplo():
    return {
        "isbn": "978-3-16-148410-0",
        "titulo": "Cien Años de Soledad",
        "autor": "Gabriel García Márquez",
        "precio": 45.90,
        "stock": 10,
        "categoria": "Novela",
    }


@pytest.fixture
def app_cliente(tmp_path):
    """Cliente de pruebas Flask, con base de datos temporal en disco."""
    db_path = str(tmp_path / "test_database.db")
    app = create_app(db_path=db_path)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
