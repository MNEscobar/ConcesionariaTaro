from django.db import models

class Solicitud(models.Model):
    # --- OPCIONES PREDEFINIDAS ---
    class CondicionLaboral(models.TextChoices):
        DEPENDIENTE = 'dependiente', 'Dependiente'
        INDEPENDIENTE = 'independiente', 'Independiente'

    class ModeloAuto(models.TextChoices):
        GOL = 'gol', 'Volkswagen Gol Trend'
        TRACKER = 'tracker', 'Chevrolet Tracker'
        COROLLA = 'corolla', 'Toyota Corolla Cross'
        A6 = 'a6', 'Audi A6'

    class TipoPlan(models.TextChoices):
        PLAN_70 = '70', 'Plan 70/30'
        PLAN_80 = '80', 'Plan 80/20'

    class CantidadCuotas(models.IntegerChoices):
        CUOTAS_72 = 72, '72 cuotas'
        CUOTAS_84 = 84, '84 cuotas'
        CUOTAS_120 = 120, '120 cuotas'

    # --- 1. DATOS PERSONALES (TITULAR) ---
    nombre_titular = models.CharField(max_length=100, verbose_name="Nombre del Titular")
    apellido_titular = models.CharField(max_length=100, verbose_name="Apellido del Titular")
    dni_titular = models.CharField(max_length=15, verbose_name="DNI del Titular")
    fecha_nac_titular = models.DateField(verbose_name="Fecha de Nacimiento (Titular)")
    email_titular = models.EmailField(verbose_name="Correo Electrónico")
    tel_titular = models.CharField(max_length=20, verbose_name="Teléfono")
    ingreso_titular = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ingreso Neto (Titular)")

    # --- 2. DATOS DEL GARANTE ---
    nombre_garante = models.CharField(max_length=100, verbose_name="Nombre del Garante")
    apellido_garante = models.CharField(max_length=100, verbose_name="Apellido del Garante")
    dni_garante = models.CharField(max_length=15, verbose_name="DNI del Garante")
    fecha_nac_garante = models.DateField(verbose_name="Fecha de Nacimiento (Garante)")
    condicion_laboral_garante = models.CharField(
        max_length=20, 
        choices=CondicionLaboral.choices, 
        verbose_name="Condición Laboral"
    )
    antiguedad_laboral_garante = models.PositiveIntegerField(verbose_name="Antigüedad Laboral (años)")
    ingreso_garante = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ingreso Neto (Garante)")

    # --- 3. DATOS DEL PLAN ---
    modelo_auto = models.CharField(
        max_length=20, 
        choices=ModeloAuto.choices, 
        verbose_name="Modelo Elegido"
    )
    tipo_plan = models.CharField(
        max_length=2, 
        choices=TipoPlan.choices, 
        verbose_name="Tipo de Plan"
    )
    cantidad_cuotas = models.IntegerField(
        choices=CantidadCuotas.choices, 
        verbose_name="Cantidad de Cuotas"
    )

    # --- DATOS DE SISTEMA ---
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")

    class Meta:
        verbose_name = "Solicitud de Simulación"
        verbose_name_plural = "Solicitudes de Simulación"
        ordering = ['-fecha_solicitud'] # Ordena de la más reciente a la más antigua

    def __str__(self):
        return f"{self.nombre_titular} {self.apellido_titular} - {self.get_modelo_auto_display()}"