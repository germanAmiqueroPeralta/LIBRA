"""
repositories/venta_repository.py
Acceso a datos para las tablas 'ventas' y 'detalle_venta'.
"""
from models.venta import Venta, DetalleVenta


class VentaRepository:
    def __init__(self, connection):
        self.conn = connection

    def crear(self, venta: Venta) -> Venta:
        cursor = self.conn.execute(
            "INSERT INTO ventas (fecha, total) VALUES (?, ?)",
            (venta.fecha, venta.total),
        )
        venta_id = cursor.lastrowid

        for detalle in venta.detalles:
            self.conn.execute(
                """INSERT INTO detalle_venta
                   (venta_id, isbn, cantidad, precio_unitario, subtotal)
                   VALUES (?, ?, ?, ?, ?)""",
                (venta_id, detalle.isbn, detalle.cantidad,
                 detalle.precio_unitario, detalle.subtotal),
            )

        self.conn.commit()
        venta.id = venta_id
        return venta

    def obtener_todas(self, periodo: str | None = None, fecha: str | None = None) -> list:
        query = "SELECT * FROM ventas"
        params = []

        if periodo:
            periodo = periodo.lower()
            if periodo == "dia":
                if fecha:
                    query += " WHERE DATE(fecha) = ?"
                    params.append(fecha)
                else:
                    query += " WHERE DATE(fecha) = DATE('now', 'localtime')"
            elif periodo == "mes":
                if fecha:
                    query += " WHERE strftime('%Y-%m', fecha) = ?"
                    params.append(fecha)
                else:
                    query += " WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')"
            elif periodo == "anio":
                if fecha:
                    query += " WHERE strftime('%Y', fecha) = ?"
                    params.append(fecha)
                else:
                    query += " WHERE strftime('%Y', fecha) = strftime('%Y', 'now', 'localtime')"

        query += " ORDER BY fecha DESC"
        ventas_rows = self.conn.execute(query, params).fetchall()

        ventas = []
        for vrow in ventas_rows:
            detalle_rows = self.conn.execute(
                "SELECT dv.*, l.titulo FROM detalle_venta dv JOIN libros l ON dv.isbn = l.isbn WHERE dv.venta_id = ?",
                (vrow["id"],)
            ).fetchall()
            detalles = [
                DetalleVenta(d["isbn"], d["cantidad"], d["precio_unitario"], d["titulo"])
                for d in detalle_rows
            ]
            venta = Venta(fecha=vrow["fecha"], detalles=detalles, venta_id=vrow["id"])
            venta.total = vrow["total"]
            ventas.append(venta)
        return ventas

    def obtener_por_id(self, venta_id: int) -> Venta | None:
        vrow = self.conn.execute(
            "SELECT * FROM ventas WHERE id = ?", (venta_id,)
        ).fetchone()
        if vrow is None:
            return None

        detalle_rows = self.conn.execute(
            "SELECT dv.*, l.titulo FROM detalle_venta dv JOIN libros l ON dv.isbn = l.isbn WHERE dv.venta_id = ?",
            (venta_id,)
        ).fetchall()
        detalles = [
            DetalleVenta(d["isbn"], d["cantidad"], d["precio_unitario"], d["titulo"])
            for d in detalle_rows
        ]
        venta = Venta(fecha=vrow["fecha"], detalles=detalles, venta_id=vrow["id"])
        venta.total = vrow["total"]
        return venta

    def libros_mas_vendidos(self, limite: int = 5) -> list:
        rows = self.conn.execute(
            """SELECT dv.isbn, l.titulo, SUM(dv.cantidad) as total_vendido
               FROM detalle_venta dv
               JOIN libros l ON l.isbn = dv.isbn
               GROUP BY dv.isbn
               ORDER BY total_vendido DESC
               LIMIT ?""",
            (limite,),
        ).fetchall()
        return [dict(row) for row in rows]

    def total_vendido(self, periodo: str = "total", fecha: str | None = None) -> float:
        query = "SELECT SUM(total) as total FROM ventas"
        params = []

        if periodo == "dia":
            if fecha:
                query += " WHERE DATE(fecha) = ?"
                params.append(fecha)
            else:
                query += " WHERE DATE(fecha) = DATE('now', 'localtime')"
        elif periodo == "mes":
            if fecha:
                query += " WHERE strftime('%Y-%m', fecha) = ?"
                params.append(fecha)
            else:
                query += " WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')"
        elif periodo == "anio":
            if fecha:
                query += " WHERE strftime('%Y', fecha) = ?"
                params.append(fecha)
            else:
                query += " WHERE strftime('%Y', fecha) = strftime('%Y', 'now', 'localtime')"

        row = self.conn.execute(query, params).fetchone()
        return float(row["total"] or 0.0)
