from django.core.management.base import BaseCommand
from locations.models import Area, LocationType, Location


class Command(BaseCommand):
    help = 'Elimina todos los datos de ubicaciones del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la eliminación sin pedir confirmación',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        if not force:
            self.stdout.write(self.style.WARNING(
                '⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos de ubicaciones.'
            ))
            confirm = input('¿Estás seguro? Escribe "yes" para confirmar: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('✗ Operación cancelada'))
                return
        
        self.stdout.write(self.style.WARNING('Eliminando datos de ubicaciones...'))
        
        # Eliminar en orden inverso a las dependencias
        deleted = {}
        
        # Ubicaciones (depende de Area y LocationType)
        count = Location.objects.all().delete()[0]
        deleted['Ubicaciones'] = count
        self.stdout.write(f'  - Ubicaciones eliminadas: {count}')
        
        # Tipos de Ubicación
        count = LocationType.objects.all().delete()[0]
        deleted['Tipos de ubicación'] = count
        self.stdout.write(f'  - Tipos de ubicación eliminados: {count}')
        
        # Áreas
        count = Area.objects.all().delete()[0]
        deleted['Áreas'] = count
        self.stdout.write(f'  - Áreas eliminadas: {count}')
        
        total = sum(deleted.values())
        self.stdout.write(self.style.SUCCESS(f'\n✓ Total de registros eliminados: {total}'))
        
        for nombre, cantidad in deleted.items():
            self.stdout.write(f'  • {nombre}: {cantidad}')
