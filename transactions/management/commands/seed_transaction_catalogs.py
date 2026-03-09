from django.core.management.base import BaseCommand
from transactions.models import TransactionStatus, TransactionType


TRANSACTION_STATUSES = [
    {
        "code": "DRAFT",
        "name": "Borrador",
        "description": "La transacción está en captura y puede modificarse.",
        "is_active": True,
    },
    {
        "code": "PENDING",
        "name": "Pendiente",
        "description": "La transacción está registrada y esperando validación o aplicación.",
        "is_active": True,
    },
    {
        "code": "APPLIED",
        "name": "Aplicada",
        "description": "La transacción fue aplicada y ya afectó el inventario.",
        "is_active": True,
    },
    {
        "code": "CANCELLED",
        "name": "Cancelada",
        "description": "La transacción fue cancelada antes de aplicarse.",
        "is_active": True,
    },
    {
        "code": "REVERSED",
        "name": "Revertida",
        "description": "La transacción fue revertida mediante otra operación.",
        "is_active": True,
    },
    {
        "code": "COMPLETED",
        "name": "Completada",
        "description": "La transacción finalizó su ciclo de vida completamente.",
        "is_active": True,
    },
]

TRANSACTION_TYPES = [
    {
        "code": "ENTRY",
        "name": "Entrada",
        "description": "Ingreso de artículos al inventario.",
        "stock_effect": "increase",
        "requires_source_location": False,
        "requires_target_location": True,
        "is_active": True,
    },
    {
        "code": "EXIT",
        "name": "Salida",
        "description": "Salida de artículos del inventario.",
        "stock_effect": "decrease",
        "requires_source_location": True,
        "requires_target_location": False,
        "is_active": True,
    },
    {
        "code": "TRANSFER",
        "name": "Transferencia",
        "description": "Movimiento de artículos entre ubicaciones.",
        "stock_effect": "transfer",
        "requires_source_location": True,
        "requires_target_location": True,
        "is_active": True,
    },
    {
        "code": "ADJ_POS",
        "name": "Ajuste positivo",
        "description": "Incremento manual de stock por corrección de inventario.",
        "stock_effect": "increase",
        "requires_source_location": False,
        "requires_target_location": True,
        "is_active": True,
    },
    {
        "code": "ADJ_NEG",
        "name": "Ajuste negativo",
        "description": "Reducción manual de stock por corrección de inventario.",
        "stock_effect": "decrease",
        "requires_source_location": True,
        "requires_target_location": False,
        "is_active": True,
    },
    {
        "code": "ASSIGN",
        "name": "Asignación",
        "description": "Asignación de un artículo a un usuario o área.",
        "stock_effect": "transfer",
        "requires_source_location": True,
        "requires_target_location": True,
        "is_active": True,
    },
    {
        "code": "RETURN",
        "name": "Devolución",
        "description": "Devolución de un artículo previamente asignado.",
        "stock_effect": "transfer",
        "requires_source_location": True,
        "requires_target_location": True,
        "is_active": True,
    },
]


class Command(BaseCommand):
    help = 'Carga los catálogos base de transacciones: estados y tipos'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando seed de catálogos de transacciones...'))

        self.seed_statuses()
        self.seed_types()

        self.stdout.write(self.style.SUCCESS('✓ Seed de catálogos de transacciones completado'))

    def seed_statuses(self):
        count = 0
        for data in TRANSACTION_STATUSES:
            _, created = TransactionStatus.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'is_active': data['is_active'],
                }
            )
            if created:
                count += 1
                self.stdout.write(f'  - Estado creado: [{data["code"]}] {data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'✓ Estados de transacción: {count} creados'))

    def seed_types(self):
        count = 0
        for data in TRANSACTION_TYPES:
            _, created = TransactionType.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'stock_effect': data['stock_effect'],
                    'requires_source_location': data['requires_source_location'],
                    'requires_target_location': data['requires_target_location'],
                    'is_active': data['is_active'],
                }
            )
            if created:
                count += 1
                self.stdout.write(f'  - Tipo creado: [{data["code"]}] {data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'✓ Tipos de transacción: {count} creados'))
