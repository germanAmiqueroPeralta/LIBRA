"""
services/pedido_service.py
Reglas de negocio para los pedidos de clientes.
"""
from datetime import datetime
from models.pedido import Pedido, DetallePedido
from models.venta import Venta, DetalleVenta
from repositories.venta_repository import VentaRepository


class PedidoServiceError(Exception):
    pass


class PedidoService:
    def __init__(self, pedido_repository, libro_repository):
        self.pedido_repo = pedido_repository
        self.libro_repo = libro_repository
        self.venta_repo = VentaRepository(pedido_repository.conn)

    def crear_pedido(self, cliente: str, items: list) -> Pedido:
        if not cliente or not cliente.strip():
            raise PedidoServiceError("El nombre del cliente es obligatorio.")

        if not items:
            raise PedidoServiceError("El pedido debe incluir al menos un libro.")

        detalles = []
        for item in items:
            isbn = item.get("isbn")
            cantidad = item.get("cantidad")
            if not isbn or cantidad is None:
                raise PedidoServiceError("Cada ítem debe contener 'isbn' y 'cantidad'.")

            try:
                cantidad = int(cantidad)
            except (TypeError, ValueError):
                raise PedidoServiceError("La cantidad debe ser un número entero.")

            if cantidad <= 0:
                raise PedidoServiceError("La cantidad debe ser mayor a cero.")

            libro = self.libro_repo.obtener_por_isbn(isbn)
            if libro is None:
                raise PedidoServiceError(f"No existe un libro con ISBN '{isbn}'.")

            if cantidad > libro.stock:
                raise PedidoServiceError(
                    f"Stock insuficiente para '{libro.titulo}'. Disponible: {libro.stock}."
                )

            detalles.append(DetallePedido(isbn, cantidad, libro.precio))

        fecha = datetime.now().isoformat(timespec="seconds")
        pedido = Pedido(cliente=cliente.strip(), fecha=fecha, detalles=detalles)
        return self.pedido_repo.crear(pedido)

    def listar_pedidos(self, estado: str | None = None) -> list:
        if estado is not None:
            estado = estado.strip().lower()
            if estado not in {"pendiente", "confirmado"}:
                raise PedidoServiceError("Estado inválido para filtrar pedidos.")
        return self.pedido_repo.obtener_todos(estado)

    def confirmar_pedido(self, pedido_id: int) -> Pedido:
        pedido = self.pedido_repo.obtener_por_id(pedido_id)
        if pedido is None:
            raise PedidoServiceError(f"No existe un pedido con id {pedido_id}.")
        if pedido.estado == "confirmado":
            raise PedidoServiceError("El pedido ya fue confirmado.")

        for item in pedido.detalles:
            libro = self.libro_repo.obtener_por_isbn(item.isbn)
            if libro is None:
                raise PedidoServiceError(f"No existe un libro con ISBN '{item.isbn}'.")
            if item.cantidad > libro.stock:
                raise PedidoServiceError(
                    f"Stock insuficiente para '{libro.titulo}'. Disponible: {libro.stock}."
                )

        venta = Venta(fecha=pedido.fecha, detalles=[DetalleVenta(d.isbn, d.cantidad, d.precio_unitario) for d in pedido.detalles])
        self.venta_repo.crear(venta)

        for item in pedido.detalles:
            libro = self.libro_repo.obtener_por_isbn(item.isbn)
            nuevo_stock = libro.stock - item.cantidad
            self.libro_repo.actualizar_stock(item.isbn, nuevo_stock)

        pedido_confirmado = self.pedido_repo.actualizar_estado(pedido_id, "confirmado")
        if pedido_confirmado is None:
            raise PedidoServiceError(f"No existe un pedido con id {pedido_id}.")
        return pedido_confirmado
