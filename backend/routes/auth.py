from functools import wraps

from flask import Blueprint, jsonify, request, session

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

USERS = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
}


def get_current_user():
    return session.get("user")


def require_admin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.get("role") != "admin":
            return jsonify({"error": "No autorizado"}), 403
        return view_func(*args, **kwargs)

    return wrapper


@auth_bp.route("/register", methods=["POST"])
def register():
    datos = request.get_json(silent=True) or {}
    username = (datos.get("username") or "").strip()
    password = (datos.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña son obligatorios"}), 400

    if username in USERS:
        return jsonify({"error": "Ese usuario ya existe"}), 409

    USERS[username] = {"username": username, "password": password, "role": "cliente"}
    session["user"] = {"username": username, "role": "cliente"}
    return jsonify({"message": "Cuenta creada", "user": session["user"]}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True) or {}
    username = (datos.get("username") or "").strip()
    password = (datos.get("password") or "").strip()

    usuario = USERS.get(username)
    if usuario and usuario["password"] == password:
        session["user"] = {"username": usuario["username"], "role": usuario["role"]}
        return jsonify({"message": "Login correcto", "user": session["user"]}), 200

    return jsonify({"error": "Credenciales inválidas"}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Sesión cerrada"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    return jsonify({"user": get_current_user()}), 200
