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
        
        // Verificar si es turno fijo ausente
        if (cancha.turno_fijo_ausente) {
            canchaDiv.className = 'cancha-card turno-fijo-ausente';
            canchaDiv.innerHTML = `
                <div class="cancha-header">
                    <h3>Cancha ${cancha.numero}</h3>
                    <span class="status-badge turno-fijo-ausente">🔁 Ausente</span>
                </div>
                <div class="cancha-imagen">
                    <img src="/static/images/Padel.jpg" 
                         alt="Cancha ${cancha.numero}"
                         onerror="this.src='/static/images/cancha-default.svg'">
                </div>
                <div class="turno-fijo-info">
                    <p><strong>Turno fijo de:</strong> ${cancha.turno_fijo_ausente.nombre}</p>
                    ${cancha.turno_fijo_ausente.telefono ? `<p><strong>📞:</strong> ${cancha.turno_fijo_ausente.telefono}</p>` : ''}
                    <p class="ausencia-text">⚠️ Marcado como ausente para hoy</p>
                </div>
                <button class="btn-reservar" onclick="abrirModalReserva('${cancha.id}', ${cancha.numero})">
                    ✅ Reservar (Temporal)
                </button>
                <button class="btn-secondary" onclick="cancelarAusencia('${cancha.id}', ${cancha.numero}, ${cancha.turno_fijo_ausente.id_turno_fijo})" style="margin-top: 10px;">
                    🔄 Restaurar Turno Fijo
                </button>
            `;
        } else if (cancha.disponible) {
            canchaDiv.className = 'cancha-card disponible';
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
            canchaDiv.className = 'cancha-card reservada';
            const esFijo = cancha.reserva.es_fijo || false;
            const idTurnoFijo = cancha.reserva.id_turno_fijo || null;
            
            canchaDiv.innerHTML = `
                <div class="cancha-header">
                    <h3>Cancha ${cancha.numero}</h3>
                    <span class="status-badge reservada">${esFijo ? '🔁 Fijo' : 'Reservada'}</span>
                </div>
                <div class="cancha-imagen reservada-overlay">
                    <img src="/static/images/Padel.jpg" 
                         alt="Cancha ${cancha.numero}"
                         onerror="this.src='/static/images/cancha-default.svg'">
                    <div class="overlay">🔒</div>
                </div>
                <div class="reserva-info-card">
                    <p><strong>Reservado por:</strong> ${cancha.reserva.nombre}</p>
                    ${cancha.reserva.telefono ? `<p><strong>📞 Teléfono:</strong> ${cancha.reserva.telefono}</p>` : ''}
                    ${esFijo ? '<p class="turno-fijo-badge">🔁 Turno Fijo Semanal</p>' : ''}
                    ${esFijo ? `<button class="btn-warning" onclick="marcarAusencia('${cancha.id}', ${cancha.numero}, ${idTurnoFijo})" style="margin-bottom: 10px;">
                        ⚠️ Marcar Ausencia
                    </button>` : ''}
                    <button class="btn-cancelar" onclick="cancelarReserva('${cancha.id}', ${cancha.numero}, ${idTurnoFijo})">
                        ❌ ${esFijo ? 'Eliminar Turno Fijo' : 'Cancelar Reserva'}
                    </button>
                </div>
            `;
        }
        
        grid.appendChild(canchaDiv);
    });
}

function abrirModalReserva(canchaId, numeroCancha) {
    canchaSeleccionada = canchaId;
    const fecha = new Date(fechaSeleccionada);
    const diasSemana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const diaSemana = diasSemana[fecha.getDay()];
    
    document.getElementById('infoFecha').textContent = fecha.toLocaleDateString('es-ES');
    document.getElementById('infoHorario').textContent = horarioSeleccionado;
    document.getElementById('infoCancha').textContent = `Cancha ${numeroCancha}`;
    
    // Mostrar mensaje de día de la semana
    const checkboxFijo = document.getElementById('esFijo');
    const mensajeDia = document.getElementById('diaSemanaMensaje');
    
    checkboxFijo.addEventListener('change', function() {
        if (this.checked) {
            mensajeDia.textContent = `✓ Se reservará para todos los ${diaSemana} a las ${horarioSeleccionado}`;
            mensajeDia.style.display = 'block';
        } else {
            mensajeDia.style.display = 'none';
        }
    });
    
    document.getElementById('modalReserva').style.display = 'block';
}

function cerrarModal() {
    document.getElementById('modalReserva').style.display = 'none';
    document.getElementById('nombreCliente').value = '';
    document.getElementById('telefonoCliente').value = '';
    document.getElementById('esFijo').checked = false;
    document.getElementById('diaSemanaMensaje').style.display = 'none';
}

async function realizarReserva() {
    const nombreCliente = document.getElementById('nombreCliente').value;
    const telefonoCliente = document.getElementById('telefonoCliente').value;
    const esFijo = document.getElementById('esFijo').checked;
    
    if (!nombreCliente) {
        alert('Por favor ingrese un nombre');
        return;
    }
    
    if (!telefonoCliente) {
        alert('Por favor ingrese un teléfono');
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
                telefono_cliente: telefonoCliente,
                fecha: fechaSeleccionada,
                es_fijo: esFijo
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

async function cancelarReserva(canchaId, numeroCancha, idTurnoFijo = null) {
    const mensaje = idTurnoFijo 
        ? `¿Eliminar el turno fijo de la Cancha ${numeroCancha}? Se eliminará para todas las semanas.`
        : `¿Cancelar reserva de Cancha ${numeroCancha}?`;
    
    if (!confirm(mensaje)) {
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
                fecha: fechaSeleccionada,
                id_turno_fijo: idTurnoFijo
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

async function abrirModalTurnosFijos() {
    try {
        const response = await fetch('/api/obtener_turnos_fijos');
        const data = await response.json();
        
        if (data.success) {
            mostrarTurnosFijos(data.turnos_fijos);
            document.getElementById('modalTurnosFijos').style.display = 'block';
        } else {
            alert('Error al cargar turnos fijos');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function cerrarModalTurnosFijos() {
    document.getElementById('modalTurnosFijos').style.display = 'none';
}

function mostrarTurnosFijos(turnos) {
    const lista = document.getElementById('listaTurnosFijos');
    
    if (turnos.length === 0) {
        lista.innerHTML = '<p style="text-align:center; color:#666;">No hay turnos fijos configurados</p>';
        return;
    }
    
    let html = '<div class="turnos-fijos-lista">';
    turnos.forEach(turno => {
        html += `
            <div class="turno-fijo-item">
                <div class="turno-fijo-info">
                    <h4>🔁 ${turno.dia_nombre} - ${turno.horario}</h4>
                    <p><strong>Cancha:</strong> ${turno.cancha_id.replace('cancha_', '')}</p>
                    <p><strong>Cliente:</strong> ${turno.nombre_cliente}</p>
                    ${turno.telefono_cliente ? `<p><strong>📞 Teléfono:</strong> ${turno.telefono_cliente}</p>` : ''}
                </div>
                <button class="btn-cancelar" onclick="eliminarTurnoFijo(${turno.id})">
                    🗑️ Eliminar
                </button>
            </div>
        `;
    });
    html += '</div>';
    
    lista.innerHTML = html;
}

async function eliminarTurnoFijo(idTurno) {
    if (!confirm('¿Eliminar este turno fijo? Se eliminará para todas las semanas.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/cancelar_reserva', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id_turno_fijo: idTurno
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ ' + data.message);
            abrirModalTurnosFijos(); // Recargar lista
            actualizarTodosSemaforos();
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function marcarAusencia(canchaId, numeroCancha, idTurnoFijo) {
    if (!confirm(`¿Marcar ausencia para esta fecha?\n\nLa cancha ${numeroCancha} quedará disponible solo para hoy, pero el turno fijo se mantendrá para las próximas semanas.`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/marcar_ausencia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                fecha: fechaSeleccionada,
                horario: horarioSeleccionado,
                cancha_id: canchaId,
                id_turno_fijo: idTurnoFijo
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ ' + data.message);
            cargarCanchas(horarioSeleccionado);
            setTimeout(() => actualizarTodosSemaforos(), 300);
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function cancelarAusencia(canchaId, numeroCancha, idTurnoFijo) {
    if (!confirm(`¿Restaurar el turno fijo para esta fecha?\n\nLa cancha ${numeroCancha} volverá a estar ocupada por el turno fijo.`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/cancelar_ausencia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                fecha: fechaSeleccionada,
                horario: horarioSeleccionado,
                cancha_id: canchaId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ ' + data.message);
            cargarCanchas(horarioSeleccionado);
            setTimeout(() => actualizarTodosSemaforos(), 300);
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
