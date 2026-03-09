from django.core.management.base import BaseCommand
from django.db import connection
from inventory.models import Item, Asset, Stock


class Command(BaseCommand):
    help = 'Elimina todos los datos de inventario (Items, Assets, Stock)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Confirmar eliminación sin preguntar',
        )

    def handle(self, *args, **options):
        if not options['yes']:
            confirm = input(
                '¿Está seguro de que desea eliminar TODOS los datos de inventario? '
                'Esta acción NO se puede deshacer. (escriba "si" para confirmar): '
            )
            if confirm.lower() != 'si':
                self.stdout.write(self.style.WARNING('Operación cancelada.'))
                return

        self.stdout.write(self.style.WARNING('Eliminando datos de inventario...'))

        # Eliminar en orden inverso a las dependencias
        stock_count = Stock.objects.count()
        Stock.objects.all().delete()
        self.stdout.write(f'  - {stock_count} registros de Stock eliminados')

        asset_count = Asset.objects.count()
        Asset.objects.all().delete()
        self.stdout.write(f'  - {asset_count} Activos eliminados')

        item_count = Item.objects.count()
        Item.objects.all().delete()
        self.stdout.write(f'  - {item_count} Artículos eliminados')
        
        # Reiniciar secuencias de IDs
        self.stdout.write('\nReiniciando secuencias de IDs...')
        self.reset_sequences([Stock, Asset, Item])

        self.stdout.write(self.style.SUCCESS('\n✓ Todos los datos de inventario han sido eliminados'))
        self.stdout.write(self.style.SUCCESS('✓ Secuencias reiniciadas correctamente'))
    
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
