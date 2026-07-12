import os
from pathlib import Path

from app import create_app
from database import get_connection, init_db


def test_init_db_crea_tablas(tmp_path):
    db_path = tmp_path / "test_database.db"
    init_db(str(db_path))

    assert db_path.exists()
    conn = get_connection(str(db_path))
    tablas = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert {"libros", "ventas", "detalle_venta", "pedidos", "detalle_pedido"}.issubset(tablas)
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    conn.close()


def test_create_app_root_404_and_error(tmp_path):
    db_path = tmp_path / "test_app.db"
    app = create_app(db_path=str(db_path))

    @app.route("/ruta-error")
    def ruta_error():
        raise RuntimeError("boom")

    client = app.test_client()
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert b"<html" in respuesta.data.lower()

    respuesta_404 = client.get("/api/ruta-que-no-existe")
    assert respuesta_404.status_code == 404
    assert respuesta_404.get_json()["error"] == "Recurso no encontrado."

    respuesta_500 = client.get("/ruta-error")
    assert respuesta_500.status_code == 500
    assert respuesta_500.get_json()["error"] == "Error interno del servidor."
