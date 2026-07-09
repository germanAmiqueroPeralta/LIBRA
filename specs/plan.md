# Plan técnico — Sistema de Venta de Libros

> Este documento responde al **CÓMO**: decisiones técnicas, arquitectura y
> stack elegidos para cumplir lo definido en `spec.md`.

## 1. Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12+, Flask 3, Flask-CORS |
| Base de datos | SQLite (archivo `backend/database.db`) |
| Acceso a datos | `sqlite3` (librería estándar), sin ORM |
| Pruebas | `pytest`, cliente de pruebas de Flask (`test_client`) |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) — sin frameworks |
| Comunicación | HTTP + JSON, API REST |

Se descartó deliberadamente usar un ORM (SQLAlchemy) o un framework de
frontend (React/Vue) porque el objetivo académico es entender cada capa
manualmente, tal como se definió en el documento original del proyecto.

## 2. Arquitectura

Arquitectura en capas (Layered Architecture), inspirada en MVC:

```
Frontend (HTML/CSS/JS)
        │  HTTP (fetch → JSON)
        ▼
Routes / Controllers (Flask Blueprints)
        │  llama a
        ▼
Services (reglas de negocio, validaciones)
        │  llama a
        ▼
Repositories (SQL puro contra SQLite)
        │
        ▼
   SQLite (database.db)
```

**Regla de dependencia**: cada capa solo conoce a la capa inmediatamente
inferior. Las rutas nunca ejecutan SQL directamente; los repositorios nunca
contienen reglas de negocio; los servicios nunca conocen detalles HTTP.

## 3. Estructura de carpetas

```
libreria/
├── backend/
│   ├── app.py                 # Punto de entrada, registra blueprints
│   ├── config.py               # Configuración (rutas, host, puerto)
│   ├── database.py             # Conexión SQLite + creación de esquema
│   ├── routes/                 # Controladores HTTP (Blueprints)
│   │   ├── libros.py
│   │   └── ventas.py
│   ├── models/                 # Entidades planas (sin lógica)
│   │   ├── libro.py
│   │   └── venta.py
│   ├── services/                # Reglas de negocio
│   │   ├── libro_service.py
│   │   └── venta_service.py
│   ├── repositories/           # Acceso a datos (SQL)
│   │   ├── libro_repository.py
│   │   └── venta_repository.py
│   ├── tests/                   # Pruebas unitarias + integración
│   │   ├── conftest.py
│   │   ├── test_libros.py
│   │   ├── test_ventas.py
│   │   └── test_integracion.py
│   └── pytest.ini
├── frontend/
│   ├── index.html               # Dashboard
│   ├── pages/
│   │   ├── libros.html          # CRUD de libros
│   │   └── ventas.html          # Carrito + historial de ventas
│   ├── css/style.css
│   ├── js/
│   │   ├── api.js               # Única capa que hace fetch()
│   │   ├── libros.js
│   │   └── ventas.js
│   └── img/
├── specs/                        # Documentos SDD (este set de archivos)
├── requirements.txt
└── README.md
```

## 4. Modelo de datos (SQLite)

```sql
CREATE TABLE libros (
    isbn      TEXT PRIMARY KEY,
    titulo    TEXT NOT NULL,
    autor     TEXT NOT NULL,
    precio    REAL NOT NULL CHECK (precio >= 0),
    stock     INTEGER NOT NULL CHECK (stock >= 0),
    categoria TEXT
);

CREATE TABLE ventas (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha  TEXT NOT NULL,
    total  REAL NOT NULL
);

CREATE TABLE detalle_venta (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id         INTEGER NOT NULL REFERENCES ventas(id),
    isbn             TEXT NOT NULL REFERENCES libros(isbn),
    cantidad         INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario  REAL NOT NULL,
    subtotal         REAL NOT NULL
);
```

`ventas` y `detalle_venta` se agregaron respecto al documento original
(que solo mencionaba `libros`) porque son necesarios para cumplir RF-12,
RF-13 y RF-14 (historial, total vendido, libros más vendidos).

## 5. Contrato de la API REST

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/libros` | Lista libros (`?buscar=texto` opcional) |
| GET | `/api/libros/<isbn>` | Obtiene un libro |
| POST | `/api/libros` | Registra un libro |
| PUT | `/api/libros/<isbn>` | Actualiza un libro |
| DELETE | `/api/libros/<isbn>` | Elimina un libro |
| POST | `/api/ventas` | Registra una venta (`{"items": [{"isbn","cantidad"}]}`) |
| GET | `/api/ventas` | Lista el historial de ventas |
| GET | `/api/ventas/<id>` | Obtiene una venta puntual |
| GET | `/api/ventas/resumen/total` | Total acumulado vendido |
| GET | `/api/ventas/resumen/mas-vendidos` | Ranking de libros más vendidos |
| GET | `/api/salud` | Chequeo de disponibilidad de la API |

Todas las respuestas son JSON. Errores de negocio devuelven `400`
(dato inválido) o `404` (recurso no encontrado) con `{"error": "mensaje"}`.

## 6. Estrategia de pruebas

- **Unitarias**: prueban `services/` y `repositories/` de forma aislada,
  usando una base de datos SQLite **en memoria** (`:memory:`), sin pasar
  por HTTP. Ejemplo clave: "una venta no debe permitir vender más
  unidades de las disponibles" (pedido explícitamente en el documento
  original del proyecto).
- **Integración**: usan el `test_client` de Flask para probar
  `Controller → Service → Repository → SQLite` juntos, con una base de
  datos temporal en disco (`tmp_path` de pytest). Casos clave: registrar
  un libro y recuperarlo desde la base de datos; realizar una venta y
  verificar que el stock se actualice correctamente.
- Ambas suites corren con `pytest` desde `backend/`.

## 7. Decisiones de diseño relevantes

- **Todo o nada en las ventas**: si una venta tiene varios ítems y uno
  falla la validación de stock, no se descuenta stock de ningún libro
  (se valida todo antes de escribir nada).
- **Conexión por request**: Flask abre una conexión SQLite nueva en
  `before_request` y la cierra en `teardown_request`, evitando compartir
  conexiones entre peticiones concurrentes.
- **Sin ORM**: las consultas SQL están escritas a mano en los
  repositorios, a propósito, para fines de aprendizaje.
- **CORS habilitado**: el frontend se sirve como archivos estáticos
  (por ejemplo con Live Server) desde un origen distinto al backend,
  por eso se habilita `flask-cors`.

## 8. Cómo correr el proyecto

Ver `README.md` en la raíz del proyecto para instrucciones paso a paso.
