"""
app.py
Punto de entrada de la API REST. Configura Flask, CORS, la conexión
a base de datos por request y registra los blueprints (rutas).
"""
import os

from flask import Flask, g, jsonify
from flask_cors import CORS

import config
from database import get_connection, init_db
from routes.auth import auth_bp
from routes.libros import libros_bp
from routes.ventas import ventas_bp
from routes.pedidos import pedidos_bp


def create_app(db_path: str = None) -> Flask:
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    app = Flask(__name__, static_folder=frontend_path, static_url_path="")
    CORS(app)  # Permite que el frontend se sirva desde el mismo origen o desde otro origen

    app.config["DATABASE_PATH"] = db_path or config.DATABASE_PATH
    app.secret_key = "libreria-secret-key"

    # Inicializa el esquema al arrancar (solo crea tablas si no existen)
    init_db(app.config["DATABASE_PATH"])

    @app.before_request
    def abrir_conexion():
        g.db = get_connection(app.config["DATABASE_PATH"])

    @app.teardown_request
    def cerrar_conexion(exception=None):
        db = getattr(g, "db", None)
        if db is not None:
            db.close()

    app.register_blueprint(auth_bp)
    app.register_blueprint(libros_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(pedidos_bp)

    @app.route("/", methods=["GET"])
    def inicio():
        return app.send_static_file("index.html")

    @app.route("/api/salud", methods=["GET"])
    def salud():
        return jsonify({"estado": "ok", "mensaje": "API Libreria funcionando"}), 200

    @app.errorhandler(404)
    def no_encontrado(e):
        return jsonify({"error": "Recurso no encontrado."}), 404

    @app.errorhandler(500)
    def error_interno(e):
        return jsonify({"error": "Error interno del servidor."}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
