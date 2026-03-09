from django.core.management.base import BaseCommand
from transactions.models import TransactionTag


class Command(BaseCommand):
    help = "Seeder para crear etiquetas de transacción predefinidas"
    
    TAGS_SEED = [
        {
            "name": "Alto valor",
            "code": "HIGH_VALUE",
            "description": "Transacción de alto valor",
            "color": "#DC2626",
            "is_auto": True
        },
        {
            "name": "Transacción masiva",
            "code": "BULK",
            "description": "Transacción con muchos artículos",
            "color": "#2563EB",
            "is_auto": True
        },
        {
            "name": "Urgente",
            "code": "URGENT",
            "description": "Transacción realizada el mismo día de creación",
            "color": "#FBBF24",
            "is_auto": True
        },
        {
            "name": "Requiere aprobación",
            "code": "REQUIRES_APPROVAL",
            "description": "Transacción que necesita aprobación antes de ser procesada",
            "color": "#B38625",
            "is_auto": False
        },
        {
            "name": "Ajuste",
            "code": "ADJUSTMENT",
            "description": "Transacción de ajuste de inventario",
            "color": "#8B5CF6",
            "is_auto": False
        },
        {
            "name": "Transferencia",
            "code": "TRANSFER",
            "description": "Transacción de transferencia entre ubicaciones",
            "color": "#10B981",
            "is_auto": False
        }
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todas las etiquetas existentes antes de crear las nuevas'
        )

    def handle(self, *args, **options):
        # Limpiar etiquetas si se especificó la opción
        if options['clear']:
            deleted_count = TransactionTag.objects.all().count()
            TransactionTag.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Se eliminaron {deleted_count} etiqueta(s) existente(s).")
            )

        # Contadores
        created_count = 0
        existing_count = 0

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Creando etiquetas de transacción ===\n"))

        # Crear etiquetas
        for tag_data in self.TAGS_SEED:
            tag, created = TransactionTag.objects.get_or_create(
                code=tag_data["code"],
                defaults={
                    "name": tag_data["name"],
                    "description": tag_data["description"],
                    "color": tag_data["color"],
                    "is_auto": tag_data["is_auto"]
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ '{tag.name}' ({tag.code}) - Creada")
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f"○ '{tag.name}' ({tag.code}) - Ya existe")
                )

        # Resumen final
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Resumen ==="))
        self.stdout.write(f"Total de etiquetas: {len(self.TAGS_SEED)}")
        self.stdout.write(self.style.SUCCESS(f"Creadas: {created_count}"))
        self.stdout.write(self.style.WARNING(f"Ya existían: {existing_count}"))
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS("\n✓ Seeder ejecutado exitosamente\n"))
            