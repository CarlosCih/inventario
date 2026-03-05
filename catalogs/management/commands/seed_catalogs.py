from django.core.management.base import BaseCommand
from catalogs.models import Estado, UnitOfMeasure, Categoria, Marca, Modelo


class Command(BaseCommand):
    help = 'Carga datos iniciales para los catálogos del sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando seed de catálogos...'))
        
        # Seed Estados
        self.seed_estados()
        
        # Seed Unidades de Medida
        self.seed_unidades_medida()
        
        # Seed Categorías
        self.seed_categorias()
        
        # Seed Marcas
        self.seed_marcas()
        
        # Seed Modelos (requiere marcas)
        self.seed_modelos()
        
        self.stdout.write(self.style.SUCCESS('✓ Seed completado exitosamente'))

    def seed_estados(self):
        """Crea estados comunes para el inventario"""
        estados = [
            'Nuevo',
            'Bueno',
            'Regular',
            'Malo',
            'En reparación',
            'Dado de baja',
            'En tránsito',
            'Disponible',
            'Asignado',
            'Reservado',
        ]
        
        count = 0
        for estado_name in estados:
            estado, created = Estado.objects.get_or_create(name=estado_name)
            if created:
                count += 1
                self.stdout.write(f'  - Estado creado: {estado_name}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Estados: {count} creados'))

    def seed_unidades_medida(self):
        """Crea unidades de medida comunes"""
        unidades = [
            ('Pieza', 'pza'),
            ('Kilogramo', 'kg'),
            ('Gramo', 'g'),
            ('Litro', 'L'),
            ('Mililitro', 'mL'),
            ('Metro', 'm'),
            ('Centímetro', 'cm'),
            ('Caja', 'caja'),
            ('Paquete', 'paq'),
            ('Juego', 'jgo'),
            ('Par', 'par'),
            ('Docena', 'doc'),
            ('Unidad', 'u'),
            ('Rollo', 'rollo'),
            ('Galon', 'gal'),
        ]
        
        count = 0
        for nombre, abreviatura in unidades:
            unidad, created = UnitOfMeasure.objects.get_or_create(
                abbr=abreviatura,
                defaults={'name': nombre}
            )
            if created:
                count += 1
                self.stdout.write(f'  - Unidad creada: {nombre} ({abreviatura})')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Unidades de medida: {count} creadas'))

    def seed_categorias(self):
        """Crea categorías comunes para inventario"""
        categorias = [
            'Electrónica',
            'Equipos de cómputo',
            'Muebles de oficina',
            'Papelería',
            'Herramientas',
            'Equipos de comunicación',
            'Vehículos',
            'Material de limpieza',
            'Equipos de seguridad',
            'Accesorios',
            'Software',
            'Consumibles',
            'Equipo médico',
            'Material de construcción',
            'Equipamiento industrial',
        ]
        
        count = 0
        for categoria_name in categorias:
            categoria, created = Categoria.objects.get_or_create(name=categoria_name)
            if created:
                count += 1
                self.stdout.write(f'  - Categoría creada: {categoria_name}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Categorías: {count} creadas'))

    def seed_marcas(self):
        """Crea marcas comunes"""
        marcas = [
            'Dell',
            'HP',
            'Lenovo',
            'Apple',
            'Samsung',
            'LG',
            'Sony',
            'Epson',
            'Canon',
            'Microsoft',
            'Cisco',
            'TP-Link',
            'Logitech',
            'Intel',
            'AMD',
            'Generic',
            'Sin marca',
        ]
        
        count = 0
        for marca_name in marcas:
            marca, created = Marca.objects.get_or_create(name=marca_name)
            if created:
                count += 1
                self.stdout.write(f'  - Marca creada: {marca_name}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Marcas: {count} creadas'))

    def seed_modelos(self):
        """Crea modelos de ejemplo para algunas marcas"""
        modelos_data = [
            # Dell
            ('Dell', 'Inspiron 15', 'DELL-INS15'),
            ('Dell', 'Latitude 5420', 'DELL-LAT5420'),
            ('Dell', 'OptiPlex 7090', 'DELL-OPT7090'),
            ('Dell', 'XPS 13', 'DELL-XPS13'),
            
            # HP
            ('HP', 'ProBook 450', 'HP-PB450'),
            ('HP', 'EliteBook 840', 'HP-EB840'),
            ('HP', 'LaserJet Pro M404', 'HP-LJM404'),
            ('HP', 'DeskJet 2720', 'HP-DJ2720'),
            
            # Lenovo
            ('Lenovo', 'ThinkPad T14', 'LNV-TPT14'),
            ('Lenovo', 'IdeaPad 3', 'LNV-IP3'),
            ('Lenovo', 'ThinkCentre M70', 'LNV-TCM70'),
            
            # Apple
            ('Apple', 'MacBook Pro 13"', 'APPL-MBP13'),
            ('Apple', 'MacBook Air M1', 'APPL-MBAM1'),
            ('Apple', 'iMac 24"', 'APPL-IMAC24'),
            
            # Samsung
            ('Samsung', 'Galaxy Tab S7', 'SAMS-GTS7'),
            ('Samsung', 'Monitor 27"', 'SAMS-MON27'),
            
            # Generic
            ('Generic', 'Modelo estándar', 'GEN-STD'),
            ('Sin marca', 'Sin modelo', 'NO-MODEL'),
        ]
        
        count = 0
        for marca_name, modelo_name, codigo in modelos_data:
            try:
                marca = Marca.objects.get(name=marca_name)
                modelo, created = Modelo.objects.get_or_create(
                    code=codigo,
                    defaults={
                        'name': modelo_name,
                        'marca': marca
                    }
                )
                if created:
                    count += 1
                    self.stdout.write(f'  - Modelo creado: {marca_name} - {modelo_name}')
            except Marca.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ! Marca no encontrada: {marca_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ Modelos: {count} creados'))
