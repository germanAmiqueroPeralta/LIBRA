"""
repositories/pedido_repository.py
Acceso a datos para la tabla de pedidos.
"""
from models.pedido import Pedido, DetallePedido


class PedidoRepository:
    def __init__(self, connection):
        self.conn = connection

    def crear(self, pedido: Pedido) -> Pedido:
        cursor = self.conn.execute(
            "INSERT INTO pedidos (cliente, fecha, estado, total) VALUES (?, ?, ?, ?)",
            (pedido.cliente, pedido.fecha, pedido.estado, pedido.total),
        )
        pedido_id = cursor.lastrowid

        for detalle in pedido.detalles:
            self.conn.execute(
                """INSERT INTO detalle_pedido
                   (pedido_id, isbn, cantidad, precio_unitario, subtotal)
                   VALUES (?, ?, ?, ?, ?)""",
                (pedido_id, detalle.isbn, detalle.cantidad,
                 detalle.precio_unitario, detalle.subtotal),
            )

        self.conn.commit()
        pedido.id = pedido_id
        return pedido

    def obtener_todos(self, estado: str | None = None) -> list:
        query = "SELECT * FROM pedidos"
        params = []
        if estado:
            query += " WHERE estado = ?"
            params.append(estado)
        query += " ORDER BY fecha DESC"

        pedidos_rows = self.conn.execute(query, params).fetchall()
        pedidos = []
        for row in pedidos_rows:
            detalle_rows = self.conn.execute(
                "SELECT * FROM detalle_pedido WHERE pedido_id = ?", (row["id"],)
            ).fetchall()
            detalles = [DetallePedido(d["isbn"], d["cantidad"], d["precio_unitario"]) for d in detalle_rows]
            pedido = Pedido(
                cliente=row["cliente"],
                fecha=row["fecha"],
                detalles=detalles,
                pedido_id=row["id"],
                estado=row["estado"],
            )
            pedidos.append(pedido)
        return pedidos

    def obtener_por_id(self, pedido_id: int) -> Pedido | None:
        row = self.conn.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
        if row is None:
            return None

        detalle_rows = self.conn.execute(
            "SELECT * FROM detalle_pedido WHERE pedido_id = ?", (pedido_id,)
        ).fetchall()
        detalles = [DetallePedido(d["isbn"], d["cantidad"], d["precio_unitario"]) for d in detalle_rows]
        return Pedido(
            cliente=row["cliente"],
            fecha=row["fecha"],
            detalles=detalles,
            pedido_id=row["id"],
            estado=row["estado"],
        )

    def actualizar_estado(self, pedido_id: int, estado: str) -> Pedido | None:
        self.conn.execute(
            "UPDATE pedidos SET estado = ? WHERE id = ?",
            (estado, pedido_id),
        )
        self.conn.commit()
        return self.obtener_por_id(pedido_id)
