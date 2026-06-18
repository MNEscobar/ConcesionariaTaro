import os
import django

# 1. Configurar el entorno para que Python entienda que es un script de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taro.settings')
django.setup()

from django.contrib.auth.models import User

# 2. Definir las credenciales de tu administrador
USERNAME = 'admin'
EMAIL = 'admin@taro.com'
PASSWORD = 'Matias2026/' # Usa la contraseña que prefieras

# 3. Lógica para crearlo solo si no existe (así no da error en futuros despliegues)
if not User.objects.filter(username=USERNAME).exists():
    print(f"Creando superusuario: {USERNAME}...")
    User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
    print("¡Superusuario creado exitosamente!")
else:
    print(f"El superusuario {USERNAME} ya existe en la base de datos.")