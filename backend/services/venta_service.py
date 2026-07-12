"""
services/venta_service.py
Reglas de negocio para el proceso de venta: valida stock, calcula
totales y descuenta stock a través del repositorio de libros.
"""
from datetime import datetime
from models.venta import Venta, DetalleVenta


class VentaServiceError(Exception):
    """Error de negocio en operaciones de venta."""
    pass


class VentaService:
    def __init__(self, venta_repository, libro_repository):
        self.venta_repo = venta_repository
        self.libro_repo = libro_repository

    def registrar_venta(self, items: list) -> Venta:
        """
        items: lista de dicts [{"isbn": "...", "cantidad": N}, ...]
        Valida stock disponible, calcula el total y descuenta el stock.
        """
        if not items:
            raise VentaServiceError("La venta debe tener al menos un libro.")

        detalles = []
        libros_a_actualizar = []

        for item in items:
            isbn = item.get("isbn")
            cantidad = item.get("cantidad")

            if not isbn or cantidad is None:
                raise VentaServiceError("Cada ítem requiere 'isbn' y 'cantidad'.")

            try:
                cantidad = int(cantidad)
            except (TypeError, ValueError):
                raise VentaServiceError("La cantidad debe ser un número entero.")

            if cantidad <= 0:
                raise VentaServiceError("La cantidad debe ser mayor a cero.")

            libro = self.libro_repo.obtener_por_isbn(isbn)
            if libro is None:
                raise VentaServiceError(f"No existe un libro con ISBN '{isbn}'.")

            if cantidad > libro.stock:
                raise VentaServiceError(
                    f"Stock insuficiente para '{libro.titulo}'. "
                    f"Disponible: {libro.stock}, solicitado: {cantidad}."
                )

            detalles.append(DetalleVenta(isbn, cantidad, libro.precio))
            libros_a_actualizar.append((libro, cantidad))

        fecha = datetime.now().isoformat(timespec="seconds")
        venta = Venta(fecha=fecha, detalles=detalles)
        venta_guardada = self.venta_repo.crear(venta)

        # Descontar stock solo después de validar TODOS los ítems.
        for libro, cantidad in libros_a_actualizar:
            nuevo_stock = libro.stock - cantidad
            self.libro_repo.actualizar_stock(libro.isbn, nuevo_stock)

        return venta_guardada

    def listar_ventas(self, periodo: str | None = None, fecha: str | None = None) -> list:
        if periodo is None and fecha is not None:
            raise VentaServiceError("Debe especificarse un periodo al filtrar por fecha.")

        if periodo is not None:
            periodo = periodo.strip().lower()
            if periodo not in {"total", "dia", "mes", "anio"}:
                raise VentaServiceError("El periodo debe ser 'total', 'dia', 'mes' o 'anio'.")

        return self.venta_repo.obtener_todas(
            None if periodo == "total" else periodo,
            fecha,
        )

    def obtener_venta(self, venta_id: int) -> Venta:
        venta = self.venta_repo.obtener_por_id(venta_id)
        if venta is None:
            raise VentaServiceError(f"No existe una venta con id {venta_id}.")
        return venta

    def total_vendido(self, periodo: str = "total", fecha: str | None = None) -> float:
        periodo = (periodo or "total").strip().lower()
        validos = {"total", "dia", "mes", "anio"}
        if periodo not in validos:
            raise VentaServiceError("El periodo debe ser 'total', 'dia', 'mes' o 'anio'.")
        return round(self.venta_repo.total_vendido(periodo, fecha), 2)

    def libros_mas_vendidos(self, limite: int = 5) -> list:
        return self.venta_repo.libros_mas_vendidos(limite)
