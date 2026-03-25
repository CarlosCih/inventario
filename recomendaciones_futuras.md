# Recomendaciones que se pueden implementar.

## Proteger ediciones de transacciones aplicadas-

- clean()
- save()
- admin
- serializer

## Kardex
Se pueden realizar consultas para alimentar los reporte o auditorias
- movimientos por articulos
- movimientos por ubicaciones
- movimientos por fechas

## Auditorias
Algunos de los campos utiles son:
- created_by
- applied_by
- cancelled_by
- reversed_by

## Control de permisos
Restingir las operaciones por permisos especifico, inclusos con grupos que tengan determinados permisos

## Manejo de logs
Tener un registros de logs para encontrar y aislar errores o fallos en la aplicacion

## Reversion de transacciones
Realizar una regresion de las transacciones

## Login
Tener un panel para incio de sesion

## Logout
Manejar un cierre de sesion

# Asignacion
El modulo debe cubrir:
- Asignación de inventario
    - Asignar uno o varios items
    - definir responsable
    - definir ubicacion
    - Fecha de asignación

- Devolucion
    - Liberar asignaciones
    - Registrar fecha de retorno

- Historial
    - Daber quien tuvo que y cuando
    - Auditoria completa

- Esta de asignacion

