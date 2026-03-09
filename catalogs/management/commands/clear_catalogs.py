from django.core.management.base import BaseCommand
from django.db import connection
from catalogs.models import Estado, UnitOfMeasure, Categoria, Marca, Modelo


class Command(BaseCommand):
    help = 'Elimina todos los datos de los catálogos del sistema'

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
                '⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos de los catálogos.'
            ))
            confirm = input('¿Estás seguro? Escribe "yes" para confirmar: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('✗ Operación cancelada'))
                return
        
        self.stdout.write(self.style.WARNING('Eliminando datos de catálogos...'))
        
        # Eliminar en orden inverso a las dependencias
        deleted = {}
        
        # Modelos (depende de Marca)
        count = Modelo.objects.all().delete()[0]
        deleted['Modelos'] = count
        self.stdout.write(f'  - Modelos eliminados: {count}')
        
        # Marcas
        count = Marca.objects.all().delete()[0]
        deleted['Marcas'] = count
        self.stdout.write(f'  - Marcas eliminadas: {count}')
        
        # Categorías
        count = Categoria.objects.all().delete()[0]
        deleted['Categorías'] = count
        self.stdout.write(f'  - Categorías eliminadas: {count}')
        
        # Unidades de Medida
        count = UnitOfMeasure.objects.all().delete()[0]
        deleted['Unidades de medida'] = count
        self.stdout.write(f'  - Unidades de medida eliminadas: {count}')
        
        # Estados
        count = Estado.objects.all().delete()[0]
        deleted['Estados'] = count
        self.stdout.write(f'  - Estados eliminados: {count}')
        
        total = sum(deleted.values())
        self.stdout.write(self.style.SUCCESS(f'\n✓ Total de registros eliminados: {total}'))
        
        for nombre, cantidad in deleted.items():
            self.stdout.write(f'  • {nombre}: {cantidad}')
        
        # Reiniciar secuencias de IDs
        self.stdout.write('\nReiniciando secuencias de IDs...')
        self.reset_sequences([Estado, UnitOfMeasure, Categoria, Marca, Modelo])
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
