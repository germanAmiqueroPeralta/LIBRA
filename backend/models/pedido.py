"""
models/pedido.py
Representa la entidad Pedido y su detalle.
"""

class DetallePedido:
    def __init__(self, isbn: str, cantidad: int, precio_unitario: float):
        self.isbn = isbn
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = round(cantidad * precio_unitario, 2)

    def to_dict(self) -> dict:
        return {
            "isbn": self.isbn,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
        }


class Pedido:
    def __init__(self, cliente: str, fecha: str, detalles: list, pedido_id: int = None, estado: str = "pendiente"):
        self.id = pedido_id
        self.cliente = cliente
        self.fecha = fecha
        self.detalles = detalles
        self.estado = estado
        self.total = round(sum(d.subtotal for d in detalles), 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cliente": self.cliente,
            "fecha": self.fecha,
            "estado": self.estado,
            "total": self.total,
            "detalles": [d.to_dict() for d in self.detalles],
        }
