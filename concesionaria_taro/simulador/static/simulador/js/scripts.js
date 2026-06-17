// 1. HERO IMAGE 
const hero = document.querySelector('.hero');
if (hero) {
    hero.style.backgroundImage = `url(${hero.dataset.bgImage})`;
}

// 2. CONTROL DE PESTAÑAS 
function mostrarTab(event, id) {
    document.querySelectorAll('.contenido-pestana').forEach(t => t.style.display = 'none');
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('activo'));
    document.getElementById(id).style.display = 'block';
    event.currentTarget.classList.add('activo');
}

const modeloKeys = ['gol', 'tracker', 'corolla', 'a6'];

document.querySelectorAll('.btn-seleccionar').forEach(function(btn, index) {
    btn.addEventListener('click', function() {
        // Limpiar selección anterior
        document.querySelectorAll('.modelo-card').forEach(function(card) {
            card.classList.remove('seleccionado');
        });
        document.querySelectorAll('.btn-seleccionar').forEach(function(b) {
            b.classList.remove('activo');
            b.textContent = 'Seleccionar';
        });

        // Aplicar selección actual
        this.closest('.modelo-card').classList.add('seleccionado');
        this.classList.add('activo');
        this.textContent = 'Seleccionado';

        // Sincronizar select del formulario
        document.querySelector('select[name="modelo_auto"]').value = modeloKeys[index];
    });
});


// 3. CONSUMO DE API EXTERNA: COTIZACIÓN DEL DÓLAR 
async function cotizarDolarOficial(inputElement) {
    const valorPesos = parseFloat(inputElement.value);
    
    // Si el campo está vacío o no es un número válido, no hace nada
    if (!valorPesos || isNaN(valorPesos)) return;

    try {
        // Consumimos la API pública en tiempo real
        const response = await fetch('https://dolarapi.com/v1/dolares/oficial');
        const data = await response.json();
        
        // Extrae el valor de venta
        const precioDolar = data.venta;
        const equivalenteDolares = (valorPesos / precioDolar).toFixed(2);

        // Busca si ya existe el mensaje debajo del input, sino lo crea
        let mensajeDolar = inputElement.nextElementSibling;
        if (!mensajeDolar || !mensajeDolar.classList.contains('alerta-dolar')) {
            mensajeDolar = document.createElement('small');
            mensajeDolar.classList.add('alerta-dolar');
            mensajeDolar.style.display = 'block';
            mensajeDolar.style.color = '#4CAF50'; // Verde para darle visibilidad positiva
            mensajeDolar.style.marginTop = '5px';
            mensajeDolar.style.fontWeight = 'bold';
            inputElement.parentNode.insertBefore(mensajeDolar, inputElement.nextSibling);
        }

        // Inserta el mensaje exacto
        mensajeDolar.textContent = `Este importe equivale a ${equivalenteDolares} dólares bajo la cotización del dólar oficial del día ($${precioDolar}).`;

    } catch (error) {
        console.error("Error al consultar la API del Dólar:", error);
    }
}

// Escuchamos el evento 'blur' (cuando el usuario quita el foco del campo) en los inputs de ingresos
const inputsPesos = document.querySelectorAll('input[name="ingreso_titular"], input[name="ingreso_garante"]');
inputsPesos.forEach(input => {
    input.addEventListener('blur', function() {
        cotizarDolarOficial(this);
    });
});


// 4. ENVÍO ASÍNCRONO Y GESTIÓN DE ERRORES (UX Mejorada)
const formSimulador = document.getElementById('form-simulador');

if (formSimulador) {
    const btnSubmit = document.getElementById('btn-submit');

    // --- LÓGICA DE BOTÓN INTELIGENTE ---
    // Escucha cualquier cambio en los inputs y verifica si todos los campos requeridos tienen datos
    formSimulador.addEventListener('input', function() {
        // Formateamos visualmente si está activo o inactivo
        if (formSimulador.checkValidity()) {
            btnSubmit.disabled = false;
            btnSubmit.style.opacity = '1';
            btnSubmit.style.cursor = 'pointer';
        } else {
            btnSubmit.disabled = true;
            btnSubmit.style.opacity = '0.5';
            btnSubmit.style.cursor = 'not-allowed';
        }
    });

    // --- ENVÍO AL BACKEND ---
    formSimulador.addEventListener('submit', async function(e) {
        e.preventDefault(); 
        
        // 1. Limpiar errores previos antes de enviar
        document.querySelectorAll('.error-msg').forEach(el => el.textContent = '');
        document.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));

        const textoOriginal = btnSubmit.textContent;
        btnSubmit.textContent = 'Calculando...';
        btnSubmit.disabled = true;

        const formData = new FormData(formSimulador);

        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest' 
                }
            });

            const data = await response.json();

            if (data.success) {
                // ÉXITO: Mostramos el informe
                const contenedorFinanciamiento = document.querySelector('.financiamiento-contenido');
                if (!contenedorFinanciamiento.classList.contains('con-informe')) {
                    contenedorFinanciamiento.classList.add('con-informe');
                }

                // Actualizamos los textos del informe
                document.querySelector('.informe-modelo').textContent = data.informe.vehiculo_nombre;
                document.querySelector('.informe-vehiculo p:nth-child(3)').textContent = data.informe.precio_vehiculo;
                
                const filas = document.querySelectorAll('.informe-fila span:last-child');
                filas[0].textContent = data.informe.plan_nombre; 
                filas[1].textContent = data.informe.cantidad_cuotas; 
                filas[2].textContent = data.informe.importe_adjudicacion; 
                filas[3].textContent = data.informe.importe_retiro; 
                filas[4].textContent = data.informe.tasa_interes; 
                document.querySelector('.informe-total').textContent = data.informe.cuota_mensual;

                // Mapeo manual de imágenes (ya que los <select> de Django no traen data-img por defecto)
                const imgMap = {
                    'gol': '/static/simulador/img/VW_Gol.jpg',
                    'tracker': '/static/simulador/img/Chevrolet_Tracker.jpg',
                    'corolla': '/static/simulador/img/Toyota_CorollaCross.jpg',
                    'a6': '/static/simulador/img/Audi_A6.jpg'
                };
                
                const modeloKey = document.querySelector('select[name="modelo_auto"]').value;
                const imagenInforme = document.querySelector('.informe-vehiculo img');
                
                if (imagenInforme && imgMap[modeloKey]) {
                    imagenInforme.src = imgMap[modeloKey];
                    imagenInforme.alt = data.informe.vehiculo_nombre;
                }

                // Opcional: Hacer scroll suave hacia el informe para guiar al usuario
                contenedorFinanciamiento.scrollIntoView({ behavior: 'smooth' });

            } else {
                // ERROR DE VALIDACIÓN O DE EDAD MINIMA
                if (data.errores) {
                    // Iteramos sobre el JSON de errores que nos mandó Django
                    for (const [campo, mensajes] of Object.entries(data.errores)) {
                        // Buscamos el pequeño span debajo del input defectuoso
                        const errorSpan = document.querySelector(`.error-msg[data-field="${campo}"]`);
                        const inputDefectuoso = document.querySelector(`[name="${campo}"]`);
                        
                        if (errorSpan && inputDefectuoso) {
                            errorSpan.textContent = mensajes[0]; // Mostramos el primer error
                            errorSpan.style.color = '#d32f2f'; // Texto rojo
                            errorSpan.style.fontSize = '0.8rem';
                            errorSpan.style.marginTop = '4px';
                            errorSpan.style.display = 'block';
                            
                            // Agregamos clase para el borde rojo
                            inputDefectuoso.classList.add('input-error');
                        }
                    }
                } 
                
                // Si el error es de lógica de negocio (Ej: menor de edad que validamos en views.py)
                if (data.motivo && !data.errores) {
                    // Si es un error general, lo ponemos arriba del botón
                    let errorGeneral = document.getElementById('error-general');
                    if (!errorGeneral) {
                        errorGeneral = document.createElement('div');
                        errorGeneral.id = 'error-general';
                        errorGeneral.style.color = '#d32f2f';
                        errorGeneral.style.fontWeight = 'bold';
                        errorGeneral.style.marginBottom = '10px';
                        btnSubmit.parentNode.insertBefore(errorGeneral, btnSubmit);
                    }
                    errorGeneral.textContent = data.motivo;
                }
            }

        } catch (error) {
            console.error('Error en el servidor:', error);
            // Mensaje de caída de servidor
        } finally {
            // Restaurar botón
            btnSubmit.textContent = textoOriginal;
            // Solo lo activamos de nuevo si el form sigue siendo válido
            btnSubmit.disabled = !formSimulador.checkValidity();
        }
    });
}