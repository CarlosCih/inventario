from django.core.management.base import BaseCommand
from django.utils import timezone
from inventory.models import Item, Asset, Stock
from catalogs.models import UnitOfMeasure, Estado
from locations.models import Location
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Carga datos iniciales para el inventario (Items, Assets, Stock)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando seed de inventario...'))
        
        # Verificar datos previos necesarios
        if not self.verify_dependencies():
            return
        
        # Seed Items
        self.seed_items()
        
        # Seed Assets (requiere items)
        self.seed_assets()
        
        # Seed Stock (requiere items y ubicaciones)
        self.seed_stock()
        
        self.stdout.write(self.style.SUCCESS('✓ Seed de inventario completado exitosamente'))

    def verify_dependencies(self):
        """Verifica que existan los datos previos necesarios"""
        self.stdout.write('Verificando dependencias...')
        
        if not UnitOfMeasure.objects.exists():
            self.stdout.write(self.style.ERROR(
                '✗ Error: No hay unidades de medida. Ejecute primero: python manage.py seed_catalogs'
            ))
            return False
        
        if not Estado.objects.exists():
            self.stdout.write(self.style.ERROR(
                '✗ Error: No hay estados. Ejecute primero: python manage.py seed_catalogs'
            ))
            return False
        
        if not Location.objects.exists():
            self.stdout.write(self.style.ERROR(
                '✗ Error: No hay ubicaciones. Ejecute primero: python manage.py seed_locations'
            ))
            return False
        
        self.stdout.write(self.style.SUCCESS('✓ Todas las dependencias están disponibles'))
        return True

    def seed_items(self):
        """Crea artículos de ejemplo con coherencia en los datos"""
        # Obtener unidades de medida
        try:
            uom_pieza = UnitOfMeasure.objects.get(abbr='pza')
            uom_juego = UnitOfMeasure.objects.get(abbr='jgo')
            uom_unidad = UnitOfMeasure.objects.get(abbr='u')
            uom_caja = UnitOfMeasure.objects.get(abbr='caja')
        except UnitOfMeasure.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: Falta una unidad de medida: {str(e)}'))
            return
        
        items_data = [
            # Equipos de cómputo - Serializados
            {
                'sku': 'COMP-LAP-001',
                'name': 'Laptop Dell Latitude 5420',
                'description': 'Laptop empresarial, Intel Core i5, 8GB RAM, 256GB SSD',
                'unitofmeasure': uom_pieza,
                'is_serialized': True,
                'is_lot_controlled': False,
                'has_expiration': False,
            },
            {
                'sku': 'COMP-LAP-002',
                'name': 'Laptop HP ProBook 450',
                'description': 'Laptop empresarial, Intel Core i7, 16GB RAM, 512GB SSD',
                'unitofmeasure': uom_pieza,
                'is_serialized': True,
                'is_lot_controlled': False,
                'has_expiration': False,
            },
            {
                'sku': 'COMP-MON-001',
                'name': 'Monitor Samsung 27 pulgadas',
                'description': 'Monitor LED Full HD 1920x1080, HDMI',
                'unitofmeasure': uom_pieza,
                'is_serialized': True,
                'is_lot_controlled': False,
                'has_expiration': False,
            },
            {
                'sku': 'COMP-TEC-001',
                'name': 'Teclado Logitech MK270',
                'description': 'Teclado inalámbrico con mouse incluido',
                'unitofmeasure': uom_juego,
                'is_serialized': True,
                'is_lot_controlled': False,
                'has_expiration': False,
            },
            {
                'sku': 'COMP-IMP-001',
                'name': 'Impresora HP LaserJet Pro M404',
                'description': 'Impresora láser monocromática, red y USB',
                'unitofmeasure': uom_pieza,
                'is_serialized': True,
                'is_lot_controlled': False,
                'has_expiration': False,
            },
            
            # Muebles - Serializados
            {
                'sku': 'MUEB-ESC-001',
                'name': 'Escritorio ejecutivo',
                'description': 'Escritorio de madera 1.60m x 0.80m',
                'unitofmeasure': uom_pieza,
                'is_serialized': True,
                'is_lot_controlled': False,
                'has_expiration': False,
            },
            {
                'sku': 'MUEB-SIL-001',
                'name': 'Silla ergonómica',
                'description': 'Silla de oficina con soporte lumbar, altura ajustable',
                'unitofmeasure': uom_pieza,
                'is_serialized': True,
                'is_lot_controlled': False,
                'has_expiration': False,
            },
            
            # Consumibles - No serializados, control por cantidad
            {
                'sku': 'CONS-PAP-001',
                'name': 'Papel bond carta',
                'description': 'Resma de papel bond tamaño carta, 500 hojas',
                'unitofmeasure': uom_caja,
                'is_serialized': False,
                'is_lot_controlled': False,
                'has_expiration': False,
            },
            {
                'sku': 'CONS-BOL-001',
                'name': 'Bolígrafos azules',
                'description': 'Caja de bolígrafos punto fino, tinta azul',
                'unitofmeasure': uom_caja,
                'is_serialized': False,
                'is_lot_controlled': False,
                'has_expiration': False,
            },
            {
                'sku': 'CONS-TON-001',
                'name': 'Toner HP 26A negro',
                'description': 'Cartucho de toner compatible con LaserJet Pro M404',
                'unitofmeasure': uom_pieza,
                'is_serialized': False,
                'is_lot_controlled': True,
                'has_expiration': True,
            },
        ]
        
        count = 0
        for item_data in items_data:
            item, created = Item.objects.get_or_create(
                sku=item_data['sku'],
                defaults=item_data
            )
            if created:
                count += 1
                self.stdout.write(f'  - Item creado: {item.sku} - {item.name}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Items: {count} creados'))

    def seed_assets(self):
        """Crea activos (assets) para los items serializados con coherencia"""
        # Verificar que existan items serializados
        items_serializados = Item.objects.filter(is_serialized=True)
        if not items_serializados.exists():
            self.stdout.write(self.style.WARNING('  ! No hay items serializados para crear activos'))
            return
        
        # Obtener estados y ubicaciones
        try:
            estado_bueno = Estado.objects.get(name='Bueno')
            estado_nuevo = Estado.objects.get(name='Nuevo')
            estado_disponible = Estado.objects.get(name='Disponible')
            estado_asignado = Estado.objects.get(name='Asignado')
        except Estado.DoesNotExist:
            # Usar el primer estado disponible
            estado_bueno = Estado.objects.first()
            estado_nuevo = estado_bueno
            estado_disponible = estado_bueno
            estado_asignado = estado_bueno
        
        # Obtener ubicaciones
        ubicaciones = list(Location.objects.filter(is_active=True))
        if not ubicaciones:
            self.stdout.write(self.style.ERROR('✗ No hay ubicaciones activas'))
            return
        
        # Crear activos de ejemplo para cada tipo de item serializado
        assets_data = []
        
        # Laptops Dell
        try:
            item_dell = Item.objects.get(sku='COMP-LAP-001')
            for i in range(1, 6):  # 5 laptops Dell
                assets_data.append({
                    'item': item_dell,
                    'num_serial': f'DELL-LAT-2024-{i:04d}',
                    'internal_code': f'LAP-DELL-{i:03d}',
                    'status': estado_nuevo if i <= 2 else estado_bueno,
                    'location': random.choice(ubicaciones),
                    'notes': f'Laptop Dell adquirida en {random.choice(["enero", "febrero", "marzo"])} 2024',
                })
        except Item.DoesNotExist:
            pass
        
        # Laptops HP
        try:
            item_hp = Item.objects.get(sku='COMP-LAP-002')
            for i in range(1, 4):  # 3 laptops HP
                assets_data.append({
                    'item': item_hp,
                    'num_serial': f'HP-PB450-2024-{i:04d}',
                    'internal_code': f'LAP-HP-{i:03d}',
                    'status': estado_bueno,
                    'location': random.choice(ubicaciones),
                    'notes': f'Laptop HP para área de {random.choice(["ventas", "administración", "gerencia"])}',
                })
        except Item.DoesNotExist:
            pass
        
        # Monitores
        try:
            item_monitor = Item.objects.get(sku='COMP-MON-001')
            for i in range(1, 11):  # 10 monitores
                assets_data.append({
                    'item': item_monitor,
                    'num_serial': f'SAMS-MON-2024-{i:04d}',
                    'internal_code': f'MON-{i:03d}',
                    'status': estado_disponible if i <= 3 else estado_asignado,
                    'location': random.choice(ubicaciones),
                    'notes': 'Monitor para estación de trabajo',
                })
        except Item.DoesNotExist:
            pass
        
        # Teclados
        try:
            item_teclado = Item.objects.get(sku='COMP-TEC-001')
            for i in range(1, 9):  # 8 juegos de teclado/mouse
                assets_data.append({
                    'item': item_teclado,
                    'num_serial': f'LOG-MK270-{i:04d}',
                    'internal_code': f'TEC-{i:03d}',
                    'status': estado_disponible,
                    'location': random.choice(ubicaciones),
                    'notes': 'Juego de teclado y mouse inalámbrico',
                })
        except Item.DoesNotExist:
            pass
        
        # Impresoras
        try:
            item_impresora = Item.objects.get(sku='COMP-IMP-001')
            for i in range(1, 4):  # 3 impresoras
                assets_data.append({
                    'item': item_impresora,
                    'num_serial': f'HP-LJ-M404-{i:04d}',
                    'internal_code': f'IMP-{i:03d}',
                    'status': estado_asignado,
                    'location': random.choice(ubicaciones),
                    'notes': f'Impresora asignada a área de {random.choice(["administración", "ventas", "recursos humanos"])}',
                })
        except Item.DoesNotExist:
            pass
        
        # Escritorios
        try:
            item_escritorio = Item.objects.get(sku='MUEB-ESC-001')
            for i in range(1, 13):  # 12 escritorios
                assets_data.append({
                    'item': item_escritorio,
                    'num_serial': f'ESC-2024-{i:03d}',
                    'internal_code': f'MUEB-ESC-{i:03d}',
                    'status': estado_asignado,
                    'location': random.choice(ubicaciones),
                    'notes': 'Escritorio para oficina',
                })
        except Item.DoesNotExist:
            pass
        
        # Sillas
        try:
            item_silla = Item.objects.get(sku='MUEB-SIL-001')
            for i in range(1, 16):  # 15 sillas
                assets_data.append({
                    'item': item_silla,
                    'num_serial': f'SIL-2024-{i:03d}',
                    'internal_code': f'MUEB-SIL-{i:03d}',
                    'status': estado_bueno,
                    'location': random.choice(ubicaciones),
                    'notes': 'Silla ergonómica para puesto de trabajo',
                })
        except Item.DoesNotExist:
            pass
        
        # Crear los activos
        count = 0
        for asset_data in assets_data:
            asset, created = Asset.objects.get_or_create(
                num_serial=asset_data['num_serial'],
                defaults=asset_data
            )
            if created:
                count += 1
                self.stdout.write(f'  - Activo creado: {asset.num_serial} - {asset.item.name}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Activos: {count} creados'))

    def seed_stock(self):
        """Crea stock para items no serializados (consumibles)"""
        # Obtener items no serializados
        items_no_serializados = Item.objects.filter(is_serialized=False)
        if not items_no_serializados.exists():
            self.stdout.write(self.style.WARNING('  ! No hay items no serializados para crear stock'))
            return
        
        # Obtener ubicaciones de almacén
        ubicaciones_almacen = Location.objects.filter(
            code__startswith='ALM',
            is_active=True
        )
        
        if not ubicaciones_almacen.exists():
            # Si no hay ubicaciones de almacén, usar cualquier ubicación
            ubicaciones_almacen = Location.objects.filter(is_active=True)[:5]
        
        stock_data = []
        
        # Papel bond - Distribuido en varias ubicaciones del almacén
        try:
            item_papel = Item.objects.get(sku='CONS-PAP-001')
            for ubicacion in ubicaciones_almacen[:3]:
                stock_data.append({
                    'item': item_papel,
                    'location': ubicacion,
                    'quantity_on_hand': Decimal(random.randint(10, 50)),
                    'quantity_reserved': Decimal(random.randint(0, 5)),
                })
        except Item.DoesNotExist:
            pass
        
        # Bolígrafos
        try:
            item_boligrafos = Item.objects.get(sku='CONS-BOL-001')
            for ubicacion in ubicaciones_almacen[:2]:
                stock_data.append({
                    'item': item_boligrafos,
                    'location': ubicacion,
                    'quantity_on_hand': Decimal(random.randint(15, 40)),
                    'quantity_reserved': Decimal(random.randint(0, 3)),
                })
        except Item.DoesNotExist:
            pass
        
        # Toner
        try:
            item_toner = Item.objects.get(sku='CONS-TON-001')
            for ubicacion in ubicaciones_almacen[:2]:
                stock_data.append({
                    'item': item_toner,
                    'location': ubicacion,
                    'quantity_on_hand': Decimal(random.randint(5, 15)),
                    'quantity_reserved': Decimal(random.randint(0, 2)),
                })
        except Item.DoesNotExist:
            pass
        
        # Crear los registros de stock
        count = 0
        for stock_info in stock_data:
            stock, created = Stock.objects.get_or_create(
                item=stock_info['item'],
                location=stock_info['location'],
                defaults={
                    'quantity_on_hand': stock_info['quantity_on_hand'],
                    'quantity_reserved': stock_info['quantity_reserved'],
                }
            )
            if created:
                count += 1
                self.stdout.write(
                    f'  - Stock creado: {stock.item.sku} en {stock.location.code} '
                    f'(Disponible: {stock.quantity_on_hand})'
                )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Registros de Stock: {count} creados'))
