from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from transactions.models import (
    TransactionType,
    TransactionStatus,
    InventoryTransaction,
    TransactionDetail
)
from inventory.models import Item
from locations.models import Location
from decimal import Decimal
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Carga datos iniciales para transacciones de inventario'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando seed de transacciones...'))
        
        # Verificar datos previos necesarios
        if not self.verify_dependencies():
            return
        
        # Seed Transacciones
        self.seed_transactions()
        
        self.stdout.write(self.style.SUCCESS('✓ Seed de transacciones completado exitosamente'))

    def verify_dependencies(self):
        """Verifica que existan los datos previos necesarios"""
        self.stdout.write('Verificando dependencias...')
        
        if not TransactionType.objects.exists():
            self.stdout.write(self.style.ERROR(
                '✗ Error: No hay tipos de transacción. Deben crearse primero desde el admin.'
            ))
            return False
        
        if not TransactionStatus.objects.exists():
            self.stdout.write(self.style.ERROR(
                '✗ Error: No hay estados de transacción. Deben crearse primero desde el admin.'
            ))
            return False
        
        if not Item.objects.exists():
            self.stdout.write(self.style.ERROR(
                '✗ Error: No hay items. Ejecute primero: python manage.py seed_inventory'
            ))
            return False
        
        if not Location.objects.exists():
            self.stdout.write(self.style.ERROR(
                '✗ Error: No hay ubicaciones. Ejecute primero: python manage.py seed_locations'
            ))
            return False
        
        if not User.objects.exists():
            self.stdout.write(self.style.ERROR(
                '✗ Error: No hay usuarios en el sistema. Cree un superusuario primero.'
            ))
            return False
        
        self.stdout.write(self.style.SUCCESS('✓ Todas las dependencias están disponibles'))
        return True

    def seed_transactions(self):
        """Crea transacciones de ejemplo con diferentes tipos y estados"""
        
        # Obtener datos necesarios
        try:
            # Tipos de transacción
            type_entry = TransactionType.objects.get(code='ENTRY')
            type_exit = TransactionType.objects.get(code='EXIT')
            type_transfer = TransactionType.objects.get(code='TRANSFER')
            type_adjust_pos = TransactionType.objects.get(code='ADJ_POS')
            type_adjust_neg = TransactionType.objects.get(code='ADJ_NEG')
            type_assign = TransactionType.objects.get(code='ASSIGN')
            type_return = TransactionType.objects.get(code='RETURN')
            
            # Estados
            status_draft = TransactionStatus.objects.get(code='DRAFT')
            status_pending = TransactionStatus.objects.get(code='PENDING')
            status_applied = TransactionStatus.objects.get(code='APPLIED')
            status_cancelled = TransactionStatus.objects.get(code='CANCELLED')
            
        except (TransactionType.DoesNotExist, TransactionStatus.DoesNotExist) as e:
            self.stdout.write(self.style.ERROR(
                f'✗ Error: Faltan tipos o estados de transacción requeridos. {str(e)}'
            ))
            return
        
        # Obtener items y ubicaciones
        items = list(Item.objects.all()[:10])
        locations = list(Location.objects.filter(is_active=True)[:5])
        
        if not items or not locations:
            self.stdout.write(self.style.ERROR(
                '✗ Error: No hay suficientes items o ubicaciones disponibles.'
            ))
            return
        
        # Obtener usuario para crear transacciones
        user = User.objects.first()
        
        # Contador de transacciones creadas
        transaction_count = 0
        detail_count = 0
        
        # 1. ENTRADA DE INVENTARIO - Aplicada
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_entry,
            status=status_applied,
            reference='PO-2026-001',
            number='ENT-2026-001',
            notes='Entrada inicial de mercancía por compra',
            performed_at=timezone.now() - timedelta(days=30),
            created_by=user,
            is_applied=True,
            applied_at=timezone.now() - timedelta(days=30)
        )
        
        # Crear detalles para la entrada
        for i in range(3):
            item = items[i % len(items)]
            TransactionDetail.objects.create(
                transaction=transaction,
                item=item,
                quantity=Decimal(str(random.randint(10, 50))),
                target_location=locations[0],
                unit_cost=Decimal(str(random.uniform(100, 1000))).quantize(Decimal('0.01')),
                notes=f'Entrada de {item.name}'
            )
            detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # 2. ENTRADA DE INVENTARIO - Borrador
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_entry,
            status=status_draft,
            reference='PO-2026-002',
            number='ENT-2026-002',
            notes='Entrada pendiente de confirmación',
            performed_at=timezone.now(),
            created_by=user,
            is_applied=False
        )
        
        for i in range(2):
            item = items[(i + 3) % len(items)]
            TransactionDetail.objects.create(
                transaction=transaction,
                item=item,
                quantity=Decimal(str(random.randint(5, 20))),
                target_location=locations[1],
                unit_cost=Decimal(str(random.uniform(100, 1000))).quantize(Decimal('0.01'))
            )
            detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # 3. SALIDA DE INVENTARIO - Aplicada
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_exit,
            status=status_applied,
            reference='SO-2026-001',
            number='SAL-2026-001',
            notes='Salida por consumo interno',
            performed_at=timezone.now() - timedelta(days=15),
            created_by=user,
            is_applied=True,
            applied_at=timezone.now() - timedelta(days=15)
        )
        
        for i in range(2):
            item = items[i % len(items)]
            TransactionDetail.objects.create(
                transaction=transaction,
                item=item,
                quantity=Decimal(str(random.randint(3, 10))),
                source_location=locations[0],
                notes=f'Salida de {item.name}'
            )
            detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # 4. TRANSFERENCIA - Pendiente
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_transfer,
            status=status_pending,
            reference='TRF-2026-001',
            number='TRF-2026-001',
            notes='Transferencia entre ubicaciones',
            performed_at=timezone.now() - timedelta(days=5),
            created_by=user,
            is_applied=False
        )
        
        item = items[0]
        TransactionDetail.objects.create(
            transaction=transaction,
            item=item,
            quantity=Decimal('5.00'),
            source_location=locations[0],
            target_location=locations[1],
            notes=f'Transferencia de {item.name}'
        )
        detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # 5. AJUSTE POSITIVO - Aplicado
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_adjust_pos,
            status=status_applied,
            reference='AJU-POS-001',
            number='AJU-POS-2026-001',
            notes='Ajuste por corrección de inventario físico',
            performed_at=timezone.now() - timedelta(days=10),
            created_by=user,
            is_applied=True,
            applied_at=timezone.now() - timedelta(days=10)
        )
        
        item = items[1]
        TransactionDetail.objects.create(
            transaction=transaction,
            item=item,
            quantity=Decimal('3.00'),
            target_location=locations[0],
            notes='Diferencia encontrada en inventario físico'
        )
        detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # 6. AJUSTE NEGATIVO - Aplicado
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_adjust_neg,
            status=status_applied,
            reference='AJU-NEG-001',
            number='AJU-NEG-2026-001',
            notes='Ajuste por corrección de inventario - merma',
            performed_at=timezone.now() - timedelta(days=8),
            created_by=user,
            is_applied=True,
            applied_at=timezone.now() - timedelta(days=8)
        )
        
        item = items[2]
        TransactionDetail.objects.create(
            transaction=transaction,
            item=item,
            quantity=Decimal('2.00'),
            source_location=locations[0],
            notes='Merma detectada en inventario'
        )
        detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # 7. ASIGNACIÓN - Aplicada
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_assign,
            status=status_applied,
            reference='ASG-2026-001',
            number='ASG-2026-001',
            notes='Asignación de equipo a usuario',
            performed_at=timezone.now() - timedelta(days=20),
            created_by=user,
            is_applied=True,
            applied_at=timezone.now() - timedelta(days=20)
        )
        
        # Buscar un item serializado si existe
        serialized_item = Item.objects.filter(is_serialized=True).first()
        if serialized_item:
            TransactionDetail.objects.create(
                transaction=transaction,
                item=serialized_item,
                quantity=Decimal('1.00'),
                source_location=locations[0],
                target_location=locations[2] if len(locations) > 2 else locations[1],
                notes=f'Asignación de {serialized_item.name} a usuario'
            )
            detail_count += 1
        else:
            # Si no hay items serializados, usar cualquier item
            item = items[3 % len(items)]
            TransactionDetail.objects.create(
                transaction=transaction,
                item=item,
                quantity=Decimal('1.00'),
                source_location=locations[0],
                target_location=locations[2] if len(locations) > 2 else locations[1],
                notes=f'Asignación de {item.name}'
            )
            detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # 8. DEVOLUCIÓN - Aplicada
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_return,
            status=status_applied,
            reference='DEV-2026-001',
            number='DEV-2026-001',
            notes='Devolución de artículo previamente asignado',
            performed_at=timezone.now() - timedelta(days=3),
            created_by=user,
            is_applied=True,
            applied_at=timezone.now() - timedelta(days=3)
        )
        
        item = items[4 % len(items)]
        TransactionDetail.objects.create(
            transaction=transaction,
            item=item,
            quantity=Decimal('1.00'),
            source_location=locations[2] if len(locations) > 2 else locations[1],
            target_location=locations[0],
            notes=f'Devolución de {item.name}'
        )
        detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # 9. ENTRADA - Cancelada
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_entry,
            status=status_cancelled,
            reference='PO-2026-999',
            number='ENT-2026-999',
            notes='Entrada cancelada por error en el pedido',
            performed_at=timezone.now() - timedelta(days=25),
            created_by=user,
            is_applied=False
        )
        
        item = items[5 % len(items)]
        TransactionDetail.objects.create(
            transaction=transaction,
            item=item,
            quantity=Decimal('10.00'),
            target_location=locations[0],
            unit_cost=Decimal('250.00'),
            notes='Transacción cancelada'
        )
        detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # 10. MÚLTIPLES ITEMS - Entrada grande
        transaction = InventoryTransaction.objects.create(
            transaction_type=type_entry,
            status=status_applied,
            reference='PO-2026-100',
            number='ENT-2026-100',
            notes='Entrada grande con múltiples artículos',
            performed_at=timezone.now() - timedelta(days=45),
            created_by=user,
            is_applied=True,
            applied_at=timezone.now() - timedelta(days=45)
        )
        
        # Crear varios detalles
        for i in range(min(5, len(items))):
            item = items[i]
            TransactionDetail.objects.create(
                transaction=transaction,
                item=item,
                quantity=Decimal(str(random.randint(15, 100))),
                target_location=locations[i % len(locations)],
                unit_cost=Decimal(str(random.uniform(50, 2000))).quantize(Decimal('0.01')),
                notes=f'Lote de {item.name}'
            )
            detail_count += 1
        
        transaction_count += 1
        self.stdout.write(f'  ✓ Transacción creada: {transaction.number} - {transaction.transaction_type.name}')
        
        # Resumen final
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Transacciones creadas: {transaction_count}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'✓ Detalles de transacción creados: {detail_count}'
        ))
