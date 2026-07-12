from models.libro import Libro
from models.pedido import Pedido, DetallePedido
from repositories.pedido_repository import PedidoRepository


def test_pedido_model_to_dict():
    detalle = DetallePedido(isbn="978-1", cantidad=2, precio_unitario=12.5)
    assert detalle.subtotal == 25.0
    assert detalle.to_dict() == {
        "isbn": "978-1",
        "cantidad": 2,
        "precio_unitario": 12.5,
        "subtotal": 25.0,
    }

    pedido = Pedido(
        cliente="Gabriel",
        fecha="2026-07-11T10:00:00",
        detalles=[detalle],
    )
    assert pedido.total == 25.0
    assert pedido.to_dict()["estado"] == "pendiente"


def test_pedido_repository_create_and_retrieve_by_id(db_connection, libro_repository):
    libro_repository.crear(Libro(isbn="978-2", titulo="Libro 2", autor="Autor", precio=30.0, stock=5, categoria="Novela"))
    repo = PedidoRepository(db_connection)
    pedido = Pedido(
        cliente="Ana",
        fecha="2026-07-11T10:00:00",
        detalles=[DetallePedido(isbn="978-2", cantidad=1, precio_unitario=30.0)],
    )

    creado = repo.crear(pedido)
    assert creado.id is not None
    assert creado.cliente == "Ana"

    encontrado = repo.obtener_por_id(creado.id)
    assert encontrado is not None
    assert encontrado.cliente == "Ana"
    assert encontrado.detalles[0].subtotal == 30.0


def test_pedido_repository_filter_by_estado_and_update_status(db_connection, libro_repository):
    libro_repository.crear(Libro(isbn="978-3", titulo="Libro 3", autor="Autor", precio=15.0, stock=5, categoria="Historia"))
    libro_repository.crear(Libro(isbn="978-4", titulo="Libro 4", autor="Autor", precio=20.0, stock=5, categoria="Historia"))
    repo = PedidoRepository(db_connection)
    pedido1 = Pedido(
        cliente="Pedro",
        fecha="2026-07-12T12:00:00",
        detalles=[DetallePedido(isbn="978-3", cantidad=2, precio_unitario=15.0)],
    )
    pedido2 = Pedido(
        cliente="Laura",
        fecha="2026-07-13T13:00:00",
        detalles=[DetallePedido(isbn="978-4", cantidad=1, precio_unitario=20.0)],
        estado="confirmado",
    )

    repo.crear(pedido1)
    creado2 = repo.crear(pedido2)

    pendientes = repo.obtener_todos("pendiente")
    confirmados = repo.obtener_todos("confirmado")

    assert len(pendientes) == 1
    assert len(confirmados) == 1
    assert confirmados[0].cliente == "Laura"

    actualizado = repo.actualizar_estado(creado2.id, "pendiente")
    assert actualizado.estado == "pendiente"
    encontrado = repo.obtener_por_id(creado2.id)
    assert encontrado.estado == "pendiente"
