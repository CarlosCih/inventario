from django.apps import AppConfig


class CatalogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogs'
    
    def ready(self):
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        
        @receiver(post_migrate)
        def create_default_catalogs(sender, **kwargs):
            if sender.name == 'catalogs':
                from .models import Estado, UnitOfMeasure
                estados = ["Activo", "Inactivo", "Baja"]
                for estado_name in estados:
                    Estado.objects.get_or_create(name=estado_name)
                unidades = [
                    ("Pieza", "Pz"),
                    ("Caja", "Cj"),                   
                ]
                for unidad_name, unidad_abbr in unidades:
                    UnitOfMeasure.objects.get_or_create(name=unidad_name, abbr=unidad_abbr)
