"""
tests/test_integracion.py
Pruebas de INTEGRACIÓN: usan el cliente de pruebas de Flask para
verificar que Controller -> Service -> Repository -> SQLite funcionan
correctamente en conjunto, tal como lo haría el frontend real.
"""


class TestIntegracionLibros:

    def _login_admin(self, app_cliente):
        return app_cliente.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

    def test_registrar_y_recuperar_libro_desde_bd(self, app_cliente, libro_ejemplo):
        """Registrar un libro y luego recuperarlo desde la base de datos real."""
        self._login_admin(app_cliente)
        respuesta_post = app_cliente.post("/api/libros", json=libro_ejemplo)
        assert respuesta_post.status_code == 201

        respuesta_get = app_cliente.get(f"/api/libros/{libro_ejemplo['isbn']}")
        assert respuesta_get.status_code == 200
        data = respuesta_get.get_json()
        assert data["titulo"] == libro_ejemplo["titulo"]
        assert data["stock"] == libro_ejemplo["stock"]

    def test_listar_libros_incluye_el_registrado(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        respuesta = app_cliente.get("/api/libros")
        data = respuesta.get_json()
        assert any(libro["isbn"] == libro_ejemplo["isbn"] for libro in data)

    def test_registrar_libro_invalido_retorna_400(self, app_cliente):
        self._login_admin(app_cliente)
        respuesta = app_cliente.post("/api/libros", json={"titulo": "Sin ISBN"})
        assert respuesta.status_code == 400
        assert "error" in respuesta.get_json()

    def test_actualizar_libro_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        respuesta = app_cliente.put(
            f"/api/libros/{libro_ejemplo['isbn']}", json={"precio": 99.99}
        )
        assert respuesta.status_code == 200
        assert respuesta.get_json()["precio"] == 99.99

    def test_eliminar_libro_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        respuesta = app_cliente.delete(f"/api/libros/{libro_ejemplo['isbn']}")
        assert respuesta.status_code == 200

        respuesta_get = app_cliente.get(f"/api/libros/{libro_ejemplo['isbn']}")
        assert respuesta_get.status_code == 404

    def test_buscar_libro_via_query_param(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        respuesta = app_cliente.get("/api/libros?buscar=Soledad")
        data = respuesta.get_json()
        assert len(data) == 1


class TestIntegracionVentas:

    def _login_admin(self, app_cliente):
        return app_cliente.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

    def test_realizar_venta_y_verificar_stock_actualizado(self, app_cliente, libro_ejemplo):
        """
        Caso de integración explícito del documento:
        'Realizar una venta y verificar que el stock se actualice correctamente.'
        """
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)

        respuesta_venta = app_cliente.post(
            "/api/ventas",
            json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 4}]},
        )
        assert respuesta_venta.status_code == 201
        venta = respuesta_venta.get_json()
        assert venta["total"] == 4 * libro_ejemplo["precio"]

        libro_actualizado = app_cliente.get(f"/api/libros/{libro_ejemplo['isbn']}").get_json()
        assert libro_actualizado["stock"] == libro_ejemplo["stock"] - 4

    def test_venta_con_stock_insuficiente_retorna_400_y_no_afecta_stock(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)

        respuesta = app_cliente.post(
            "/api/ventas",
            json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 999}]},
        )
        assert respuesta.status_code == 400

        libro = app_cliente.get(f"/api/libros/{libro_ejemplo['isbn']}").get_json()
        assert libro["stock"] == libro_ejemplo["stock"]  # intacto

    def test_historial_de_ventas_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        app_cliente.post("/api/ventas", json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 2}]})
        app_cliente.post("/api/ventas", json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 1}]})

        respuesta = app_cliente.get("/api/ventas")
        assert respuesta.status_code == 200
        assert len(respuesta.get_json()) == 2

    def test_obtener_venta_por_id_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        respuesta_venta = app_cliente.post("/api/ventas", json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 2}]})
        venta = respuesta_venta.get_json()

        respuesta = app_cliente.get(f"/api/ventas/{venta['id']}")
        assert respuesta.status_code == 200
        data = respuesta.get_json()
        assert data["id"] == venta["id"]
        assert data["detalles"][0]["isbn"] == libro_ejemplo["isbn"]
        assert data["detalles"][0]["titulo"] == libro_ejemplo["titulo"]
        assert data["detalles"][0]["cantidad"] == 2

    def test_total_vendido_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        app_cliente.post("/api/ventas", json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 2}]})

        respuesta = app_cliente.get("/api/ventas/resumen/total")
        assert respuesta.status_code == 200
        assert respuesta.get_json()["total_vendido"] == 2 * libro_ejemplo["precio"]

    def test_total_vendido_por_dia_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        app_cliente.post("/api/ventas", json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 1}]})

        respuesta = app_cliente.get("/api/ventas/resumen/total?periodo=dia")
        assert respuesta.status_code == 200
        assert respuesta.get_json()["total_vendido"] == 1 * libro_ejemplo["precio"]
        assert respuesta.get_json()["periodo"] == "dia"

    def test_total_vendido_por_mes_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        app_cliente.post("/api/ventas", json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 2}]})

        respuesta = app_cliente.get("/api/ventas/resumen/total?periodo=mes")
        assert respuesta.status_code == 200
        assert respuesta.get_json()["total_vendido"] == 2 * libro_ejemplo["precio"]
        assert respuesta.get_json()["periodo"] == "mes"

    def test_total_vendido_por_anio_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        app_cliente.post("/api/ventas", json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 3}]})

        respuesta = app_cliente.get("/api/ventas/resumen/total?periodo=anio")
        assert respuesta.status_code == 200
        assert respuesta.get_json()["total_vendido"] == 3 * libro_ejemplo["precio"]
        assert respuesta.get_json()["periodo"] == "anio"

    def test_total_vendido_periodo_invalido_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        app_cliente.post("/api/ventas", json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 1}]})

        respuesta = app_cliente.get("/api/ventas/resumen/total?periodo=semana")
        assert respuesta.status_code == 400
        assert "error" in respuesta.get_json()

    def test_libros_mas_vendidos_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)
        app_cliente.post("/api/ventas", json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 3}]})

        respuesta = app_cliente.get("/api/ventas/resumen/mas-vendidos")
        data = respuesta.get_json()
        assert data[0]["isbn"] == libro_ejemplo["isbn"]
        assert data[0]["total_vendido"] == 3


class TestAutenticacion:
    def test_admin_registra_compra_presencial_y_baja_stock(self, app_cliente, libro_ejemplo):
        app_cliente.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        app_cliente.post("/api/libros", json=libro_ejemplo)

        respuesta = app_cliente.post(
            "/api/ventas",
            json={"items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 2}]},
        )

        assert respuesta.status_code == 201
        libro_actualizado = app_cliente.get(f"/api/libros/{libro_ejemplo['isbn']}").get_json()
        assert libro_actualizado["stock"] == libro_ejemplo["stock"] - 2

    def test_registro_de_cliente_crea_cuenta(self, app_cliente):
        respuesta = app_cliente.post(
            "/api/auth/register",
            json={"username": "nuevo_cliente", "password": "miClave123"},
        )
        assert respuesta.status_code == 201
        data = respuesta.get_json()
        assert data["user"]["role"] == "cliente"
        assert data["user"]["username"] == "nuevo_cliente"

    def test_login_de_admin_retorna_rol_admin(self, app_cliente):
        respuesta = app_cliente.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert respuesta.status_code == 200
        data = respuesta.get_json()
        assert data["user"]["role"] == "admin"
        assert data["user"]["username"] == "admin"

    def test_login_de_cliente_retorna_rol_cliente(self, app_cliente):
        app_cliente.post(
            "/api/auth/register",
            json={"username": "cliente_prueba", "password": "cliente123"},
        )
        respuesta = app_cliente.post(
            "/api/auth/login",
            json={"username": "cliente_prueba", "password": "cliente123"},
        )
        assert respuesta.status_code == 200
        data = respuesta.get_json()
        assert data["user"]["role"] == "cliente"
        assert data["user"]["username"] == "cliente_prueba"


class TestIntegracionPedidos:

    def _login_admin(self, app_cliente):
        return app_cliente.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

    def test_crear_y_confirmar_pedido_via_api(self, app_cliente, libro_ejemplo):
        self._login_admin(app_cliente)
        app_cliente.post("/api/libros", json=libro_ejemplo)

        respuesta = app_cliente.post(
            "/api/pedidos",
            json={"cliente": "Martin", "items": [{"isbn": libro_ejemplo["isbn"], "cantidad": 3}]},
        )
        assert respuesta.status_code == 201
        pedido = respuesta.get_json()
        assert pedido["estado"] == "pendiente"
        assert pedido["total"] == 3 * libro_ejemplo["precio"]

        respuesta_listar = app_cliente.get("/api/pedidos?estado=pendiente")
        assert respuesta_listar.status_code == 200
        assert any(p["id"] == pedido["id"] for p in respuesta_listar.get_json())

        respuesta_confirmar = app_cliente.post(f"/api/pedidos/{pedido['id']}/confirmar")
        assert respuesta_confirmar.status_code == 200
        assert respuesta_confirmar.get_json()["estado"] == "confirmado"

    def test_listar_pedidos_estado_invalido_retorna_400(self, app_cliente):
        self._login_admin(app_cliente)
        respuesta = app_cliente.get("/api/pedidos?estado=invalido")
        assert respuesta.status_code == 400
        assert "error" in respuesta.get_json()

    def test_confirmar_pedido_inexistente_retorna_400(self, app_cliente):
        self._login_admin(app_cliente)
        respuesta = app_cliente.post("/api/pedidos/9999/confirmar")
        assert respuesta.status_code == 400
        assert "error" in respuesta.get_json()


class TestSalud:
    def test_endpoint_salud(self, app_cliente):
        respuesta = app_cliente.get("/api/salud")
        assert respuesta.status_code == 200
        assert respuesta.get_json()["estado"] == "ok"
