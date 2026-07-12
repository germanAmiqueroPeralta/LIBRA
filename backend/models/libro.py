"""
models/libro.py
Representa la entidad Libro. Es un objeto plano (sin lógica de negocio ni SQL).
"""


class Libro:
    def __init__(self, isbn: str, titulo: str, autor: str, precio: float,
                 stock: int, categoria: str = ""):
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.precio = precio
        self.stock = stock
        self.categoria = categoria

    def to_dict(self) -> dict:
        return {
            "isbn": self.isbn,
            "titulo": self.titulo,
            "autor": self.autor,
            "precio": self.precio,
            "stock": self.stock,
            "categoria": self.categoria,
        }

    @staticmethod
    def from_row(row) -> "Libro":
        """Construye un Libro a partir de una fila de sqlite3.Row."""
        return Libro(
            isbn=row["isbn"],
            titulo=row["titulo"],
            autor=row["autor"],
            precio=row["precio"],
            stock=row["stock"],
            categoria=row["categoria"],
        )
