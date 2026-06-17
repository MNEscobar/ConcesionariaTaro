from django import forms
from datetime import date
from .models import Solicitud

class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        # Usamos 'exclude' para decirle a Django que incluya todos los campos del modelo, excepto 'fecha_solicitud' ya que ese se genera automáticamente por el sistema.
        exclude = ['fecha_solicitud']
        # Definimos widgets específicos para los campos de fecha para que el navegador muestre el calendario
        widgets = {
            'fecha_nac_titular': forms.DateInput(attrs={'type': 'date'}),
            'fecha_nac_garante': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bucle para recorrer todos los campos y agregarles una clase CSS base
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
    # --- VALIDACIONES PERSONALIZADAS DE EDAD (Mínimo 18 años) ---
    def validar_mayoria_edad(self, fecha_nac, tipo_persona):
        if not fecha_nac:
            return fecha_nac
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        
        if edad < 18:
            # Esto arrojará un error específico para el campo, que luego se mostrara en el HTML
            raise forms.ValidationError(f"El {tipo_persona} debe ser mayor de 18 años.")
        return fecha_nac

    def clean_fecha_nac_titular(self):
        fecha = self.cleaned_data.get('fecha_nac_titular')
        return self.validar_mayoria_edad(fecha, 'titular')

    def clean_fecha_nac_garante(self):
        fecha = self.cleaned_data.get('fecha_nac_garante')
        return self.validar_mayoria_edad(fecha, 'garante')