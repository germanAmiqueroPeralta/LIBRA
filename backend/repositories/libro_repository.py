"""
repositories/libro_repository.py
Única capa que habla directamente con SQLite para la tabla 'libros'.
No contiene reglas de negocio, solo operaciones CRUD puras.
"""
from models.libro import Libro


class LibroRepository:
    def __init__(self, connection):
        self.conn = connection

    def obtener_todos(self) -> list:
        cursor = self.conn.execute("SELECT * FROM libros ORDER BY titulo ASC")
        return [Libro.from_row(row) for row in cursor.fetchall()]

    def obtener_por_isbn(self, isbn: str) -> Libro | None:
        cursor = self.conn.execute("SELECT * FROM libros WHERE isbn = ?", (isbn,))
        row = cursor.fetchone()
        return Libro.from_row(row) if row else None

    def buscar(self, termino: str) -> list:
        """Busca por título, autor o categoría (búsqueda parcial, insensible a mayúsculas)."""
        patron = f"%{termino.lower()}%"
        cursor = self.conn.execute(
            """SELECT * FROM libros
               WHERE LOWER(titulo) LIKE ?
                  OR LOWER(autor) LIKE ?
                  OR LOWER(categoria) LIKE ?
               ORDER BY titulo ASC""",
            (patron, patron, patron),
        )
        return [Libro.from_row(row) for row in cursor.fetchall()]

    def crear(self, libro: Libro) -> Libro:
        self.conn.execute(
            """INSERT INTO libros (isbn, titulo, autor, precio, stock, categoria)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (libro.isbn, libro.titulo, libro.autor, libro.precio,
             libro.stock, libro.categoria),
        )
        self.conn.commit()
        return libro

    def actualizar(self, isbn: str, datos: dict) -> Libro | None:
        libro = self.obtener_por_isbn(isbn)
        if libro is None:
            return None

        titulo = datos.get("titulo", libro.titulo)
        autor = datos.get("autor", libro.autor)
        precio = datos.get("precio", libro.precio)
        stock = datos.get("stock", libro.stock)
        categoria = datos.get("categoria", libro.categoria)

        self.conn.execute(
            """UPDATE libros
               SET titulo = ?, autor = ?, precio = ?, stock = ?, categoria = ?
               WHERE isbn = ?""",
            (titulo, autor, precio, stock, categoria, isbn),
        )
        self.conn.commit()
        return self.obtener_por_isbn(isbn)

    def actualizar_stock(self, isbn: str, nuevo_stock: int) -> None:
        self.conn.execute(
            "UPDATE libros SET stock = ? WHERE isbn = ?", (nuevo_stock, isbn)
        )
        self.conn.commit()

    def eliminar(self, isbn: str) -> bool:
        libro = self.obtener_por_isbn(isbn)
        if libro is None:
            return False
        self.conn.execute("DELETE FROM libros WHERE isbn = ?", (isbn,))
        self.conn.commit()
        return True
