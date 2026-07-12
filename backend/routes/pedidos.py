"""
routes/pedidos.py
Controlador HTTP para pedidos de clientes.
"""
from flask import Blueprint, request, jsonify, g
from services.pedido_service import PedidoService, PedidoServiceError
from repositories.pedido_repository import PedidoRepository
from repositories.libro_repository import LibroRepository
from routes.auth import require_admin

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/api/pedidos")


def _get_service():
    pedido_repo = PedidoRepository(g.db)
    libro_repo = LibroRepository(g.db)
    return PedidoService(pedido_repo, libro_repo)


@pedidos_bp.route("", methods=["POST"])
def crear_pedido():
    datos = request.get_json(silent=True) or {}
    cliente = datos.get("cliente")
    items = datos.get("items", [])
    service = _get_service()
    try:
        pedido = service.crear_pedido(cliente, items)
        return jsonify(pedido.to_dict()), 201
    except PedidoServiceError as e:
        return jsonify({"error": str(e)}), 400


@pedidos_bp.route("", methods=["GET"])
@require_admin
def listar_pedidos():
    estado = request.args.get("estado")
    service = _get_service()
    try:
        pedidos = service.listar_pedidos(estado)
        return jsonify([p.to_dict() for p in pedidos]), 200
    except PedidoServiceError as e:
        return jsonify({"error": str(e)}), 400


@pedidos_bp.route("/<int:pedido_id>/confirmar", methods=["POST"])
@require_admin
def confirmar_pedido(pedido_id):
    service = _get_service()
    try:
        pedido = service.confirmar_pedido(pedido_id)
        return jsonify(pedido.to_dict()), 200
    except PedidoServiceError as e:
        return jsonify({"error": str(e)}), 400
