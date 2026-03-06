from django.core.management.base import BaseCommand
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

        self.stdout.write(self.style.SUCCESS('✓ Todos los datos de inventario han sido eliminados'))
