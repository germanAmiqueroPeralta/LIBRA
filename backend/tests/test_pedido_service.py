import pytest
from models.libro import Libro
from services.pedido_service import PedidoService, PedidoServiceError


def test_crear_pedido_valido(libro_repository, pedido_repository, libro_ejemplo):
    libro_repository.crear(Libro(**libro_ejemplo))
    servicio = PedidoService(pedido_repository, libro_repository)

    pedido = servicio.crear_pedido(
        "Cliente prueba",
        [{"isbn": libro_ejemplo["isbn"], "cantidad": 2}],
    )

    assert pedido.id is not None
    assert pedido.estado == "pendiente"
    assert pedido.total == pytest.approx(2 * libro_ejemplo["precio"])


def test_confirmar_pedido_actualiza_stock_y_estado(libro_repository, pedido_repository, libro_ejemplo):
    libro_repository.crear(Libro(**libro_ejemplo))
    servicio = PedidoService(pedido_repository, libro_repository)

    pedido = servicio.crear_pedido(
        "Cliente prueba",
        [{"isbn": libro_ejemplo["isbn"], "cantidad": 4}],
    )
    confirmado = servicio.confirmar_pedido(pedido.id)

    assert confirmado.estado == "confirmado"
    libro_actualizado = libro_repository.obtener_por_isbn(libro_ejemplo["isbn"])
    assert libro_actualizado.stock == libro_ejemplo["stock"] - 4

    with pytest.raises(PedidoServiceError):
        servicio.confirmar_pedido(pedido.id)


def test_crear_pedido_con_errores(libro_repository, pedido_repository, libro_ejemplo):
    servicio = PedidoService(pedido_repository, libro_repository)

    with pytest.raises(PedidoServiceError):
        servicio.crear_pedido("", [{"isbn": libro_ejemplo["isbn"], "cantidad": 1}])

    with pytest.raises(PedidoServiceError):
        servicio.crear_pedido("Cliente", [])

    with pytest.raises(PedidoServiceError):
        servicio.crear_pedido("Cliente", [{"isbn": libro_ejemplo["isbn"]}])

    with pytest.raises(PedidoServiceError):
        servicio.crear_pedido("Cliente", [{"isbn": libro_ejemplo["isbn"], "cantidad": "no-numero"}])

    with pytest.raises(PedidoServiceError):
        servicio.crear_pedido("Cliente", [{"isbn": libro_ejemplo["isbn"], "cantidad": 0}])

    with pytest.raises(PedidoServiceError):
        servicio.crear_pedido("Cliente", [{"isbn": "inexistente", "cantidad": 1}])

    libro_repository.crear(Libro(**libro_ejemplo))
    with pytest.raises(PedidoServiceError):
        servicio.crear_pedido("Cliente", [{"isbn": libro_ejemplo["isbn"], "cantidad": libro_ejemplo["stock"] + 1}])


def test_listar_pedidos_con_estado_invalido_lanza_error(libro_repository, pedido_repository):
    servicio = PedidoService(pedido_repository, libro_repository)
    with pytest.raises(PedidoServiceError):
        servicio.listar_pedidos("invalid")
