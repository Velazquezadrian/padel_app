// Variables globales
let horarioSeleccionado = null;
let canchaSeleccionada = null;
let fechaSeleccionada = null;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Configurar fecha actual
    const inputFecha = document.getElementById('fecha');
    const hoy = new Date().toISOString().split('T')[0];
    inputFecha.value = hoy;
    fechaSeleccionada = hoy;
    
    // Event listener para cambio de fecha
    inputFecha.addEventListener('change', function() {
        fechaSeleccionada = this.value;
        // Actualizar semáforos para la nueva fecha
        actualizarTodosSemaforos();
        if (horarioSeleccionado) {
            cargarCanchas(horarioSeleccionado);
        }
    });
    
    // Event listeners para botones de horario
    const botonesHorario = document.querySelectorAll('.horario-btn');
    botonesHorario.forEach(btn => {
        btn.addEventListener('click', function() {
            seleccionarHorario(this);
        });
    });
    
    // Event listener para cerrar modal
    const modal = document.getElementById('modalReserva');
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.onclick = function() {
            cerrarModal();
        };
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            cerrarModal();
        }
    };
    
    // Event listener para formulario de reserva
    const formReserva = document.getElementById('formReserva');
    if (formReserva) {
        formReserva.addEventListener('submit', function(e) {
            e.preventDefault();
            realizarReserva();
        });
    }
});

async function actualizarTodosSemaforos() {
    const botonesHorario = document.querySelectorAll('.horario-btn');
    for (const btn of botonesHorario) {
        const horario = btn.getAttribute('data-horario');
        try {
            const response = await fetch('/api/obtener_disponibilidad', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    horario: horario,
                    fecha: fechaSeleccionada
                })
            });
            
            const data = await response.json();
            if (data.success) {
                actualizarSemaforoHorario(horario, data.canchas, btn);
            }
        } catch (error) {
            console.error('Error cargando semáforo:', error);
        }
    }
}

function actualizarSemaforoHorario(horario, canchas, boton) {
    const totalCanchas = canchas.length;
    const canchasDisponibles = canchas.filter(c => c.disponible).length;
    
    // Eliminar semáforo previo si existe
    const semaforoExistente = boton.querySelector('.semaforo');
    if (semaforoExistente) {
        semaforoExistente.remove();
    }
    
    // Crear nuevo semáforo
    const semaforo = document.createElement('span');
    semaforo.className = 'semaforo';
    
    if (canchasDisponibles === totalCanchas) {
        // Todas disponibles - Verde
        semaforo.innerHTML = '🟢';
        semaforo.classList.add('verde');
    } else if (canchasDisponibles === 0) {
        // Todas ocupadas - Rojo
        semaforo.innerHTML = '🔴';
        semaforo.classList.add('rojo');
    } else {
        // Parcialmente ocupadas - Amarillo
        semaforo.innerHTML = '🟡';
        semaforo.classList.add('amarillo');
    }
    
    boton.appendChild(semaforo);
}

function seleccionarHorario(boton) {
    // Remover selección previa
    document.querySelectorAll('.horario-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Marcar como seleccionado
    boton.classList.add('selected');
    horarioSeleccionado = boton.getAttribute('data-horario');
    
    // Mostrar sección de canchas
    document.getElementById('horarioSeleccionado').textContent = horarioSeleccionado;
    document.getElementById('canchasSection').style.display = 'block';
    
    // Cargar canchas disponibles
    cargarCanchas(horarioSeleccionado);
    
    // Scroll suave a la sección de canchas
    setTimeout(() => {
        document.getElementById('canchasSection').scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

async function cargarCanchas(horario) {
    try {
        const response = await fetch('/api/obtener_disponibilidad', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                horario: horario,
                fecha: fechaSeleccionada
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarCanchas(data.canchas);
            // Actualizar semáforo del horario seleccionado
            const boton = document.querySelector(`[data-horario="${horario}"]`);
            if (boton) {
                actualizarSemaforoHorario(horario, data.canchas, boton);
            }
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Error al cargar canchas: ' + error.message);
    }
}

function mostrarCanchas(canchas) {
    const grid = document.getElementById('canchasGrid');
    grid.innerHTML = '';
    
    canchas.forEach((cancha) => {
        const canchaDiv = document.createElement('div');
        canchaDiv.className = `cancha-card ${cancha.disponible ? 'disponible' : 'reservada'}`;
        
        if (cancha.disponible) {
            canchaDiv.innerHTML = `
                <div class="cancha-header">
                    <h3>Cancha ${cancha.numero}</h3>
                    <span class="status-badge disponible">Disponible</span>
                </div>
                <div class="cancha-imagen">
                    <img src="/static/images/Padel.jpg" 
                         alt="Cancha ${cancha.numero}"
                         onerror="this.src='/static/images/cancha-default.svg'">
                </div>
                <button class="btn-reservar" onclick="abrirModalReserva('${cancha.id}', ${cancha.numero})">
                    ✅ Reservar
                </button>
            `;
        } else {
            canchaDiv.innerHTML = `
                <div class="cancha-header">
                    <h3>Cancha ${cancha.numero}</h3>
                    <span class="status-badge reservada">Reservada</span>
                </div>
                <div class="cancha-imagen reservada-overlay">
                    <img src="/static/images/Padel.jpg" 
                         alt="Cancha ${cancha.numero}"
                         onerror="this.src='/static/images/cancha-default.svg'">
                    <div class="overlay">🔒</div>
                </div>
                <div class="reserva-info-card">
                    <p><strong>Reservado por:</strong> ${cancha.reserva.nombre}</p>
                    <button class="btn-cancelar" onclick="cancelarReserva('${cancha.id}', ${cancha.numero})">
                        ❌ Cancelar Reserva
                    </button>
                </div>
            `;
        }
        
        grid.appendChild(canchaDiv);
    });
}

function abrirModalReserva(canchaId, numeroCancha) {
    canchaSeleccionada = canchaId;
    document.getElementById('infoFecha').textContent = new Date(fechaSeleccionada).toLocaleDateString('es-ES');
    document.getElementById('infoHorario').textContent = horarioSeleccionado;
    document.getElementById('infoCancha').textContent = `Cancha ${numeroCancha}`;
    document.getElementById('modalReserva').style.display = 'block';
}

function cerrarModal() {
    document.getElementById('modalReserva').style.display = 'none';
    document.getElementById('nombreCliente').value = '';
}

async function realizarReserva() {
    const nombreCliente = document.getElementById('nombreCliente').value;
    
    if (!nombreCliente) {
        alert('Por favor ingrese un nombre');
        return;
    }
    
    try {
        const response = await fetch('/api/reservar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                horario: horarioSeleccionado,
                cancha_id: canchaSeleccionada,
                nombre_cliente: nombreCliente,
                fecha: fechaSeleccionada
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ ' + data.message);
            cerrarModal();
            cargarCanchas(horarioSeleccionado);
            // Actualizar todos los semáforos
            setTimeout(() => actualizarTodosSemaforos(), 300);
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function cancelarReserva(canchaId, numeroCancha) {
    if (!confirm(`¿Cancelar reserva de Cancha ${numeroCancha}?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/cancelar_reserva', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                horario: horarioSeleccionado,
                cancha_id: canchaId,
                fecha: fechaSeleccionada
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ ' + data.message);
            cargarCanchas(horarioSeleccionado);
            // Actualizar todos los semáforos
            setTimeout(() => actualizarTodosSemaforos(), 300);
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
