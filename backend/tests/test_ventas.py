"""
tests/test_ventas.py
Pruebas UNITARIAS del servicio de ventas: validación de stock,
cálculo de totales y actualización de stock tras una venta.
"""
import pytest
from services.venta_service import VentaServiceError
from models.libro import Libro


@pytest.fixture
def libro_en_stock(libro_repository, libro_ejemplo):
    """Crea un libro con stock=10 y precio=45.90 listo para vender."""
    libro_repository.crear(Libro(**libro_ejemplo))
    return libro_ejemplo


class TestVentaService:

    def test_registrar_venta_valida_descuenta_stock(self, venta_service, libro_repository, libro_en_stock):
        isbn = libro_en_stock["isbn"]
        venta = venta_service.registrar_venta([{"isbn": isbn, "cantidad": 3}])

        assert venta.id is not None
        assert venta.total == pytest.approx(3 * 45.90, rel=1e-3)

        libro_actualizado = libro_repository.obtener_por_isbn(isbn)
        assert libro_actualizado.stock == 7  # 10 - 3

    def test_venta_no_permite_vender_mas_del_stock_disponible(self, venta_service, libro_en_stock):
        """Caso de prueba explícitamente pedido en el documento del proyecto."""
        isbn = libro_en_stock["isbn"]
        with pytest.raises(VentaServiceError):
            venta_service.registrar_venta([{"isbn": isbn, "cantidad": 999}])

    def test_venta_con_cantidad_igual_al_stock_es_valida(self, venta_service, libro_repository, libro_en_stock):
        isbn = libro_en_stock["isbn"]
        venta_service.registrar_venta([{"isbn": isbn, "cantidad": 10}])
        libro_actualizado = libro_repository.obtener_por_isbn(isbn)
        assert libro_actualizado.stock == 0

    def test_venta_con_cantidad_cero_lanza_error(self, venta_service, libro_en_stock):
        with pytest.raises(VentaServiceError):
            venta_service.registrar_venta([{"isbn": libro_en_stock["isbn"], "cantidad": 0}])

    def test_venta_con_cantidad_negativa_lanza_error(self, venta_service, libro_en_stock):
        with pytest.raises(VentaServiceError):
            venta_service.registrar_venta([{"isbn": libro_en_stock["isbn"], "cantidad": -2}])

    def test_venta_con_libro_inexistente_lanza_error(self, venta_service):
        with pytest.raises(VentaServiceError):
            venta_service.registrar_venta([{"isbn": "no-existe", "cantidad": 1}])

    def test_venta_sin_items_lanza_error(self, venta_service):
        with pytest.raises(VentaServiceError):
            venta_service.registrar_venta([])

    def test_venta_no_descuenta_stock_si_un_item_falla(self, venta_service, libro_repository, libro_en_stock):
        """
        Si la venta tiene 2 items y uno falla por stock insuficiente,
        NINGÚN libro debe perder stock (todo o nada).
        """
        isbn = libro_en_stock["isbn"]
        items = [
            {"isbn": isbn, "cantidad": 2},
            {"isbn": "no-existe", "cantidad": 1},
        ]
        with pytest.raises(VentaServiceError):
            venta_service.registrar_venta(items)

        libro_intacto = libro_repository.obtener_por_isbn(isbn)
        assert libro_intacto.stock == 10  # no cambió

    def test_total_vendido_acumula_varias_ventas(self, venta_service, libro_en_stock):
        isbn = libro_en_stock["isbn"]
        venta_service.registrar_venta([{"isbn": isbn, "cantidad": 1}])
        venta_service.registrar_venta([{"isbn": isbn, "cantidad": 2}])

        total = venta_service.total_vendido()
        assert total == pytest.approx(3 * 45.90, rel=1e-3)

    def test_libros_mas_vendidos(self, venta_service, libro_en_stock):
        isbn = libro_en_stock["isbn"]
        venta_service.registrar_venta([{"isbn": isbn, "cantidad": 5}])

        resultado = venta_service.libros_mas_vendidos()
        assert len(resultado) == 1
        assert resultado[0]["isbn"] == isbn
        assert resultado[0]["total_vendido"] == 5

    def test_listar_ventas_retorna_vacio_si_no_hay_ventas(self, venta_service):
        assert venta_service.listar_ventas() == []
