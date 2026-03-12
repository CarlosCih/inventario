from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Configurar los grupos de permisos para el sistema de inventario"

    def handle(self, *args, **options):
        groups = [
            "Encargado",
            "Usuario",
            "Consultor"
        ]

        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Grupo "{group_name}" creado correctamente')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Grupo "{group_name}" ya existe')
                )
        self.stdout.write(self.style.SUCCESS("\n Configuración de grupos de permisos completada"))
        self.stdout.write(self.style.SUCCESS('\n Grupos disponibles'))
        self.stdout.write('  • Encargado: Gestiona catálogos, inventario y transacciones')
        self.stdout.write('  • Usuario: Crea transacciones, consulta inventario')
        self.stdout.write('  • Consultor: Solo lectura (reportes y auditorías)')
        self.stdout.write('\nNota: Los usuarios staff/superuser tienen acceso completo')