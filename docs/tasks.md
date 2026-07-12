# Tareas — Sistema de Venta de Libros

> Desglose ejecutable derivado de `spec.md` (qué) y `plan.md` (cómo).
> `[x]` = ya implementado en esta entrega. `[ ]` = pendiente / mejora futura.
> Úsalo como checklist en VSCode para retomar el proyecto o extenderlo.

## Sprint 0 — Base del proyecto

- [x] Definir estructura de carpetas (backend / frontend / specs)
- [x] Configurar `requirements.txt`
- [x] Configurar `database.py` con creación de esquema (`libros`, `ventas`, `detalle_venta`)
- [x] Configurar `app.py` con Flask + CORS + manejo de conexión por request
- [x] Configurar `pytest.ini`
- [x] Configurar `.vscode/` (tasks, settings, extensiones recomendadas)

## Sprint 1 — Gestión de libros (CRUD)

- [x] Modelo `Libro`
- [x] `LibroRepository`: crear, obtener por ISBN, obtener todos, buscar, actualizar, actualizar stock, eliminar
- [x] `LibroService`: validaciones (campos obligatorios, precio/stock no negativos, ISBN único)
- [x] Rutas `GET/POST/PUT/DELETE /api/libros`
- [x] Frontend: `pages/libros.html` + `js/libros.js` (formulario + tabla + búsqueda + editar + eliminar)
- [x] Pruebas unitarias de repositorio y servicio (`test_libros.py`)
- [x] Pruebas de integración vía API (`test_integracion.py::TestIntegracionLibros`)

## Sprint 2 — Ventas

- [x] Modelos `Venta` y `DetalleVenta`
- [x] `VentaRepository`: crear venta con detalle, obtener todas, obtener por id, libros más vendidos
- [x] `VentaService`: validación de stock, cálculo de total, actualización de stock (todo o nada)
- [x] Rutas `POST/GET /api/ventas`
- [x] Frontend: `pages/ventas.html` + `js/ventas.js` (carrito en memoria + confirmación)
- [x] Prueba clave: "no permitir vender más unidades de las disponibles" (`test_ventas.py`)
- [x] Prueba de integración: "realizar una venta y verificar que el stock se actualice" (`test_integracion.py::TestIntegracionVentas`)

## Sprint 3 — Historial

- [x] Endpoint `GET /api/ventas` (ver ventas)
- [x] Endpoint `GET /api/ventas/resumen/total` (total vendido)
- [x] Endpoint `GET /api/ventas/resumen/mas-vendidos` (libros más vendidos)
- [x] Frontend: dashboard (`index.html`) con métricas y ranking
- [x] Frontend: tabla de historial en `pages/ventas.html`
- [x] Pruebas de integración de historial y resúmenes

## Documentación

- [x] `specs/spec.md` — especificación funcional
- [x] `specs/plan.md` — plan técnico
- [x] `specs/tasks.md` — este archivo
- [x] `README.md` — instrucciones de instalación y ejecución

## Mejoras futuras (fuera del alcance actual, ideas para continuar en VSCode)

- [ ] Autenticación de usuarios (login del vendedor/administrador)
- [ ] Paginación en el listado de libros cuando el catálogo crezca
- [ ] Exportar historial de ventas a PDF o Excel
- [ ] Gráficos en el dashboard (por ejemplo, ventas por día)
- [ ] Dockerizar backend + frontend
- [ ] Migrar la conexión SQLite a un pool o usar SQLAlchemy si el proyecto escala
- [ ] Endpoint de edición/anulación de una venta ya registrada
