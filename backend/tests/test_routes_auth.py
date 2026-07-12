import pytest
from routes import auth as auth_module


def test_register_login_logout_and_me(app_cliente, monkeypatch):
    monkeypatch.setattr(
        auth_module,
        "USERS",
        {"admin": {"username": "admin", "password": "admin123", "role": "admin"}},
        raising=True,
    )

    respuesta = app_cliente.post(
        "/api/auth/register",
        json={"username": "cliente1", "password": "clave123"},
    )
    assert respuesta.status_code == 201
    data = respuesta.get_json()
    assert data["user"]["role"] == "cliente"
    assert data["user"]["username"] == "cliente1"

    respuesta = app_cliente.post(
        "/api/auth/login",
        json={"username": "cliente1", "password": "clave123"},
    )
    assert respuesta.status_code == 200

    respuesta = app_cliente.get("/api/auth/me")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["user"]["username"] == "cliente1"

    respuesta = app_cliente.post("/api/auth/logout")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["message"] == "Sesión cerrada"

    respuesta = app_cliente.get("/api/auth/me")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["user"] is None


def test_login_invalid_credentials_returns_401(app_cliente, monkeypatch):
    monkeypatch.setattr(
        auth_module,
        "USERS",
        {"admin": {"username": "admin", "password": "admin123", "role": "admin"}},
        raising=True,
    )

    respuesta = app_cliente.post(
        "/api/auth/login",
        json={"username": "admin", "password": "incorrecto"},
    )
    assert respuesta.status_code == 401
    assert respuesta.get_json()["error"] == "Credenciales inválidas"


def test_register_duplicate_user_returns_409(app_cliente, monkeypatch):
    monkeypatch.setattr(
        auth_module,
        "USERS",
        {"admin": {"username": "admin", "password": "admin123", "role": "admin"}},
        raising=True,
    )

    respuesta = app_cliente.post(
        "/api/auth/register",
        json={"username": "admin", "password": "cualquier"},
    )
    assert respuesta.status_code == 409
    assert respuesta.get_json()["error"] == "Ese usuario ya existe"
