from django.db import models
from django.conf import settings


# Create your models here.
class Assignment(models.Model):
    STATUS_ASSIGNMENT_CHOICES = [
        ("PENDING", "Pendiente"),
        ("PENDING_APPROVAL", "Pendiente de Aprobación"),
        ("IN_PROGRESS", "En Progreso"),
        ("ON_HOLD", "En Espera"),
        ("COMPLETED", "Completado"),
        ("DRAFT", "Borrador"),
        ("APPROVED", "Aprobado"),
        ("REJECTED", "Rechazado"),
        ("RETURNED", "Devuelto"),
        ("CANCELLED", "Cancelado"),
        ("TRANSFERRED", "Transferido"),
        ("LOST", "Perdido"),
        ("DAMAGED", "Dañado"),
        ("ARCHIVED", "Archivado"),
        ("CLOSED", "Cerrado"),
        ("DELIVERED", "Entregado"),
    ]

    TYPE_ASSIGNMENT_CHOICES = [
        ("LOAN", "Préstamo"),
        ("TEMPORARY", "Temporal"),
        ("PERMANENT", "Permanente"),
        ("CONSUPTION", "Consumo"),
        ("MAINTENANCE", "Mantenimiento"),
        ("CUSTODY", "Custodia"),
        ("OTHER", "Otro"),
    ]

    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Folio"
    )

    assignment_type = models.CharField(
        max_length=20,
        choices=TYPE_ASSIGNMENT_CHOICES,
        verbose_name="Tipo de Asignación",
        db_index=True
    )

    assignment_status = models.CharField(
        max_length=20,
        choices=STATUS_ASSIGNMENT_CHOICES,
        verbose_name="Estatus de Asignación",
        db_index=True
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Solicitado por"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="assigned_to",
        verbose_name="Asignado a"
    )

    assignment_to_area = models.ForeignKey(
        'locations.Area',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Área de Asignación"
    )

    aproved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="aproved_by",
        verbose_name="Aprobado por"
    )

    returned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="returned_by",
        verbose_name="Devuelto por"
    )

    delivered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="delivered_by",
        verbose_name="Entregado por"
    )


    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="received_by",
        verbose_name="Recibido por"
    )

    origin_location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
        related_name="origin_location",
        null=True,
        blank=True,
        verbose_name="Ubicación de Origen"
    )

    expected_return_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Devolución Esperada"
    )

    aproved_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Aprobación")
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Devolución")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Entrega")
    received_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Recepción")
    acknowledgment = models.TextField(blank=True, null=True, verbose_name="Acuse de Recibo")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Cierre")

    purpose = models.TextField(blank=True, null=True, verbose_name="Propósito de la Asignación")
    comments = models.TextField(blank=True, null=True, verbose_name="Comentarios")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} - {self.get_assignment_type_display()} - {self.get_assignment_status_display()}"
    

class AssignmentLine(models.Model):
    STATUS_PENDING = "pending"
    STATUS_DELIVERED = "delivered"
    STATUS_PARTIALLY_RETURNED = "partially_returned"
    STATUS_RETURNED = "returned"
    STATUS_LOST = "lost"
    STATUS_DAMAGED = "damaged"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pendiente"),
        (STATUS_DELIVERED, "Entregado"),
        (STATUS_PARTIALLY_RETURNED, "Parcialmente devuelto"),
        (STATUS_RETURNED, "Devuelto"),
        (STATUS_LOST, "Perdido"),
        (STATUS_DAMAGED, "Dañado"),
        (STATUS_CANCELLED, "Cancelado"),
    )

    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="lines"
    )

    item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="assignment_lines"
    )

    stock = models.ForeignKey(
        "inventory.Stock",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="assignment_lines"
    )

    quantity_assigned = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        verbose_name="Cantidad asignada"
    )

    quantity_returned = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=0,
        verbose_name="Cantidad devuelta"
    )

    quantity_pending = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=0,
        verbose_name="Cantidad pendiente"
    )

    unit_cost_snapshot = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Costo unitario al asignar"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )

    delivered_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Detalle de asignación"
        verbose_name_plural = "Detalles de asignación"

class AssignmentAsset(models.Model):
    line = models.ForeignKey(
        "assignments.AssignmentLine",
        on_delete=models.CASCADE,
        related_name="assets"
    )

    asset = models.ForeignKey(
        "inventory.ItemAsset",
        on_delete=models.PROTECT,
        related_name="assignment_assets"
    )

    is_returned = models.BooleanField(default=False, db_index=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    delivery_condition = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Condición de entrega"
    )

    return_condition = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Condición de devolución"
    )

    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Activo asignado"
        verbose_name_plural = "Activos asignados"

class AssignmentEvent(models.Model):
    EVENT_CREATED = "CREATED"
    EVENT_SUBMITTED = "SUBMITTED"
    EVENT_APPROVED = "APPROVED"
    EVENT_REJECTED = "REJECTED"
    EVENT_DELIVERED = "DELIVERED"
    EVENT_ACKNOWLEDGED = "ACKNOWLEDGED"
    EVENT_RETURNED = "RETURNED"
    EVENT_CANCELLED = "CANCELLED"
    EVENT_LOST = "LOST"
    EVENT_DAMAGED = "DAMAGED"
    EVENT_COMMENT = "COMMENT"

    EVENT_CHOICES = [
        (EVENT_CREATED, "Creada"),
        (EVENT_SUBMITTED, "Enviada"),
        (EVENT_APPROVED, "Aprobada"),
        (EVENT_REJECTED, "Rechazada"),
        (EVENT_DELIVERED, "Entregada"),
        (EVENT_ACKNOWLEDGED, "Acuse de Recibo"),
        (EVENT_RETURNED, "Devuelta"),
        (EVENT_CANCELLED, "Cancelada"),
        (EVENT_LOST, "Perdida"),
        (EVENT_DAMAGED, "Dañada"),
        (EVENT_COMMENT, "Comentario"),
    ]

    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="events",
    )

    event_type = models.CharField(
        max_length=30,
        choices=EVENT_CHOICES,
        verbose_name="Tipo de Evento",
        db_index=True
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Realizado por"
    )

    event_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Evento")
    comments = models.TextField(blank=True, null=True, verbose_name="Comentarios")

    metadata = models.JSONField(blank=True, null=True, verbose_name="Metadatos del Evento", default=dict)

    class Meta:
        verbose_name = "Evento de Asignación"
        verbose_name_plural = "Eventos de Asignación"
        ordering = ["-event_at"]



# Sirve para almacenar documentos relacionados con la asignación, como responsivas, actas de entrega, fotos, firmas, comprobantes.
class AssignmentDocument(models.Model):
    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="documents",
    )

    name = models.CharField(max_length=250, verbose_name="Nombre del documento")
    file = models.FileField(upload_to="assignment_documents/", verbose_name="Archivo")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Subido por"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Subido el")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        verbose_name = "Documento de Asignación"
        verbose_name_plural = "Documentos de Asignación"
        ordering = ["-created_at"]
