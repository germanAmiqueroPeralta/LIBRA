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


def test_registrar_venta_y_obtenerla_via_api(app_cliente, libro_ejemplo, monkeypatch):
    _login_admin(app_cliente, monkeypatch)
    app_cliente.post("/api/libros", json=libro_ejemplo)

    respuesta = app_cliente.post(
        "/api/ventas",
        json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 2}]},
    )
    assert respuesta.status_code == 201
    data = respuesta.get_json()
    assert data["total"] == libro_ejemplo["precio"] * 2

    respuesta_get = app_cliente.get(f"/api/ventas/{data['id']}")
    assert respuesta_get.status_code == 200
    assert respuesta_get.get_json()["id"] == data["id"]


def test_total_vendido_periodo_invalido_via_api(app_cliente, libro_ejemplo, monkeypatch):
    _login_admin(app_cliente, monkeypatch)
    app_cliente.post("/api/libros", json=libro_ejemplo)
    app_cliente.post(
        "/api/ventas",
        json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 1}]},
    )

    respuesta = app_cliente.get("/api/ventas/resumen/total?periodo=semana")
    assert respuesta.status_code == 400
    assert "error" in respuesta.get_json()


def test_obtener_venta_inexistente_via_api(app_cliente, monkeypatch):
    _login_admin(app_cliente, monkeypatch)
    respuesta = app_cliente.get("/api/ventas/9999")
    assert respuesta.status_code == 404
