# 01. Requisitos del Sistema

## 1. Propósito

El sistema es una aplicación web para gestionar el catálogo de una librería, permitir el acceso por roles y registrar compras presenciales de forma administrativa. Está orientado a dos tipos de usuarios:

- Administrador: gestiona libros, registra ventas y consulta reportes básicos.
- Cliente: crea su propia cuenta y consulta el catálogo de libros, precios y disponibilidad.

## 2. Requisitos funcionales

### 2.1 Autenticación y usuarios
- El sistema debe permitir iniciar sesión con un usuario administrador fijo.
- El sistema debe permitir que un cliente cree su propia cuenta.
- El sistema debe mantener una sesión activa durante la navegación.
- El sistema debe permitir cerrar sesión.

### 2.2 Roles de usuario
- El rol administrador puede:
  - gestionar libros (crear, editar, eliminar)
  - registrar ventas presenciales
  - consultar historial de ventas y totales
  - ver reportes de libros más vendidos
- El rol cliente puede:
  - iniciar sesión
  - consultar el catálogo de libros
  - ver disponibilidad y precio
  - navegar sin acceso a ventas ni administración

### 2.3 Gestión de libros
- El sistema debe permitir listar libros.
- El sistema debe permitir buscar libros por título o texto parcial.
- El sistema debe permitir registrar un nuevo libro con datos obligatorios.
- El sistema debe permitir actualizar información del libro.
- El sistema debe permitir eliminar un libro.
- El sistema debe mostrar el stock disponible.

### 2.4 Gestión de ventas
- El administrador debe poder registrar una venta con uno o más libros.
- La venta debe validar que exista stock suficiente.
- Al registrar una venta, el stock debe disminuir correctamente.
- El sistema debe permitir consultar el historial de ventas.
- El sistema debe permitir calcular el total vendido.
- El sistema debe permitir ver los libros más vendidos.

### 2.5 Interfaz de usuario
- El frontend debe mostrar formularios de login y registro.
- El frontend debe ocultar opciones de administración para clientes.
- El frontend debe adaptar su contenido según el rol autenticado.

## 3. Requisitos no funcionales

### 3.1 Usabilidad
- La interfaz debe ser simple, clara y accesible.
- Los usuarios deben poder completar las operaciones principales sin complejidad innecesaria.

### 3.2 Seguridad
- El acceso a acciones administrativas debe restringirse al rol administrador.
- Las sesiones deben proteger el acceso a rutas sensibles.

### 3.3 Mantenibilidad
- El sistema debe organizarse en capas para separar lógica de negocio, acceso a datos y presentación.
- El código debe ser fácil de extender para nuevas funcionalidades.

### 3.4 Rendimiento
- La carga del catálogo debe realizarse en tiempos cortos para un volumen pequeño o mediano de datos.
- Las operaciones de consulta y registro deben responder de forma inmediata en la mayoría de los casos.

### 3.5 Compatibilidad
- El sistema debe funcionar en navegadores modernos.
- El backend debe ejecutarse sobre Flask con SQLite como base de datos local.
