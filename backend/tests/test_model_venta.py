from models.venta import Venta, DetalleVenta


def test_venta_to_dict_incluye_detalles_y_total():
    detalle = DetalleVenta(isbn="978-1", cantidad=2, precio_unitario=10.0, titulo="Demo")
    venta = Venta(fecha="2026-07-11T12:00:00", detalles=[detalle], venta_id=1)

    resultado = venta.to_dict()
    assert resultado["id"] == 1
    assert resultado["total"] == 20.0
    assert resultado["detalles"][0]["subtotal"] == 20.0
    assert resultado["detalles"][0]["titulo"] == "Demo"
