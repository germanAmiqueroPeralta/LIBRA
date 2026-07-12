import pytest
from services.libro_service import LibroService, LibroServiceError
from models.libro import Libro


def test_buscar_libros_sin_termino_llama_obtener_todos(libro_service, libro_repository, libro_ejemplo):
    libro_repository.crear(Libro(**libro_ejemplo))
    resultados = libro_service.buscar_libros("")
    assert len(resultados) == 1


def test_registrar_libro_precio_formato_invalido_lanza_error(libro_service, libro_ejemplo):
    datos = libro_ejemplo.copy()
    datos["precio"] = "no-numero"

    with pytest.raises(LibroServiceError, match="formato inválido"):
        libro_service.registrar_libro(datos)


def test_registrar_libro_stock_formato_invalido_lanza_error(libro_service, libro_ejemplo):
    datos = libro_ejemplo.copy()
    datos["stock"] = "no-numero"

    with pytest.raises(LibroServiceError, match="formato inválido"):
        libro_service.registrar_libro(datos)
