# 05. Pruebas del Sistema

## 1. Estrategia de pruebas

El proyecto utiliza pruebas unitarias e integración para validar el comportamiento del sistema.

## 2. Pruebas unitarias

Se enfocan en componentes aislados:

- pruebas del repositorio de libros
- pruebas del servicio de libros
- pruebas del servicio de ventas

### Casos cubiertos
- crear y obtener un libro
- actualizar stock
- eliminar un libro
- validar precio y stock negativos
- validar stock insuficiente en ventas
- validar cantidades inválidas
- calcular totales y libros más vendidos

## 3. Pruebas de integración

Se validan flujos completos desde la API hasta la base de datos real.

### Casos cubiertos
- registrar un libro y recuperarlo desde la base de datos
- listar libros desde la API
- actualizar y eliminar libros vía API
- registrar ventas y verificar el stock actualizado
- rechazar ventas con stock insuficiente
- validar el historial de ventas
- validar totales y ranking de productos más vendidos
- validar login, registro y control de roles

## 4. Ejecución de pruebas

Comando utilizado:

```bash
cd backend
python -m pytest -v
```

## 5. Resultado verificado

Se ejecutó la suite de pruebas y el resultado fue:

- 45 pruebas ejecutadas
- 45 aprobadas
- 0 fallos

## 6. Valor de las pruebas

Las pruebas ayudan a asegurar que:
- el catálogo funciona correctamente
- el stock se actualiza como corresponde
- las ventas no se registran si no hay inventario suficiente
- los roles de administrador y cliente se respetan
