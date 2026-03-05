from django.core.management.base import BaseCommand
from locations.models import Area, LocationType, Location


class Command(BaseCommand):
    help = 'Carga datos iniciales para las ubicaciones del sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando seed de ubicaciones...'))
        
        # Seed Áreas
        self.seed_areas()
        
        # Seed Tipos de Ubicación
        self.seed_location_types()
        
        # Seed Ubicaciones (requiere áreas y tipos)
        self.seed_locations()
        
        self.stdout.write(self.style.SUCCESS('✓ Seed completado exitosamente'))

    def seed_areas(self):
        """Crea áreas comunes para el sistema"""
        areas = [
            ('Administración', 'Área administrativa y de oficinas'),
            ('Almacén General', 'Almacén principal de la empresa'),
            ('Producción', 'Área de producción y manufactura'),
            ('Ventas', 'Área de ventas y atención al cliente'),
            ('Compras', 'Área de compras y adquisiciones'),
            ('Recursos Humanos', 'Área de gestión de personal'),
            ('TI', 'Área de tecnologías de información'),
            ('Mantenimiento', 'Área de mantenimiento y reparaciones'),
            ('Logística', 'Área de logística y distribución'),
            ('Calidad', 'Área de control de calidad'),
        ]
        
        count = 0
        for nombre, descripcion in areas:
            area, created = Area.objects.get_or_create(
                name=nombre,
                defaults={'description': descripcion}
            )
            if created:
                count += 1
                self.stdout.write(f'  - Área creada: {nombre}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Áreas: {count} creadas'))

    def seed_location_types(self):
        """Crea tipos de ubicación comunes"""
        tipos = [
            'Estante',
            'Escritorio',
            'Oficina',
            'Bodega',
            'Almacén',
            'Anaquel',
            'Mostrador',
            'Vitrina',
            'Sala',
            'Cubículo',
            'Rack',
            'Pasillo',
            'Área común',
            'Depósito',
            'Armario',
        ]
        
        count = 0
        for tipo_name in tipos:
            tipo, created = LocationType.objects.get_or_create(name=tipo_name)
            if created:
                count += 1
                self.stdout.write(f'  - Tipo de ubicación creado: {tipo_name}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Tipos de ubicación: {count} creados'))

    def seed_locations(self):
        """Crea ubicaciones de ejemplo"""
        # Obtener áreas y tipos
        try:
            area_almacen = Area.objects.get(name='Almacén General')
            area_admin = Area.objects.get(name='Administración')
            area_ti = Area.objects.get(name='TI')
            
            tipo_estante = LocationType.objects.get(name='Estante')
            tipo_oficina = LocationType.objects.get(name='Oficina')
            tipo_escritorio = LocationType.objects.get(name='Escritorio')
            tipo_rack = LocationType.objects.get(name='Rack')
        except (Area.DoesNotExist, LocationType.DoesNotExist) as e:
            self.stdout.write(self.style.ERROR(
                f'✗ Error: Faltan áreas o tipos de ubicación requeridos. {str(e)}'
            ))
            return
        
        ubicaciones = [
            # Almacén
            ('ALM-EST-001', 'Estante A1', tipo_estante, area_almacen, 'Primer estante del pasillo A'),
            ('ALM-EST-002', 'Estante A2', tipo_estante, area_almacen, 'Segundo estante del pasillo A'),
            ('ALM-EST-003', 'Estante B1', tipo_estante, area_almacen, 'Primer estante del pasillo B'),
            ('ALM-EST-004', 'Estante B2', tipo_estante, area_almacen, 'Segundo estante del pasillo B'),
            ('ALM-EST-005', 'Estante C1', tipo_estante, area_almacen, 'Primer estante del pasillo C'),
            
            # Administración
            ('ADM-OFC-001', 'Oficina Director', tipo_oficina, area_admin, 'Oficina del director general'),
            ('ADM-OFC-002', 'Oficina Gerente', tipo_oficina, area_admin, 'Oficina del gerente administrativo'),
            ('ADM-ESC-001', 'Escritorio Asistente 1', tipo_escritorio, area_admin, 'Escritorio de asistente administrativo'),
            ('ADM-ESC-002', 'Escritorio Asistente 2', tipo_escritorio, area_admin, 'Escritorio de asistente de gerencia'),
            
            # TI
            ('TI-RACK-001', 'Rack Principal', tipo_rack, area_ti, 'Rack de servidores principal'),
            ('TI-RACK-002', 'Rack Comunicaciones', tipo_rack, area_ti, 'Rack de equipos de comunicaciones'),
            ('TI-OFC-001', 'Oficina TI', tipo_oficina, area_ti, 'Oficina del departamento de TI'),
            ('TI-ESC-001', 'Escritorio Soporte', tipo_escritorio, area_ti, 'Escritorio de soporte técnico'),
        ]
        
        count = 0
        for codigo, nombre, tipo, area, descripcion in ubicaciones:
            location, created = Location.objects.get_or_create(
                code=codigo,
                defaults={
                    'name': nombre,
                    'location_type': tipo,
                    'area': area,
                    'description': descripcion,
                }
            )
            if created:
                count += 1
                self.stdout.write(f'  - Ubicación creada: {codigo} - {nombre}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Ubicaciones: {count} creadas'))
