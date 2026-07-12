"""
services/libro_service.py
Contiene las reglas de negocio relacionadas a los libros.
No conoce SQL: delega el acceso a datos al LibroRepository.
"""
from models.libro import Libro


class LibroServiceError(Exception):
    """Error de negocio en operaciones de libros."""
    pass


class LibroService:
    def __init__(self, libro_repository):
        self.repo = libro_repository

    def listar_libros(self) -> list:
        return self.repo.obtener_todos()

    def buscar_libros(self, termino: str) -> list:
        if not termino or not termino.strip():
            return self.repo.obtener_todos()
        return self.repo.buscar(termino.strip())

    def obtener_libro(self, isbn: str) -> Libro:
        libro = self.repo.obtener_por_isbn(isbn)
        if libro is None:
            raise LibroServiceError(f"No existe un libro con ISBN '{isbn}'.")
        return libro

    def registrar_libro(self, datos: dict) -> Libro:
        self._validar_datos_libro(datos)

        isbn = str(datos["isbn"]).strip()
        if self.repo.obtener_por_isbn(isbn) is not None:
            raise LibroServiceError(f"Ya existe un libro con ISBN '{isbn}'.")

        libro = Libro(
            isbn=isbn,
            titulo=str(datos["titulo"]).strip(),
            autor=str(datos["autor"]).strip(),
            precio=float(datos["precio"]),
            stock=int(datos["stock"]),
            categoria=str(datos.get("categoria", "")).strip(),
        )
        return self.repo.crear(libro)

    def actualizar_libro(self, isbn: str, datos: dict) -> Libro:
        self.obtener_libro(isbn)  # lanza error si no existe

        if "precio" in datos and float(datos["precio"]) < 0:
            raise LibroServiceError("El precio no puede ser negativo.")
        if "stock" in datos and int(datos["stock"]) < 0:
            raise LibroServiceError("El stock no puede ser negativo.")

        libro_actualizado = self.repo.actualizar(isbn, datos)
        return libro_actualizado

    def eliminar_libro(self, isbn: str) -> None:
        eliminado = self.repo.eliminar(isbn)
        if not eliminado:
            raise LibroServiceError(f"No existe un libro con ISBN '{isbn}'.")

    @staticmethod
    def _validar_datos_libro(datos: dict) -> None:
        campos_obligatorios = ["isbn", "titulo", "autor", "precio", "stock"]
        for campo in campos_obligatorios:
            if campo not in datos or datos[campo] in (None, ""):
                raise LibroServiceError(f"El campo '{campo}' es obligatorio.")

        try:
            precio = float(datos["precio"])
            stock = int(datos["stock"])
        except (TypeError, ValueError):
            raise LibroServiceError("Precio o stock tienen un formato inválido.")

        if precio < 0:
            raise LibroServiceError("El precio no puede ser negativo.")
        if stock < 0:
            raise LibroServiceError("El stock no puede ser negativo.")
