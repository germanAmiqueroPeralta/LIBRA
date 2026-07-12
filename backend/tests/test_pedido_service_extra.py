import pytest
from models.libro import Libro
from services.pedido_service import PedidoService, PedidoServiceError


def test_crear_pedido_valido_y_confirmar_pedido_confirmado(libro_repository, pedido_repository, libro_ejemplo):
    libro_repository.crear(Libro(**libro_ejemplo))
    servicio = PedidoService(pedido_repository, libro_repository)
    pedido = servicio.crear_pedido("Cliente", [{"isbn": libro_ejemplo["isbn"], "cantidad": 1}])

    pedido_confirmado = servicio.confirmar_pedido(pedido.id)
    assert pedido_confirmado.estado == "confirmado"

    with pytest.raises(PedidoServiceError, match="pedido ya fue confirmado"):
        servicio.confirmar_pedido(pedido.id)


def test_confirmar_pedido_con_libro_inexistente_lanza_error(db_connection, libro_repository, pedido_repository, libro_ejemplo):
    libro_repository.crear(Libro(**libro_ejemplo))
    servicio = PedidoService(pedido_repository, libro_repository)
    pedido = servicio.crear_pedido("Cliente", [{"isbn": libro_ejemplo["isbn"], "cantidad": 1}])

    db_connection.execute("PRAGMA foreign_keys = OFF")
    db_connection.execute("DELETE FROM libros WHERE isbn = ?", (libro_ejemplo["isbn"],))
    db_connection.execute("PRAGMA foreign_keys = ON")
    db_connection.commit()

    with pytest.raises(PedidoServiceError, match="No existe un libro con ISBN"):
        servicio.confirmar_pedido(pedido.id)


def test_confirmar_pedido_con_stock_insuficiente_lanza_error(libro_repository, pedido_repository, libro_ejemplo):
    libro_repository.crear(Libro(**libro_ejemplo))
    servicio = PedidoService(pedido_repository, libro_repository)
    pedido = servicio.crear_pedido("Cliente", [{"isbn": libro_ejemplo["isbn"], "cantidad": 2}])

    libro_repository.actualizar_stock(libro_ejemplo["isbn"], 1)

    with pytest.raises(PedidoServiceError, match="Stock insuficiente"):
        servicio.confirmar_pedido(pedido.id)
