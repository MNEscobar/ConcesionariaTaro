from django.contrib import admin
from .models import Solicitud

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    # Columnas que se verán en la tabla principal del administrador
    list_display = ('nombre_titular', 'apellido_titular', 'dni_titular', 'modelo_auto', 'fecha_solicitud')
    # Filtros laterales para buscar rápidamente
    list_filter = ('modelo_auto', 'tipo_plan', 'condicion_laboral_garante')
    # Barra de búsqueda superior
    search_fields = ('dni_titular', 'nombre_titular', 'apellido_titular', 'email_titular')
    # Protegemos los registros para que sean de solo lectura (buena práctica en auditorías)
    readonly_fields = ('fecha_solicitud',)