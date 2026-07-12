"""
routes/libros.py
Controlador HTTP: recibe peticiones, llama al servicio y devuelve JSON.
No contiene reglas de negocio ni SQL.
"""
from flask import Blueprint, request, jsonify
from services.libro_service import LibroService, LibroServiceError
from repositories.libro_repository import LibroRepository
from routes.auth import require_admin

libros_bp = Blueprint("libros", __name__, url_prefix="/api/libros")


def _get_service():
    from flask import g
    repo = LibroRepository(g.db)
    return LibroService(repo)


@libros_bp.route("", methods=["GET"])
def listar_libros():
    termino = request.args.get("buscar", "")
    service = _get_service()
    libros = service.buscar_libros(termino)
    return jsonify([libro.to_dict() for libro in libros]), 200


@libros_bp.route("/<isbn>", methods=["GET"])
def obtener_libro(isbn):
    service = _get_service()
    try:
        libro = service.obtener_libro(isbn)
        return jsonify(libro.to_dict()), 200
    except LibroServiceError as e:
        return jsonify({"error": str(e)}), 404


@libros_bp.route("", methods=["POST"])
@require_admin
def registrar_libro():
    datos = request.get_json(silent=True) or {}
    service = _get_service()
    try:
        libro = service.registrar_libro(datos)
        return jsonify(libro.to_dict()), 201
    except LibroServiceError as e:
        return jsonify({"error": str(e)}), 400


@libros_bp.route("/<isbn>", methods=["PUT"])
@require_admin
def actualizar_libro(isbn):
    datos = request.get_json(silent=True) or {}
    service = _get_service()
    try:
        libro = service.actualizar_libro(isbn, datos)
        return jsonify(libro.to_dict()), 200
    except LibroServiceError as e:
        return jsonify({"error": str(e)}), 400


@libros_bp.route("/<isbn>", methods=["DELETE"])
@require_admin
def eliminar_libro(isbn):
    service = _get_service()
    try:
        service.eliminar_libro(isbn)
        return jsonify({"mensaje": "Libro eliminado correctamente."}), 200
    except LibroServiceError as e:
        return jsonify({"error": str(e)}), 404
