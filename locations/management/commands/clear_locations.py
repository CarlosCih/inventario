from django.core.management.base import BaseCommand
from django.db import connection
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
        
        # Reiniciar secuencias de IDs
        self.stdout.write('\nReiniciando secuencias de IDs...')
        self.reset_sequences([Area, LocationType, Location])
        self.stdout.write(self.style.SUCCESS('\n✓ Secuencias reiniciadas correctamente'))
    
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
