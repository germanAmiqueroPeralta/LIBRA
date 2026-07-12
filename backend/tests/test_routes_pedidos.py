from models.libro import Libro
from routes import auth as auth_module


def _login_admin(app_cliente, monkeypatch):
    monkeypatch.setattr(
        auth_module,
        "USERS",
        {"admin": {"username": "admin", "password": "admin123", "role": "admin"}},
        raising=True,
    )
    respuesta = app_cliente.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert respuesta.status_code == 200


def test_create_and_confirm_pedido_via_api(app_cliente, libro_ejemplo, monkeypatch):
    _login_admin(app_cliente, monkeypatch)
    respuesta_libro = app_cliente.post("/api/libros", json=libro_ejemplo)
    assert respuesta_libro.status_code == 201

    datos_pedido = {
        "cliente": "Juliana",
        "items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 3}],
    }
    respuesta = app_cliente.post("/api/pedidos", json=datos_pedido)
    assert respuesta.status_code == 201
    pedido = respuesta.get_json()
    assert pedido["estado"] == "pendiente"
    assert pedido["total"] == 3 * libro_ejemplo["precio"]

    respuesta_listar = app_cliente.get("/api/pedidos?estado=pendiente")
    assert respuesta_listar.status_code == 200
    pedidos = respuesta_listar.get_json()
    assert len(pedidos) == 1
    assert pedidos[0]["cliente"] == "Juliana"

    respuesta_confirmar = app_cliente.post(f"/api/pedidos/{pedido['id']}/confirmar")
    assert respuesta_confirmar.status_code == 200
    pedido_confirmado = respuesta_confirmar.get_json()
    assert pedido_confirmado["estado"] == "confirmado"

    respuesta_libro_get = app_cliente.get(f"/api/libros/{libro_ejemplo['isbn']}")
    assert respuesta_libro_get.status_code == 200
    assert respuesta_libro_get.get_json()["stock"] == libro_ejemplo["stock"] - 3


def test_list_pedidos_with_invalid_estado_returns_400(app_cliente, monkeypatch):
    _login_admin(app_cliente, monkeypatch)
    respuesta = app_cliente.get("/api/pedidos?estado=invalido")
    assert respuesta.status_code == 400
    assert "error" in respuesta.get_json()


def test_confirm_nonexistent_pedido_returns_400(app_cliente, monkeypatch):
    _login_admin(app_cliente, monkeypatch)
    respuesta = app_cliente.post("/api/pedidos/9999/confirmar")
    assert respuesta.status_code == 400
    assert "error" in respuesta.get_json()
