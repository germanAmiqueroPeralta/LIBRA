# 📚 Sistema de Venta de Libros — Librería

Sistema web simple para gestionar el catálogo de una librería y registrar
ventas, construido con **arquitectura en capas**, **API REST (Flask)** y
**SQLite**. Frontend en HTML/CSS/JS puro, sin frameworks.

Este proyecto fue construido siguiendo **SDD (Spec-Driven Development)**:
revisa la carpeta [`specs/`](./specs) para ver la especificación funcional
(`spec.md`), el plan técnico (`plan.md`) y el desglose de tareas
(`tasks.md`) antes de tocar el código.

## 🗂️ Estructura

```
libreria/
├── backend/      → API Flask (routes, services, repositories, models, tests)
├── frontend/     → HTML / CSS / JS vanilla
├── specs/        → Documentos SDD (spec, plan, tasks)
├── .vscode/      → Tareas y configuración lista para VSCode
└── requirements.txt
```

Detalle completo de capas y modelo de datos en [`specs/plan.md`](./specs/plan.md).

## ▶️ Cómo correr el proyecto en VSCode

### 1. Abrir el proyecto

Abre la carpeta `libreria/` completa en VSCode (`File > Open Folder`).
Se recomienda instalar las extensiones sugeridas (Python, Live Server) —
VSCode debería ofrecértelas automáticamente al abrir el proyecto.

### 2. Instalar dependencias del backend

Abre una terminal en VSCode (`Ctrl + ñ` / `Ctrl + backtick`) y ejecuta:

```bash
cd backend
pip install -r ../requirements.txt
```

> También puedes usar la tarea ya configurada:
> `Terminal > Run Task... > Backend: Instalar dependencias`

### 3. Levantar el backend (API)

```bash
cd backend
python app.py
```

Debería iniciar en `http://127.0.0.1:5000`. Verifica que funciona
visitando `http://127.0.0.1:5000/api/salud` en el navegador — debe
responder `{"estado": "ok", ...}`.

> Tarea de VSCode equivalente: `Backend: Ejecutar servidor Flask`
> (atajo por defecto: `Ctrl + Shift + B`).

La primera vez que corres el backend se crea automáticamente el archivo
`backend/database.db` con las tablas necesarias — no necesitas crear
nada a mano.

### 4. Abrir el frontend

Con el backend corriendo, abre `frontend/index.html`:

- **Opción recomendada**: clic derecho sobre `index.html` → **"Open with Live Server"**
  (requiere la extensión Live Server, ya sugerida en `.vscode/extensions.json`).
- **Alternativa**: abrir el archivo directamente en el navegador (doble clic).

El frontend consume la API en `http://127.0.0.1:5000` (definido en
`frontend/js/api.js`, constante `API_BASE_URL`). Si cambias el puerto del
backend, actualiza esa constante.

### 5. Ejecutar las pruebas

```bash
cd backend
python -m pytest -v
```

Esto corre **41 pruebas** (unitarias + integración). También disponible
como tarea de VSCode: `Backend: Ejecutar pruebas (unitarias + integración)`
(atajo por defecto de "Run Test Task": `Ctrl + Shift + ,` o desde el
menú `Terminal > Run Task...`).

Para ver cobertura de código:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

## 🧪 Sobre las pruebas

- `backend/tests/test_libros.py` — pruebas **unitarias** del CRUD de libros
  (repositorio + servicio), aisladas con SQLite en memoria.
- `backend/tests/test_ventas.py` — pruebas **unitarias** del servicio de
  ventas: validación de stock, cálculo de totales, actualización de stock.
- `backend/tests/test_integracion.py` — pruebas de **integración**
  (Controller → Service → Repository → SQLite) usando el cliente de
  pruebas de Flask, tal como lo consumiría el frontend real.

## 🌐 Resumen de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/libros` | Listar / buscar libros |
| POST | `/api/libros` | Registrar libro |
| PUT | `/api/libros/<isbn>` | Actualizar libro |
| DELETE | `/api/libros/<isbn>` | Eliminar libro |
| POST | `/api/ventas` | Registrar venta |
| GET | `/api/ventas` | Historial de ventas |
| GET | `/api/ventas/resumen/total` | Total vendido |
| GET | `/api/ventas/resumen/mas-vendidos` | Ranking de más vendidos |

Contrato completo en [`specs/plan.md`](./specs/plan.md#5-contrato-de-la-api-rest).

## 🚀 Próximos pasos sugeridos

Revisa la sección "Mejoras futuras" en [`specs/tasks.md`](./specs/tasks.md)
para ideas de continuación (autenticación, paginación, exportar reportes, etc.).
