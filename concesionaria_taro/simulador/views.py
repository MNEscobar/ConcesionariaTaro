from django.shortcuts import render
from django.http import JsonResponse
from datetime import date
from .forms import SolicitudForm
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics
from .serializers import SolicitudSerializer
from .models import Solicitud

class SolicitudListCreateView(generics.ListCreateAPIView):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer

def index(request):
    # Si la petición es POST, significa que el usuario envió el formulario
    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        
        # 1. Validación de estructura y tipos de datos (Django Forms)
        if form.is_valid():
            datos = form.cleaned_data

            # --- LÓGICA DE NEGOCIO Y CÁLCULOS FINANCIEROS ---
            
            # A. Precios de vehículos
            precios_vehiculos = {
                'gol': 10000000,
                'tracker': 30000000,
                'corolla': 50000000,
                'a6': 100000000
            }
            precio_auto = precios_vehiculos[datos['modelo_auto']]

            # B. Validación de Edad Máxima (No superar 80 años al finalizar el plan)
            hoy = date.today()
            fecha_nac = datos['fecha_nac_titular']
            # Calculamos la edad exacta actual
            edad_actual = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            # Sumamos la duración del plan en años
            duracion_anios = datos['cantidad_cuotas'] / 12
            edad_al_finalizar = edad_actual + duracion_anios

            if edad_al_finalizar > 80:
                return JsonResponse({
                    'success': False, 
                    'motivo': f'No calificas. La edad al finalizar el plan ({edad_al_finalizar:.1f} años) supera el límite de 80 años.'
                })

            # C. Cálculos del Plan y Adjudicación
            if datos['tipo_plan'] == '70':
                porc_financiado = 0.70
                porc_adjudicacion = 0.30
            else: # Es '80'
                porc_financiado = 0.80
                porc_adjudicacion = 0.20

            importe_adjudicacion = precio_auto * porc_adjudicacion
            importe_retiro = precio_auto * 0.08  # 8% para gastos de patentamiento
            monto_financiado = precio_auto * porc_financiado

            # D. Cálculo de Cuota y Tasa de Interés (6.5%)
            # Interés aplicado al monto financiado y distribuido en las cuotas
            interes_total = monto_financiado * 0.065
            total_a_financiar = monto_financiado + interes_total
            cuota_mensual = total_a_financiar / datos['cantidad_cuotas']

            # E. Validación de Ingresos del Garante
            ingreso_minimo_requerido = cuota_mensual * 4
            # Convertimos float a Decimal para poder compararlo de forma segura
            if float(datos['ingreso_garante']) < ingreso_minimo_requerido:
                return JsonResponse({
                    'success': False, 
                    'motivo': f'No calificas. El ingreso neto del garante debe ser al menos 4 veces el valor de la cuota (${ingreso_minimo_requerido:,.2f}).'
                })

            # --- GUARDADO Y RESPUESTA EXITOSA ---
            
            # Si pasó todas las validaciones matemáticas, guardamos en la Base de Datos
            solicitud = form.save()

            # Preparamos los datos financieros formateados para que JS actualice el "Informe" en el HTML
            informe_data = {
                'vehiculo_nombre': solicitud.get_modelo_auto_display(),
                'precio_vehiculo': f"${precio_auto:,.2f}",
                'plan_nombre': solicitud.get_tipo_plan_display(),
                'cantidad_cuotas': datos['cantidad_cuotas'],
                'importe_adjudicacion': f"${importe_adjudicacion:,.2f}",
                'importe_retiro': f"${importe_retiro:,.2f}",
                'tasa_interes': "6.50%",
                'cuota_mensual': f"${cuota_mensual:,.2f}"
            }

            # --- ENVÍO DE CORREO ELECTRÓNICO ---
            asunto = f"Confirmación de Simulación Automotriz - {solicitud.get_modelo_auto_display()}"
            mensaje = f"""
            Hola {solicitud.nombre_titular} {solicitud.apellido_titular},
            
            Tu simulación para el vehículo {solicitud.get_modelo_auto_display()} ha sido procesada con éxito.
            
            --- DETALLE DEL INFORME ---
            Vehículo: {solicitud.get_modelo_auto_display()}
            Precio del Vehículo: {informe_data['precio_vehiculo']}
            Plan Seleccionado: {informe_data['plan_nombre']}
            Cantidad de Cuotas: {informe_data['cantidad_cuotas']}
            Importe para Adjudicación: {informe_data['importe_adjudicacion']}
            Importe para Retiro (Patentamiento): {informe_data['importe_retiro']}
            Tasa de Interés: {informe_data['tasa_interes']}
            
            VALOR FINAL DE LA CUOTA MENSUAL: {informe_data['cuota_mensual']}
            ---------------------------
            
            Gracias por confiar en nuestra concesionaria.
            """
            
            try:
                send_mail(
                    asunto,
                    mensaje,
                    settings.EMAIL_HOST_USER,
                    [solicitud.email_titular],
                    fail_silently=False,
                )
            except Exception as e:
                # Si el correo falla, lo registramos en la consola pero no rompemos la experiencia del usuario
                print(f"Error al enviar el correo SMTP: {e}")

            return JsonResponse({'success': True, 'informe': informe_data})
        
        else:
            # Si fallan las validaciones de Django Forms (ej. menor de edad, formato erróneo)
            # Retornamos los errores exactos (form.errors) para que JS los pinte en pantalla
            return JsonResponse({
                'success': False, 
                'motivo': 'Revisa los campos marcados en rojo.', 
                'errores': form.errors
            })

    # SI ES UNA PETICIÓN GET (El usuario entra por primera vez)
    else:
        form = SolicitudForm() # Creamos un formulario vacío
    # FALTABA PASAR EL CONTEXTO {'form': form} AL RENDERIZAR EL HTML, POR ESO NO SE VEÍA EL FORMULARIO EN PANTALLA
    return render(request, 'simulador/index.html', {'form': form})