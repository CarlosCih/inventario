from django.core.management.base import BaseCommand
from transactions.models import TransactionDetail, InventoryTransaction


class Command(BaseCommand):
    help = 'Elimina todos los datos de transacciones (TransactionDetail e InventoryTransaction)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma la eliminación de datos',
        )

    def handle(self, *args, **kwargs):
        confirm = kwargs.get('confirm')
        
        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    '⚠ ADVERTENCIA: Este comando eliminará TODOS los datos de transacciones.\n'
                    'Para confirmar, ejecute: python manage.py clear_transactions --confirm'
                )
            )
            return
        
        self.stdout.write(self.style.WARNING('Eliminando datos de transacciones...'))
        
        # Contar registros antes de eliminar
        details_count = TransactionDetail.objects.count()
        transactions_count = InventoryTransaction.objects.count()
        
        # Eliminar en orden correcto (detalles primero)
        TransactionDetail.objects.all().delete()
        self.stdout.write(f'  - {details_count} detalles de transacción eliminados')
        
        InventoryTransaction.objects.all().delete()
        self.stdout.write(f'  - {transactions_count} transacciones eliminadas')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Limpieza completada: {transactions_count} transacciones y {details_count} detalles eliminados'
            )
        )
