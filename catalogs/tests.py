from django.test import TestCase
from .models import Estado
from django.core.exceptions import ValidationError

# Create your tests here.
class EstadoModelTest(TestCase):
    def test_estado_name_case_insensitive_uniqueness(self):
        Estado.objects.create(name="Activo")
        estado2 = Estado(name="activo")
        with self.assertRaises(ValidationError):
            estado2.clean()  # Esto debería lanzar una ValidationError debido a la validación personalizada