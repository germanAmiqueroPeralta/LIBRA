import pytest
from models.libro import Libro
from models.venta import Venta, DetalleVenta
from repositories.venta_repository import VentaRepository


def test_venta_repository_create_and_obtener_por_id(db_connection, libro_repository, libro_ejemplo):
    libro_repository.crear(Libro(**libro_ejemplo))
    repo = VentaRepository(db_connection)

    venta = Venta(
        fecha="2026-07-11T10:00:00",
        detalles=[DetalleVenta(libro_ejemplo["isbn"], 2, libro_ejemplo["precio"], libro_ejemplo["titulo"])],
    )
    creado = repo.crear(venta)

    encontrado = repo.obtener_por_id(creado.id)
    assert encontrado is not None
    assert encontrado.id == creado.id
    assert len(encontrado.detalles) == 1
    assert encontrado.detalles[0].titulo == libro_ejemplo["titulo"]


def test_venta_repository_obtener_todas_y_resumenes(db_connection, libro_repository, libro_ejemplo):
    libro_repository.crear(Libro(**libro_ejemplo))
    repo = VentaRepository(db_connection)

    venta1 = Venta(
        fecha="2026-07-11T10:00:00",
        detalles=[DetalleVenta(libro_ejemplo["isbn"], 2, libro_ejemplo["precio"], libro_ejemplo["titulo"])],
    )
    venta2 = Venta(
        fecha="2026-06-30T09:00:00",
        detalles=[DetalleVenta(libro_ejemplo["isbn"], 1, libro_ejemplo["precio"], libro_ejemplo["titulo"])],
    )
    repo.crear(venta1)
    repo.crear(venta2)

    todas = repo.obtener_todas()
    assert len(todas) == 2

    por_dia = repo.obtener_todas("dia", "2026-07-11")
    assert len(por_dia) == 1

    por_mes = repo.obtener_todas("mes", "2026-07")
    assert len(por_mes) == 1

    por_anio = repo.obtener_todas("anio", "2026")
    assert len(por_anio) == 2

    total = repo.total_vendido()
    assert total == pytest.approx(venta1.total + venta2.total)

    total_dia = repo.total_vendido("dia", "2026-07-11")
    assert total_dia == pytest.approx(venta1.total)

    total_mes = repo.total_vendido("mes", "2026-07")
    assert total_mes == pytest.approx(venta1.total)

    total_anio = repo.total_vendido("anio", "2026")
    assert total_anio == pytest.approx(venta1.total + venta2.total)

    mas_vendidos = repo.libros_mas_vendidos(limite=1)
    assert len(mas_vendidos) == 1
    assert mas_vendidos[0]["isbn"] == libro_ejemplo["isbn"]
    assert mas_vendidos[0]["total_vendido"] == 3
