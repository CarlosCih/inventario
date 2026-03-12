# Se manejan excepciones personalizadas para la API, como errores de validación, autenticación, permisos, etc.
# Estas excepciones pueden ser capturadas y formateadas para proporcionar respuestas de error consistentes a los clientes de la API.
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.views import exception_handler


# ===== Excepciones Base =====
class InventoryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Se ha producido un error en la operación."
    default_code = "inventory_error"

class BusinessRuleViolation(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "La operación viola una regla de negocio."
    default_code = "business_rule_violation"

# ========== EXCEPCIONES DE STOCK ==========

class InsufficientStockException(InventoryException):
    """
    Se lanza cuando no hay suficiente stock disponible
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Stock insuficiente para completar la operación.'
    default_code = 'insufficient_stock'
    
    def __init__(self, item_name=None, available=None, requested=None, location=None):
        if item_name and available is not None and requested is not None:
            detail = (
                f"Stock insuficiente de '{item_name}'. "
                f"Disponible: {available}, Solicitado: {requested}"
            )
            if location:
                detail += f" en ubicación '{location}'"
            self.detail = detail
        else:
            self.detail = self.default_detail


class NegativeStockException(InventoryException):
    """
    Se lanza cuando una operación resultaría en stock negativo
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La operación resultaría en stock negativo.'
    default_code = 'negative_stock'


class StockReservedException(InventoryException):
    """
    Se lanza cuando se intenta usar stock que está reservado
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La cantidad solicitada está reservada y no disponible.'
    default_code = 'stock_reserved'


# ========== EXCEPCIONES DE TRANSACCIONES ==========

class TransactionAlreadyAppliedException(BusinessRuleViolation):
    """
    Se lanza cuando se intenta modificar una transacción ya aplicada
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No se puede modificar una transacción que ya ha sido aplicada.'
    default_code = 'transaction_already_applied'


class TransactionNotAppliedException(BusinessRuleViolation):
    """
    Se lanza cuando se requiere que una transacción esté aplicada pero no lo está
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La transacción debe estar aplicada para realizar esta operación.'
    default_code = 'transaction_not_applied'


class InvalidTransactionTypeException(InventoryException):
    """
    Se lanza cuando el tipo de transacción es inválido para la operación
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El tipo de transacción no es válido para esta operación.'
    default_code = 'invalid_transaction_type'
    
    def __init__(self, transaction_type=None, reason=None):
        if transaction_type and reason:
            self.detail = f"Tipo de transacción '{transaction_type}' inválido: {reason}"
        else:
            self.detail = self.default_detail


class MissingLocationException(InventoryException):
    """
    Se lanza cuando falta una ubicación requerida
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Se requiere especificar una ubicación.'
    default_code = 'missing_location'
    
    def __init__(self, location_type=None):
        if location_type:
            self.detail = f"Se requiere especificar ubicación de {location_type}."
        else:
            self.detail = self.default_detail


# ========== EXCEPCIONES DE ITEMS/ASSETS ==========

class ItemNotFoundException(InventoryException):
    """
    Se lanza cuando no se encuentra un artículo
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Artículo no encontrado.'
    default_code = 'item_not_found'
    
    def __init__(self, item_id=None, item_sku=None):
        if item_id:
            self.detail = f"Artículo con ID {item_id} no encontrado."
        elif item_sku:
            self.detail = f"Artículo con SKU '{item_sku}' no encontrado."
        else:
            self.detail = self.default_detail


class ItemInactiveException(BusinessRuleViolation):
    """
    Se lanza cuando se intenta usar un artículo inactivo
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No se pueden realizar operaciones con artículos inactivos.'
    default_code = 'item_inactive'


class DuplicateSKUException(InventoryException):
    """
    Se lanza cuando se intenta crear un artículo con SKU duplicado
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Ya existe un artículo con este SKU.'
    default_code = 'duplicate_sku'
    
    def __init__(self, sku=None):
        if sku:
            self.detail = f"Ya existe un artículo con el SKU '{sku}'."
        else:
            self.detail = self.default_detail


class DuplicateSerialNumberException(InventoryException):
    """
    Se lanza cuando se intenta crear un asset con número de serie duplicado
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Ya existe un asset con este número de serie.'
    default_code = 'duplicate_serial_number'
    
    def __init__(self, serial_number=None):
        if serial_number:
            self.detail = f"Ya existe un asset con el número de serie '{serial_number}'."
        else:
            self.detail = self.default_detail


class SerialNumberRequiredException(BusinessRuleViolation):
    """
    Se lanza cuando se requiere número de serie pero no se proporciona
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Este artículo requiere número de serie.'
    default_code = 'serial_number_required'


class LotNumberRequiredException(BusinessRuleViolation):
    """
    Se lanza cuando se requiere número de lote pero no se proporciona
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Este artículo requiere número de lote.'
    default_code = 'lot_number_required'


class ExpiredItemException(BusinessRuleViolation):
    """
    Se lanza cuando se intenta usar un artículo caducado
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No se puede usar un artículo caducado.'
    default_code = 'expired_item'
    
    def __init__(self, item_name=None, expiration_date=None):
        if item_name and expiration_date:
            self.detail = f"El artículo '{item_name}' caducó el {expiration_date}."
        else:
            self.detail = self.default_detail


# ========== EXCEPCIONES DE UBICACIONES ==========

class LocationNotFoundException(InventoryException):
    """
    Se lanza cuando no se encuentra una ubicación
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Ubicación no encontrada.'
    default_code = 'location_not_found'


class LocationInactiveException(BusinessRuleViolation):
    """
    Se lanza cuando se intenta usar una ubicación inactiva
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No se pueden realizar operaciones con ubicaciones inactivas.'
    default_code = 'location_inactive'


class SameSourceAndTargetException(BusinessRuleViolation):
    """
    Se lanza cuando la ubicación origen y destino son la misma
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La ubicación de origen y destino no pueden ser la misma.'
    default_code = 'same_source_and_target'


# ========== EXCEPCIONES DE PERMISOS ==========

class InsufficientPermissionsException(APIException):
    """
    Se lanza cuando el usuario no tiene permisos para realizar la acción
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'No tiene permisos suficientes para realizar esta acción.'
    default_code = 'insufficient_permissions'


class CannotDeleteAppliedTransactionException(BusinessRuleViolation):
    """
    Se lanza cuando se intenta eliminar una transacción ya aplicada
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No se pueden eliminar transacciones que ya han sido aplicadas.'
    default_code = 'cannot_delete_applied_transaction'


class OnlyOwnerCanEditException(APIException):
    """
    Se lanza cuando un usuario intenta editar algo que no le pertenece
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Solo el creador puede editar este recurso.'
    default_code = 'only_owner_can_edit'


# ========== EXCEPCIONES DE VALIDACIÓN ==========

class InvalidQuantityException(InventoryException):
    """
    Se lanza cuando la cantidad es inválida
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La cantidad debe ser mayor a cero.'
    default_code = 'invalid_quantity'


class EmptyTransactionException(BusinessRuleViolation):
    """
    Se lanza cuando se intenta crear una transacción sin detalles
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La transacción debe incluir al menos un detalle.'
    default_code = 'empty_transaction'


class InvalidDateException(InventoryException):
    """
    Se lanza cuando una fecha es inválida
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La fecha proporcionada es inválida.'
    default_code = 'invalid_date'


# ========== HANDLER PERSONALIZADO ==========

def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones para toda la API
    
    Uso: En settings.py agregar:
    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler'
    }
    """    
    # Llamar al manejador por defecto primero
    response = exception_handler(exc, context)
    
    if response is not None:
        # Obtener el código de error
        error_code = getattr(exc, 'default_code', 'error')
        
        # Obtener el mensaje - manejar diferentes estructuras
        if isinstance(response.data, dict):
            # Si es un dict, intentar obtener 'detail'
            message = response.data.get('detail', response.data)
        elif isinstance(response.data, list):
            # Si es una lista (validation errors), convertir a string
            message = response.data
        else:
            # Fallback a string de la excepción
            message = str(exc)
        
        # Personalizar la respuesta
        custom_response = {
            'error': True,
            'error_code': error_code,
            'message': message,
            'status_code': response.status_code
        }
        
        # Agregar información adicional si está disponible
        if hasattr(exc, 'get_full_details'):
            try:
                custom_response['details'] = exc.get_full_details()
            except:
                pass
        
        response.data = custom_response
    
    return response