from django.core.management.base import BaseCommand
from django.db import connection
from transactions.models import TransactionDetail, InventoryTransaction, TransactionTag


class Command(BaseCommand):
    help = 'Elimina todos los datos de transacciones (TransactionDetail e InventoryTransaction)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma la eliminación de datos',
        )
        parser.add_argument(
            '--include-tags',
            action='store_true',
            help='También elimina las etiquetas de transacciones',
        )

    def handle(self, *args, **kwargs):
        confirm = kwargs.get('confirm')
        include_tags = kwargs.get('include_tags', False)
        
        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    '⚠ ADVERTENCIA: Este comando eliminará TODOS los datos de transacciones.\n'
                    'Para confirmar, ejecute: python manage.py clear_transactions --confirm\n'
                    'Para también eliminar las etiquetas: python manage.py clear_transactions --confirm --include-tags'
                )
            )
            return
        
        self.stdout.write(self.style.WARNING('Eliminando datos de transacciones...'))
        
        # Contar registros antes de eliminar
        details_count = TransactionDetail.objects.count()
        transactions_count = InventoryTransaction.objects.count()
        tags_count = TransactionTag.objects.count()
        
        # Contar transacciones con tags
        transactions_with_tags = InventoryTransaction.objects.filter(tags__isnull=False).distinct().count()
        
        # Mostrar información
        self.stdout.write(f'  📊 {transactions_count} transacciones')
        self.stdout.write(f'  📊 {details_count} detalles de transacción')
        self.stdout.write(f'  📊 {transactions_with_tags} transacciones con etiquetas')
        self.stdout.write(f'  📊 {tags_count} etiquetas definidas\n')
        
        # Eliminar en orden correcto (detalles primero)
        TransactionDetail.objects.all().delete()
        self.stdout.write(f'  ✓ {details_count} detalles de transacción eliminados')
        
        InventoryTransaction.objects.all().delete()
        self.stdout.write(f'  ✓ {transactions_count} transacciones eliminadas')
        
        # Eliminar tags si se solicitó
        if include_tags and tags_count > 0:
            TransactionTag.objects.all().delete()
            self.stdout.write(f'  ✓ {tags_count} etiquetas eliminadas')
        elif tags_count > 0:
            self.stdout.write(
                self.style.NOTICE(
                    f'  ℹ {tags_count} etiquetas conservadas (usa --include-tags para eliminarlas)'
                )
            )
        
        # Reiniciar secuencias de IDs
        self.stdout.write('\nReiniciando secuencias de IDs...')
        models_to_reset = [TransactionDetail, InventoryTransaction]
        if include_tags:
            models_to_reset.append(TransactionTag)
        self.reset_sequences(models_to_reset)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Limpieza completada: {transactions_count} transacciones y {details_count} detalles eliminados'
            )
        )
    
    def reset_sequences(self, models_list):
        """Reinicia las secuencias de auto-incremento de las tablas"""
        with connection.cursor() as cursor:
            db_vendor = connection.vendor
            
            for model in models_list:
                table_name = model._meta.db_table
                
                if db_vendor == 'sqlite':
                    cursor.execute(
                        f"DELETE FROM sqlite_sequence WHERE name='{table_name}';"
                    )
                elif db_vendor == 'postgresql':
                    cursor.execute(
                        f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;"
                    )
                elif db_vendor == 'mysql':
                    cursor.execute(
                        f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;"
                    )
                
                self.stdout.write(f'  ↻ Secuencia reiniciada: {table_name}')
