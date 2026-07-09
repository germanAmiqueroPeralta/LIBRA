# Especificación — Sistema de Venta de Libros (Librería)

> Este documento sigue la metodología **SDD (Spec-Driven Development)**:
> primero se define **QUÉ** debe hacer el sistema y **POR QUÉ**, sin hablar
> todavía de tecnologías ni de cómo se va a implementar. Eso vive en `plan.md`.
> El desglose en tareas ejecutables vive en `tasks.md`.

## 1. Propósito

Construir un sistema de venta de libros para una librería, que permita:
gestionar el catálogo de libros, registrar ventas descontando el stock
automáticamente, y consultar un historial con estadísticas básicas.

El proyecto tiene también un propósito **académico**: sirve para practicar
arquitectura en capas, una API REST, persistencia con SQLite, pruebas
unitarias/integración y organización profesional de un repositorio.

## 2. Usuarios y roles

- **Vendedor / administrador de la librería**: único rol por ahora. Puede
  gestionar el catálogo y registrar ventas. No hay autenticación en esta
  primera versión (queda fuera de alcance, ver sección 6).

## 3. Requisitos funcionales

### 3.1 Gestión de libros (Sprint 1)

| ID | Requisito | Criterio de aceptación |
|----|-----------|-------------------------|
| RF-01 | Registrar un libro | Dado un ISBN, título, autor, precio y stock válidos, el libro se guarda y aparece en el catálogo. |
| RF-02 | Listar libros | El sistema muestra todos los libros existentes, ordenados por título. |
| RF-03 | Buscar libro | Se puede buscar por título, autor o categoría (coincidencia parcial). |
| RF-04 | Actualizar libro | Se puede modificar título, autor, precio, stock o categoría de un libro existente. El ISBN no se puede cambiar. |
| RF-05 | Eliminar libro | Se puede eliminar un libro del catálogo por su ISBN. |
| RF-06 | Validaciones | No se permite registrar libros con ISBN duplicado, precio negativo o stock negativo. Los campos isbn, título, autor, precio y stock son obligatorios. |

### 3.2 Ventas (Sprint 2)

| ID | Requisito | Criterio de aceptación |
|----|-----------|-------------------------|
| RF-07 | Buscar libro para vender | El vendedor puede elegir un libro del catálogo disponible (con stock > 0). |
| RF-08 | Elegir cantidad | El vendedor indica cuántas unidades desea vender de cada libro. |
| RF-09 | Validar stock | El sistema **no permite vender más unidades de las disponibles**. Si la cantidad solicitada supera el stock, la venta se rechaza con un mensaje claro. |
| RF-10 | Calcular total | El sistema calcula automáticamente el subtotal por libro y el total de la venta. |
| RF-11 | Actualizar stock | Al confirmarse una venta, el stock de cada libro vendido se descuenta automáticamente. Si algún ítem de la venta falla la validación, **ningún** libro pierde stock (todo o nada). |

### 3.3 Historial (Sprint 3)

| ID | Requisito | Criterio de aceptación |
|----|-----------|-------------------------|
| RF-12 | Ver ventas | El sistema lista todas las ventas registradas, con fecha, detalle de libros y total. |
| RF-13 | Total vendido | El sistema muestra la suma de todas las ventas registradas. |
| RF-14 | Libros más vendidos | El sistema muestra un ranking de libros por unidades vendidas. |

## 4. Requisitos no funcionales

- **Usabilidad**: interfaz simple, clara y amigable, usable sin capacitación previa.
- **Persistencia**: los datos deben sobrevivir al reinicio del servidor (SQLite en archivo, no en memoria, en producción/desarrollo).
- **Mantenibilidad**: separación estricta de responsabilidades (arquitectura en capas) para poder evolucionar el sistema sin reescribirlo.
- **Verificabilidad**: toda regla de negocio crítica (validación de stock, cálculo de totales) debe estar cubierta por pruebas automatizadas.

## 5. Reglas de negocio clave

1. Un libro se identifica de forma única por su **ISBN**.
2. El **stock nunca puede ser negativo**.
3. El **precio nunca puede ser negativo**.
4. Una venta no puede registrarse si **algún** ítem excede el stock disponible (operación atómica: todo o nada).
5. El total de una venta es la suma de `cantidad × precio_unitario` de cada ítem.

## 6. Fuera de alcance (por ahora)

- Autenticación / múltiples usuarios o roles.
- Múltiples sucursales.
- Pagos reales (pasarela de pago).
- Devoluciones / notas de crédito.
- Reportes avanzados (gráficos, exportación a PDF/Excel).

Estos ítems pueden convertirse en especificaciones futuras (`spec.md` v2) si el proyecto crece.

## 7. Glosario

- **Libro**: ítem del catálogo, identificado por ISBN.
- **Venta**: transacción compuesta de uno o más ítems (detalle de venta).
- **Detalle de venta**: línea de una venta que referencia un libro, una cantidad y un precio unitario.
- **Stock**: cantidad de unidades disponibles de un libro.
