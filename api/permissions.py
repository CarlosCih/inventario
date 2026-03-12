#Roles
# - Admin: Full acceso a todas las funcionalidades del sistema, gestion de usuarios, catalogos, inventario, transacciones, reportes, etc.
# - Encargados/Gestores: Acceso a quienes manejan el inventario, catalogos, aprueban las transacciones. No pueden gestionar usuarios ni ver reportes financieros.
# - Usuarios: Acceso limitado; pueden realizar consultas al inventario(only lectura), crear transacciones (requieren aprobación), editar sus propias transacciones, pero sin modificar catalogos, inventario directamente.
# - Consultor/Auditor: Acceso unicamente a reportes e historial de transacciones, sin capacidad de modificar nada en el sistema.

from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a usuarios con rol de admin acceder a ciertas vistas.
    Se asume que el modelo User tiene un campo 'role' que define el rol del usuario.
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_authenticated and request.user.role == 'admin'
    
class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado para permitir a usuarios con rol de manager o admin acceder a ciertas vistas.
    """

    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False
        #Lectura: todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        # Escritura: Admin o Encargado
        if request.user.is_staff or request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Encargado').exists()
    
class IsStandardUser(permissions.BasePermission):
    """
    Permiso personalizado para permitir a usuarios con rol de standard user acceder a ciertas vistas.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Lectura: todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        # Escritura: Solo admin 
        if request.user.is_staff or request.user.is_superuser:
            return True
        # Crear: Usuario, Encargado
        if request.method == 'POST':
            return request.user.groups.filter(name__in=['Encargado','Usuario']).exists()
        # Actualizar/Eliminar: Solo admin o el encargado
        if request.method in ['PUT', 'PATCH','DELETE']:
            return request.user.groups.filter(name='Encargado').exists()
        return False
    
class CanManageTransactions(permissions.BasePermission):
    """
    Permisoa para transacciones:
    - Lectura: Todos los autenticados
    - Crear: Usuario, Encargado, Admin
    - Editar propias no aplicadas: Usuario
    - Editar cualquiera: Encargado, Admin
    - Eliminar: Admin, Encargado (solo si no está aplicada)
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Lectura: todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        # Crear: Usuario o superiores
        if request.method == 'POST':
            if request.user.is_staff or request.user.is_superuser:
                return True
            return request.user.groups.filter(name__in=['Encargado','Usuario']).exists()
        # Actualizar/Eliminar: necesita verificacion a nivel de objeto
        if request.method in ['PUT','PATCH','DELETE']:
            if request.user.is_staff or request.user.is_superuser:
                return True
            return request.user.groups.filter(name__in=['Encargado','Usuario']).exists()
        return False
    def has_object_permissions(self, request, view, obj):
        """
        Permisos a nivel de objetos para transacciones
        """
        #Admin
        if request.user.is_staff or request.user.is_superuser:
            return True
        #Encargado
        if request.user.groups.filter(name='Encargado').exists():
            return True
        #Usuario: solo puede editar sus propias transacciones no aplicadas
        if request.user.groups.filter(name='Usuario').exists():
            if request.method in ['PUT','PATCH','DELETE']:
                return obj.created_by == request.user and not obj.is_applied
        return False

class IsReadOnly(permissions.BasePermission):
    """
    Permiso solo lectura, para consultores o auditores
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.method in permissions.SAFE_METHODS