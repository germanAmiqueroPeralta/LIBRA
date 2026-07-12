"""
models/venta.py
Representa las entidades Venta y DetalleVenta.
"""


class DetalleVenta:
    def __init__(self, isbn: str, cantidad: int, precio_unitario: float, titulo: str = None):
        self.isbn = isbn
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.titulo = titulo or isbn
        self.subtotal = round(cantidad * precio_unitario, 2)

    def to_dict(self) -> dict:
        return {
            "isbn": self.isbn,
            "titulo": self.titulo,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
        }


class Venta:
    def __init__(self, fecha: str, detalles: list, venta_id: int = None):
        self.id = venta_id
        self.fecha = fecha
        self.detalles = detalles  # lista de DetalleVenta
        self.total = round(sum(d.subtotal for d in detalles), 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fecha": self.fecha,
            "total": self.total,
            "detalles": [d.to_dict() for d in self.detalles],
        }
