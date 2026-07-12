import pytest
from models.libro import Libro
from models.venta import DetalleVenta, Venta
from services.venta_service import VentaService, VentaServiceError


def test_registrar_venta_sin_items_lanza_error(venta_service):
    with pytest.raises(VentaServiceError, match="al menos un libro"):
        venta_service.registrar_venta([])


def test_registrar_venta_item_falta_isbn_lanza_error(venta_service):
    with pytest.raises(VentaServiceError, match="requiere 'isbn' y 'cantidad'"):
        venta_service.registrar_venta([{"cantidad": 1}])


def test_registrar_venta_item_cantidad_no_entero_lanza_error(libro_repository, venta_service, libro_ejemplo):
    libro_repository.crear(Libro(**libro_ejemplo))
    with pytest.raises(VentaServiceError, match="número entero"):
        venta_service.registrar_venta([{"isbn": libro_ejemplo["isbn"], "cantidad": "dos"}])


def test_listar_ventas_con_fecha_sin_periodo_lanza_error(venta_service):
    with pytest.raises(VentaServiceError, match="Debe especificarse un periodo"):
        venta_service.listar_ventas(periodo=None, fecha="2026-07-11")


def test_listar_ventas_periodo_invalido_lanza_error(venta_service):
    with pytest.raises(VentaServiceError, match="periodo debe ser"):
        venta_service.listar_ventas(periodo="semana")


def test_total_vendido_periodo_invalido_lanza_error(venta_service):
    with pytest.raises(VentaServiceError, match="periodo debe ser"):
        venta_service.total_vendido(periodo="semana")


def test_obtener_venta_inexistente_lanza_error(venta_service):
    with pytest.raises(VentaServiceError, match="No existe una venta"):
        venta_service.obtener_venta(9999)
