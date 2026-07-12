"""
tests/test_libros.py
Pruebas UNITARIAS: prueban el servicio y el repositorio de libros de
forma aislada, usando una base de datos SQLite en memoria.
"""
import pytest
from services.libro_service import LibroServiceError


class TestLibroRepository:
    """Pruebas del repositorio (acceso a datos puro)."""

    def test_crear_y_obtener_libro(self, libro_repository, libro_ejemplo):
        from models.libro import Libro
        libro = Libro(**libro_ejemplo)
        libro_repository.crear(libro)

        encontrado = libro_repository.obtener_por_isbn(libro_ejemplo["isbn"])
        assert encontrado is not None
        assert encontrado.titulo == libro_ejemplo["titulo"]

    def test_obtener_por_isbn_inexistente_retorna_none(self, libro_repository):
        assert libro_repository.obtener_por_isbn("0000000000") is None

    def test_actualizar_stock(self, libro_repository, libro_ejemplo):
        from models.libro import Libro
        libro_repository.crear(Libro(**libro_ejemplo))
        libro_repository.actualizar_stock(libro_ejemplo["isbn"], 3)

        actualizado = libro_repository.obtener_por_isbn(libro_ejemplo["isbn"])
        assert actualizado.stock == 3

    def test_eliminar_libro(self, libro_repository, libro_ejemplo):
        from models.libro import Libro
        libro_repository.crear(Libro(**libro_ejemplo))
        eliminado = libro_repository.eliminar(libro_ejemplo["isbn"])

        assert eliminado is True
        assert libro_repository.obtener_por_isbn(libro_ejemplo["isbn"]) is None


class TestLibroService:
    """Pruebas del servicio (reglas de negocio)."""

    def test_registrar_libro_valido(self, libro_service, libro_ejemplo):
        libro = libro_service.registrar_libro(libro_ejemplo)
        assert libro.isbn == libro_ejemplo["isbn"]
        assert libro.stock == 10

    def test_registrar_libro_sin_campo_obligatorio_lanza_error(self, libro_service, libro_ejemplo):
        datos_incompletos = libro_ejemplo.copy()
        del datos_incompletos["titulo"]

        with pytest.raises(LibroServiceError):
            libro_service.registrar_libro(datos_incompletos)

    def test_registrar_libro_con_precio_negativo_lanza_error(self, libro_service, libro_ejemplo):
        datos = libro_ejemplo.copy()
        datos["precio"] = -10
        with pytest.raises(LibroServiceError):
            libro_service.registrar_libro(datos)

    def test_registrar_libro_con_stock_negativo_lanza_error(self, libro_service, libro_ejemplo):
        datos = libro_ejemplo.copy()
        datos["stock"] = -1
        with pytest.raises(LibroServiceError):
            libro_service.registrar_libro(datos)

    def test_registrar_libro_duplicado_lanza_error(self, libro_service, libro_ejemplo):
        libro_service.registrar_libro(libro_ejemplo)
        with pytest.raises(LibroServiceError):
            libro_service.registrar_libro(libro_ejemplo)

    def test_listar_libros_vacio(self, libro_service):
        assert libro_service.listar_libros() == []

    def test_buscar_libros_por_titulo_parcial(self, libro_service, libro_ejemplo):
        libro_service.registrar_libro(libro_ejemplo)
        resultados = libro_service.buscar_libros("cien años")
        assert len(resultados) == 1
        assert resultados[0].isbn == libro_ejemplo["isbn"]

    def test_buscar_libros_sin_coincidencias(self, libro_service, libro_ejemplo):
        libro_service.registrar_libro(libro_ejemplo)
        resultados = libro_service.buscar_libros("inexistente-xyz")
        assert resultados == []

    def test_obtener_libro_inexistente_lanza_error(self, libro_service):
        with pytest.raises(LibroServiceError):
            libro_service.obtener_libro("no-existe")

    def test_actualizar_libro_valido(self, libro_service, libro_ejemplo):
        libro_service.registrar_libro(libro_ejemplo)
        actualizado = libro_service.actualizar_libro(
            libro_ejemplo["isbn"], {"precio": 55.00, "stock": 20}
        )
        assert actualizado.precio == 55.00
        assert actualizado.stock == 20

    def test_actualizar_libro_con_precio_negativo_lanza_error(self, libro_service, libro_ejemplo):
        libro_service.registrar_libro(libro_ejemplo)
        with pytest.raises(LibroServiceError):
            libro_service.actualizar_libro(libro_ejemplo["isbn"], {"precio": -5})

    def test_actualizar_libro_inexistente_lanza_error(self, libro_service):
        with pytest.raises(LibroServiceError):
            libro_service.actualizar_libro("no-existe", {"precio": 10})

    def test_eliminar_libro_existente(self, libro_service, libro_ejemplo):
        libro_service.registrar_libro(libro_ejemplo)
        libro_service.eliminar_libro(libro_ejemplo["isbn"])
        with pytest.raises(LibroServiceError):
            libro_service.obtener_libro(libro_ejemplo["isbn"])

    def test_eliminar_libro_inexistente_lanza_error(self, libro_service):
        with pytest.raises(LibroServiceError):
            libro_service.eliminar_libro("no-existe")
