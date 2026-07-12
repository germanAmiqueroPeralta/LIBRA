"""
routes/ventas.py
Controlador HTTP para el proceso de ventas e historial.
"""
from flask import Blueprint, request, jsonify
from services.venta_service import VentaService, VentaServiceError
from repositories.venta_repository import VentaRepository
from repositories.libro_repository import LibroRepository
from routes.auth import require_admin

ventas_bp = Blueprint("ventas", __name__, url_prefix="/api/ventas")


def _get_service():
    from flask import g
    venta_repo = VentaRepository(g.db)
    libro_repo = LibroRepository(g.db)
    return VentaService(venta_repo, libro_repo)


@ventas_bp.route("", methods=["POST"])
@require_admin
def registrar_venta():
    datos = request.get_json(silent=True) or {}
    items = datos.get("items", [])
    service = _get_service()
    try:
        venta = service.registrar_venta(items)
        return jsonify(venta.to_dict()), 201
    except VentaServiceError as e:
        return jsonify({"error": str(e)}), 400


@ventas_bp.route("", methods=["GET"])
@require_admin
def listar_ventas():
    periodo = (request.args.get("periodo") or "total").lower()
    fecha = request.args.get("fecha")
    service = _get_service()
    try:
        ventas = service.listar_ventas(periodo, fecha)
        return jsonify([v.to_dict() for v in ventas]), 200
    except VentaServiceError as e:
        return jsonify({"error": str(e)}), 400


@ventas_bp.route("/<int:venta_id>", methods=["GET"])
@require_admin
def obtener_venta(venta_id):
    service = _get_service()
    try:
        venta = service.obtener_venta(venta_id)
        return jsonify(venta.to_dict()), 200
    except VentaServiceError as e:
        return jsonify({"error": str(e)}), 404


@ventas_bp.route("/resumen/total", methods=["GET"])
@require_admin
def total_vendido():
    periodo = (request.args.get("periodo", "total") or "total").lower()
    fecha = request.args.get("fecha")
    service = _get_service()
    try:
        total = service.total_vendido(periodo, fecha)
        return jsonify({"total_vendido": total, "periodo": periodo, "fecha": fecha}), 200
    except VentaServiceError as e:
        return jsonify({"error": str(e)}), 400


@ventas_bp.route("/resumen/mas-vendidos", methods=["GET"])
@require_admin
def libros_mas_vendidos():
    service = _get_service()
    limite = request.args.get("limite", default=5, type=int)
    return jsonify(service.libros_mas_vendidos(limite)), 200
