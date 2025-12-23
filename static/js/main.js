// Abre el modal de backup desde cualquier parte
function abrirModalBackup() {
    const modal = document.getElementById('modalBackup');
    if (modal) {
        modal.style.display = 'block';
        document.getElementById('importarBackupSection').style.display = 'none';
    }
}

function cerrarModalBackup() {
    const modal = document.getElementById('modalBackup');
    if (modal) {
        modal.style.display = 'none';
        document.getElementById('importarBackupSection').style.display = 'none';
    }
}


function abrirModalImportarBackup() {
    const modal = document.getElementById('modalImportarBackup');
    if (modal) {
        modal.style.display = 'block';
        // Resetear el formulario y mensaje
        document.getElementById('formImportarBackup').reset();
        document.getElementById('mensajeImportarBackup').style.display = 'none';
        // Disparar el input file automáticamente
        setTimeout(() => {
            const input = document.getElementById('archivoBackup');
            if (input && input.offsetParent !== null) input.click();
        }, 300);
    }
}

function cerrarModalImportarBackup() {
    const modal = document.getElementById('modalImportarBackup');
    if (modal) {
        modal.style.display = 'none';
    }
}

function cerrarImportarBackupSection() {
    document.getElementById('importarBackupSection').style.display = 'none';
}

// --- Importar backup desde el modal de backup ---
document.addEventListener('DOMContentLoaded', function() {
    // Nada especial, el botón llama a abrirModalImportarBackup()
    const formImportarBackup = document.getElementById('formImportarBackup');
    if (formImportarBackup) {
        formImportarBackup.addEventListener('submit', async function(e) {
            e.preventDefault();
            const archivoInput = document.getElementById('archivoBackup');
            const archivo = archivoInput.files[0];
            if (!archivo) {
                alert('⚠️ Por favor selecciona un archivo');
                return;
            }
            if (!confirm('⚠️ ADVERTENCIA: Esta acción reemplazará todos los datos actuales. ¿Continuar?')) {
                return;
            }
            const mensajeDiv = document.getElementById('mensajeImportarBackup');
            mensajeDiv.style.display = 'block';
            mensajeDiv.style.backgroundColor = '#d1ecf1';
            mensajeDiv.style.color = '#0c5460';
            mensajeDiv.style.border = '2px solid #bee5eb';
            mensajeDiv.textContent = '⏳ Importando datos...';
            try {
                const formData = new FormData();
                formData.append('archivo', archivo);
                const response = await fetch('/api/importar_backup', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (data.success) {
                    mensajeDiv.style.backgroundColor = '#d4edda';
                    mensajeDiv.style.color = '#155724';
                    mensajeDiv.style.border = '2px solid #c3e6cb';
                    mensajeDiv.innerHTML = `✅ <strong>Datos importados correctamente</strong><br>📊 Reservas: ${data.estadisticas.reservas}<br>📋 Turnos Fijos: ${data.estadisticas.turnos_fijos}<br>🔵 Ausencias: ${data.estadisticas.ausencias}`;
                    setTimeout(() => { window.location.reload(); }, 2000);
                } else {
                    mensajeDiv.style.backgroundColor = '#f8d7da';
                    mensajeDiv.style.color = '#721c24';
                    mensajeDiv.style.border = '2px solid #f5c6cb';
                    mensajeDiv.textContent = '❌ Error: ' + data.message;
                }
            } catch (error) {
                mensajeDiv.style.backgroundColor = '#f8d7da';
                mensajeDiv.style.color = '#721c24';
                mensajeDiv.style.border = '2px solid #f5c6cb';
                mensajeDiv.textContent = '❌ Error: ' + error.message;
            }
        });
    }
});
// Variables globales
let horarioSeleccionado = null;
let canchaSeleccionada = null;
let fechaSeleccionada = null;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Cargar tema guardado
    cargarTemaGuardado();
    
    // Cargar información del footer y badge de licencia
    cargarInfoFooter();
    
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

function generarVistaProductosCancha(reserva) {
    // Muestra base, extras y total en formato compacto, siempre visible
    let base = reserva.precio_base || 0;
    let descuento = reserva.descuento_aplicado || 0;
    let final = reserva.precio_final || base;
    let extras = reserva.precio_extras || 0;
    let productos = reserva.productos_lista && reserva.productos_lista.length > 0 ? reserva.productos_lista : [];
    const mostrarDetalle = productos.length > 0 && productos.length <= 2;

    let html = `<div style="background: #e7f6f8; padding: 8px 10px; border-radius: 6px; margin: 6px 0; border-left: 3px solid #17a2b8; font-size: 0.85em;">
        <div style="display: flex; flex-direction: column; gap: 2px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>💲Base:</span>
                <span style="font-weight: bold;">$${base.toLocaleString('es-AR')}</span>
            </div>`;
    if (descuento > 0) {
        html += `<div style="display: flex; justify-content: space-between; align-items: center; color: #e67e22;">
            <span>Descuento:</span>
            <span>-$${descuento.toLocaleString('es-AR')}</span>
        </div>`;
    }
    if (productos.length > 0) {
        if (mostrarDetalle) {
            productos.forEach(producto => {
                html += `<div style="display: flex; justify-content: space-between; color: #0c5460; line-height: 1.3;">
                    <span>🛒 ${producto.nombre}</span>
                    <span style="font-weight: bold;">$${producto.precio.toLocaleString('es-AR')}</span>
                </div>`;
            });
        } else {
            html += `<div style="display: flex; justify-content: space-between; color: #0c5460;">
                <span>🛒 ${productos.length} productos</span>
            </div>`;
        }
    }
    if (extras > 0) {
        html += `<div style="display: flex; justify-content: space-between; color: #17a2b8;">
            <span>+ Extras:</span>
            <span>$${extras.toLocaleString('es-AR')}</span>
        </div>`;
    }
    html += `<div style="display: flex; justify-content: space-between; font-weight: bold; color: #229954; border-top: 1px solid #17a2b8; margin-top: 4px; padding-top: 4px;">
        <span>Total:</span>
        <span>$${(final + extras).toLocaleString('es-AR')}</span>
    </div>
    </div>
    </div>`;
    return html;
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
            mostrarNotificacion('❌ Error: ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error al cargar canchas: ' + error.message);
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
            let productosHtml = '';
            let tieneReservaTemporal = (
                typeof cancha.reserva === 'object' &&
                Object.keys(cancha.reserva).length > 0
            );
            if (
                tieneReservaTemporal &&
                Array.isArray(cancha.reserva.productos_lista) &&
                cancha.reserva.productos_lista.length > 0
            ) {
                productosHtml = generarVistaProductosCancha(cancha.reserva);
            }
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
                ${productosHtml}
                ${tieneReservaTemporal ? `
                    <button class="btn-cancelar" onclick="cancelarReserva('${cancha.id}', ${cancha.numero})">
                        ❌ Cancelar reserva temporal
                    </button>
                ` : `
                    <button class="btn-reservar" onclick="abrirModalReserva('${cancha.id}', ${cancha.numero})">
                        ✅ Reservar (Temporal)
                    </button>
                `}
                <button class="btn-secondary" onclick="abrirModalProductos('${cancha.id}', ${cancha.numero}, false, null)" style="margin: 10px 0 0 0;">
                    🛒 Agregar Productos
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
                    ${generarVistaProductosCancha(cancha.reserva)}
                    ${esFijo ? '<p class="turno-fijo-badge">🔁 Turno Fijo Semanal</p>' : ''}
                    ${esFijo ? `<button class="btn-warning" onclick="marcarAusencia('${cancha.id}', ${cancha.numero}, ${idTurnoFijo})" style="margin-bottom: 10px;">
                        ⚠️ Marcar Ausencia
                    </button>` : ''}
                    <button class="btn-secondary" onclick="abrirModalProductos('${cancha.id}', ${cancha.numero}, ${esFijo}, ${idTurnoFijo})" style="margin-bottom: 10px;">
                        🛒 ${cancha.reserva.productos_lista && cancha.reserva.productos_lista.length > 0 ? 'Editar' : 'Agregar'} Productos
                    </button>
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
    const grupoCheckbox = checkboxFijo.closest('.checkbox-group');


    // Por defecto ocultar la casilla
    grupoCheckbox.style.display = 'none';
    checkboxFijo.checked = false;
    mensajeDia.style.display = 'none';

    // Solo mostrar la casilla si NO existe turno fijo para ese día, horario y cancha Y no es un horario de ausencia temporal
    existeTurnoFijo(canchaId, fechaSeleccionada, horarioSeleccionado).then(existe => {
        // Si existe turno fijo, ocultar casilla
        if (existe) {
            grupoCheckbox.style.display = 'none';
            checkboxFijo.checked = false;
            mensajeDia.style.display = 'none';
            return;
        }
        // Verificar si la cancha está disponible por ausencia temporal de turno fijo
        fetch('/api/obtener_disponibilidad', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ horario: horarioSeleccionado, fecha: fechaSeleccionada })
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.success) {
                const cancha = data.canchas.find(c => c.id === canchaId);
                if (cancha && cancha.turno_fijo_ausente) {
                    // Es un horario de ausencia temporal, NO permitir crear turno fijo
                    grupoCheckbox.style.display = 'none';
                    checkboxFijo.checked = false;
                    mensajeDia.style.display = 'none';
                    return;
                }
            }
            // Si no hay turno fijo ni ausencia, mostrar casilla
            grupoCheckbox.style.display = '';
            checkboxFijo.addEventListener('change', function() {
                if (this.checked) {
                    mensajeDia.textContent = `✓ Se reservará para todos los ${diaSemana} a las ${horarioSeleccionado}`;
                    mensajeDia.style.display = 'block';
                } else {
                    mensajeDia.style.display = 'none';
                }
            }, { once: true });
        });
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
        mostrarNotificacion('⚠️ Por favor ingrese un nombre');
        return;
    }
    
    if (!telefonoCliente) {
        mostrarNotificacion('⚠️ Por favor ingrese un teléfono');
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
                es_fijo: esFijo,
                productos_extras: '',
                precio_extras: 0
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarNotificacion('✅ ' + data.message);
            cerrarModal();
            cargarCanchas(horarioSeleccionado);
            // Actualizar todos los semáforos
            setTimeout(() => actualizarTodosSemaforos(), 300);
        } else {
            mostrarNotificacion('❌ ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error: ' + error.message);
    }
}

async function cancelarReserva(canchaId, numeroCancha, idTurnoFijo = null) {
    const mensaje = idTurnoFijo 
        ? `¿Eliminar el turno fijo de la Cancha ${numeroCancha}? Se eliminará para todas las semanas.`
        : `¿Cancelar reserva de Cancha ${numeroCancha}?`;

    // Eliminado confirm(mensaje)

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
            mostrarNotificacion('✅ ' + data.message);
            cargarCanchas(horarioSeleccionado);
            // Actualizar todos los semáforos
            setTimeout(() => actualizarTodosSemaforos(), 300);
        } else {
            mostrarNotificacion('❌ ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error: ' + error.message);
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
            mostrarNotificacion('❌ Error al cargar turnos fijos');
        }
    } catch (error) {
        mostrarNotificacion('❌ Error: ' + error.message);
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
                <button class="btn-eliminar-chico" onclick="eliminarTurnoFijo(${turno.id})" title="Eliminar turno fijo">
                    🗑️
                </button>
            </div>
        `;
    });
    html += '</div>';
    
    lista.innerHTML = html;
}

async function eliminarTurnoFijo(idTurno) {
    // Eliminado confirm('¿Eliminar este turno fijo? Se eliminará para todas las semanas.')

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
            mostrarNotificacion('✅ ' + data.message);
            abrirModalTurnosFijos(); // Recargar lista
            actualizarTodosSemaforos();
        } else {
            mostrarNotificacion('❌ ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error: ' + error.message);
    }
}

async function marcarAusencia(canchaId, numeroCancha, idTurnoFijo) {
    // Eliminado confirm(`¿Marcar ausencia para esta fecha?\n\nLa cancha ${numeroCancha} quedará disponible solo para hoy, pero el turno fijo se mantendrá para las próximas semanas.`)

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
            mostrarNotificacion('✅ ' + data.message);
            cargarCanchas(horarioSeleccionado);
            setTimeout(() => actualizarTodosSemaforos(), 300);
        } else {
            mostrarNotificacion('❌ ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error: ' + error.message);
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
            mostrarNotificacion('✅ ' + data.message);
            cargarCanchas(horarioSeleccionado);
            setTimeout(() => actualizarTodosSemaforos(), 300);
        } else {
            mostrarNotificacion('❌ ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error: ' + error.message);
    }
}

// ============================================
// Funciones de Personalización de Temas
// ============================================

async function cargarTemaGuardado() {
    try {
        const response = await fetch('/api/obtener_tema');
        const data = await response.json();
        
        if (data.success) {
            aplicarTema(data.tema);
        }
    } catch (error) {
        console.error('Error al cargar tema:', error);
    }
}

function aplicarTema(tema) {
    document.body.setAttribute('data-theme', tema);
    
    // Actualizar tarjetas activas en el modal
    const tarjetas = document.querySelectorAll('.theme-card');
    tarjetas.forEach(card => {
        if (card.getAttribute('data-theme') === tema) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });
}

async function cambiarTema(tema) {
    try {
        const response = await fetch('/api/guardar_tema', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tema: tema })
        });
        
        const data = await response.json();
        
        if (data.success) {
            aplicarTema(tema);
            // Mostrar feedback visual
            mostrarNotificacion(`✨ Tema "${obtenerNombreTema(tema)}" aplicado`);
        } else {
            mostrarNotificacion('❌ ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error al cambiar tema: ' + error.message);
    }
}

function obtenerNombreTema(tema) {
    const nombres = {
        'clasico': 'Clásico Padel',
        'oceano': 'Océano Azul',
        'atardecer': 'Atardecer Naranja',
        'noche': 'Noche Morada'
    };
    return nombres[tema] || tema;
}

function aplicarTamano(tamano) {
    document.body.setAttribute('data-size', tamano);
    
    // Actualizar tarjetas activas en el modal
    const tarjetas = document.querySelectorAll('.size-card');
    tarjetas.forEach(card => {
        if (card.getAttribute('data-size') === tamano) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });
}

async function cambiarTamano(tamano) {
    try {
        const response = await fetch('/api/guardar_tamano', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tamano: tamano })
        });
        
        const data = await response.json();
        
        if (data.success) {
            aplicarTamano(tamano);
            // Mostrar feedback visual
            const nombres = {
                'compacto': 'Compacto',
                'normal': 'Normal',
                'grande': 'Grande'
            };
            mostrarNotificacion(`📐 Tamaño "${nombres[tamano]}" aplicado`);
        } else {
            mostrarNotificacion('❌ ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error al cambiar tamaño: ' + error.message);
    }
}

function mostrarNotificacion(mensaje) {
    // Crear notificación temporal
    const notif = document.createElement('div');
    notif.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--primary-color);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notif.textContent = mensaje;
    document.body.appendChild(notif);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notif.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}

function abrirModalPersonalizacion() {
    const modal = document.getElementById('modalPersonalizacion');
    modal.style.display = 'block';
    
    // Marcar tema actual como activo
    const temaActual = document.body.getAttribute('data-theme') || 'clasico';
    aplicarTema(temaActual);
    
    // Marcar tamaño actual como activo
    const tamanoActual = document.body.getAttribute('data-size') || 'normal';
    aplicarTamano(tamanoActual);
}

function cerrarModalPersonalizacion() {
    const modal = document.getElementById('modalPersonalizacion');
    modal.style.display = 'none';
}

// ============================================
// FUNCIONES DE CONFIGURACIÓN
// ============================================

function abrirModalConfiguracion() {
    const modal = document.getElementById('modalConfiguracion');
    modal.style.display = 'block';
}

function cerrarModalConfiguracion() {
    const modal = document.getElementById('modalConfiguracion');
    modal.style.display = 'none';
    // Auto-actualizar disponibilidad al salir de configuración
    setTimeout(() => actualizarTodosSemaforos(), 300);
}

// ============================================
// FUNCIONES DE FINANZAS
// ============================================

let tipoReporteActual = 'dia';

function abrirModalFinanzas() {
    const modal = document.getElementById('modalFinanzas');
    
    // Configurar fecha actual
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('fechaFinanzas').value = hoy;
    
    // Configurar semana actual
    const semana = obtenerSemanaActual();
    document.getElementById('semanaFinanzas').value = semana;
    
    // Configurar mes actual
    const mes = hoy.substring(0, 7); // YYYY-MM
    document.getElementById('mesFinanzas').value = mes;
    
    // Configurar fechas desde/hasta
    document.getElementById('fechaDesde').value = hoy;
    document.getElementById('fechaHasta').value = hoy;
    
    // Seleccionar tipo "día" por defecto
    seleccionarTipoReporte('dia');
    
    modal.style.display = 'block';
}

function cerrarModalFinanzas() {
    const modal = document.getElementById('modalFinanzas');
    modal.style.display = 'none';
}

function seleccionarTipoReporte(tipo) {
    tipoReporteActual = tipo;
    
    // Actualizar botones activos
    document.querySelectorAll('.btn-tipo-reporte').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tipo="${tipo}"]`).classList.add('active');
    
    // Ocultar todos los selectores
    document.querySelectorAll('.selector-fechas').forEach(selector => {
        selector.style.display = 'none';
    });
    
    // Mostrar el selector correspondiente
    switch(tipo) {
        case 'dia':
            document.getElementById('selectorDia').style.display = 'flex';
            break;
        case 'varios':
            document.getElementById('selectorVarios').style.display = 'block';
            break;
        case 'semanal':
            document.getElementById('selectorSemanal').style.display = 'block';
            break;
        case 'mensual':
            document.getElementById('selectorMensual').style.display = 'block';
            break;
    }
    
    // Ocultar reporte anterior
    document.getElementById('reporteFinanzas').style.display = 'none';
}

function obtenerSemanaActual() {
    const hoy = new Date();
    const año = hoy.getFullYear();
    const primerDia = new Date(año, 0, 1);
    const dias = Math.floor((hoy - primerDia) / (24 * 60 * 60 * 1000));
    const semana = Math.ceil((dias + primerDia.getDay() + 1) / 7);
    return `${año}-W${semana.toString().padStart(2, '0')}`;
}

async function cargarReporteFinanzas() {
    let fechas = {};
    let titulo = '';
    
    // Obtener fechas según el tipo de reporte
    switch(tipoReporteActual) {
        case 'dia':
            const fecha = document.getElementById('fechaFinanzas').value;
            if (!fecha) {
                mostrarNotificacion('⚠️ Por favor selecciona una fecha');
                return;
            }
            fechas = { fecha_desde: fecha, fecha_hasta: fecha };
            titulo = `📈 Resumen del ${formatearFecha(fecha)}`;
            break;
            
        case 'varios':
            const fechaDesde = document.getElementById('fechaDesde').value;
            const fechaHasta = document.getElementById('fechaHasta').value;
            if (!fechaDesde || !fechaHasta) {
                mostrarNotificacion('⚠️ Por favor selecciona ambas fechas');
                return;
            }
            if (fechaDesde > fechaHasta) {
                mostrarNotificacion('⚠️ La fecha "Desde" no puede ser posterior a la fecha "Hasta"');
                return;
            }
            fechas = { fecha_desde: fechaDesde, fecha_hasta: fechaHasta };
            titulo = `📈 Resumen del ${formatearFecha(fechaDesde)} al ${formatearFecha(fechaHasta)}`;
            break;
            
        case 'semanal':
            const semana = document.getElementById('semanaFinanzas').value;
            if (!semana) {
                mostrarNotificacion('⚠️ Por favor selecciona una semana');
                return;
            }
            const [año, numSemana] = semana.split('-W');
            const fechasSemana = obtenerFechasDeSemana(parseInt(año), parseInt(numSemana));
            fechas = { fecha_desde: fechasSemana.inicio, fecha_hasta: fechasSemana.fin };
            titulo = `📈 Resumen Semanal (Semana ${numSemana} de ${año})`;
            break;
            
        case 'mensual':
            const mes = document.getElementById('mesFinanzas').value;
            if (!mes) {
                mostrarNotificacion('⚠️ Por favor selecciona un mes');
                return;
            }
            const [añoMes, numMes] = mes.split('-');
            const fechasMes = obtenerFechasDeMes(parseInt(añoMes), parseInt(numMes));
            fechas = { fecha_desde: fechasMes.inicio, fecha_hasta: fechasMes.fin };
            const nombreMes = new Date(añoMes, numMes - 1).toLocaleString('es-AR', { month: 'long', year: 'numeric' });
            titulo = `📈 Resumen Mensual (${nombreMes.charAt(0).toUpperCase() + nombreMes.slice(1)})`;
            break;
    }
    
    try {
        const response = await fetch('/api/finanzas/reporte_rango', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(fechas)
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarReporteFinanzas(data, titulo);
        } else {
            mostrarNotificacion('❌ ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error al cargar reporte: ' + error.message);
    }
}

function obtenerFechasDeSemana(año, semana) {
    // Primer día del año
    const primerDia = new Date(año, 0, 1);
    // Calcular el lunes de la semana especificada
    const diasHastaSemana = (semana - 1) * 7;
    const lunes = new Date(primerDia);
    lunes.setDate(primerDia.getDate() + diasHastaSemana - primerDia.getDay() + 1);
    
    // Domingo de esa semana
    const domingo = new Date(lunes);
    domingo.setDate(lunes.getDate() + 6);
    
    return {
        inicio: lunes.toISOString().split('T')[0],
        fin: domingo.toISOString().split('T')[0]
    };
}

function obtenerFechasDeMes(año, mes) {
    // Primer día del mes
    const primerDia = new Date(año, mes - 1, 1);
    // Último día del mes
    const ultimoDia = new Date(año, mes, 0);
    
    return {
        inicio: primerDia.toISOString().split('T')[0],
        fin: ultimoDia.toISOString().split('T')[0]
    };
}

function formatearFecha(fecha) {
    const [año, mes, dia] = fecha.split('-');
    return `${dia}/${mes}/${año}`;
}

function mostrarReporteFinanzas(data) {
    const reporteDiv = document.getElementById('reporteFinanzas');
    reporteDiv.style.display = 'block';
    
    // Formatear moneda
    const formatoPrecio = (monto) => {
        return '$' + Math.round(monto).toLocaleString('es-AR');
    };
    
    // Resumen
    document.getElementById('totalRecaudado').textContent = formatoPrecio(data.resumen.total_recaudado);
    document.getElementById('totalTurnos').textContent = data.resumen.total_turnos;
    document.getElementById('totalExtras').textContent = formatoPrecio(data.resumen.total_extras || 0);
    document.getElementById('totalDescuentos').textContent = formatoPrecio(data.resumen.total_descuentos);
    
    document.getElementById('turnosRegulares').textContent = data.resumen.turnos_regulares + ' turnos';
    document.getElementById('turnosFijos').textContent = data.resumen.turnos_fijos + ' turnos';
    
    // Promoción activa
    const promocionDiv = document.getElementById('promocionActiva');
    if (data.resumen.descuento_promocion_actual > 0) {
        promocionDiv.style.display = 'block';
        document.getElementById('textoPromocion').textContent = 
            `${data.resumen.descuento_promocion_actual}% de descuento en todos los turnos nuevos`;
    } else {
        promocionDiv.style.display = 'none';
    }
    
    // Detalle de turnos
    const detalleDiv = document.getElementById('detalleFinanzas');
    if (data.detalle.length === 0) {
        detalleDiv.innerHTML = '<p style="text-align: center; color: var(--text-light); padding: 30px;">No hay turnos registrados para esta fecha</p>';
    } else {
        let html = '<div style="display: flex; flex-direction: column; gap: 10px;">';
        
        data.detalle.forEach(turno => {
            const tipoColor = turno.tipo === 'Turno Fijo' ? 'var(--success-color)' : 'var(--primary-color)';
            const tipoIcon = turno.tipo === 'Turno Fijo' ? '🔁' : '💵';
            const tieneExtras = turno.precio_extras && turno.precio_extras > 0;
            
            html += `
                <div style="background-color: var(--card-bg); border: 2px solid var(--border-color); border-left: 5px solid ${tipoColor}; padding: 15px; border-radius: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div style="flex: 1;">
                            <div style="font-weight: bold; color: ${tipoColor}; margin-bottom: 5px;">
                                ${tipoIcon} ${turno.tipo}
                            </div>
                            <div style="font-size: 0.9em; color: var(--text-light);">
                                ⏰ ${turno.horario} | 🎾 Cancha ${turno.cancha} | 👤 ${turno.cliente}
                            </div>
                            ${tieneExtras ? `<div style="font-size: 0.85em; color: #17a2b8; margin-top: 5px;">
                                🧃 ${turno.productos_extras}
                            </div>` : ''}
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.85em; color: var(--text-light); text-decoration: ${turno.descuento > 0 ? 'line-through' : 'none'};">
                                ${turno.descuento > 0 ? formatoPrecio(turno.precio_base) : ''}
                            </div>
                            ${turno.descuento > 0 ? `<div style="font-size: 0.85em; color: var(--warning-color);">-${formatoPrecio(turno.descuento)}</div>` : ''}
                            <div style="font-size: 1.3em; font-weight: bold; color: var(--success-color);">
                                ${formatoPrecio(turno.precio_final)}
                            </div>
                            ${tieneExtras ? `<div style="font-size: 0.9em; color: #17a2b8; margin-top: 3px;">
                                + ${formatoPrecio(turno.precio_extras)} (extras)
                            </div>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        detalleDiv.innerHTML = html;
    }
}

// ============================================
// FUNCIONES DE PRODUCTOS EXTRAS
// ============================================

let datosProductosActual = {};
let listaProductosTemp = []; // Lista temporal de productos en el modal

async function abrirModalProductos(canchaId, numeroCancha, esFijo, idTurnoFijo) {
    datosProductosActual = {
        canchaId: canchaId,
        numeroCancha: numeroCancha,
        horario: horarioSeleccionado,
        fecha: fechaSeleccionada,
        esFijo: esFijo,
        idTurnoFijo: idTurnoFijo
    };
    
    document.getElementById('infoProductosReserva').innerHTML = `
        <p><strong>Cancha:</strong> ${numeroCancha}</p>
        <p><strong>Horario:</strong> ${horarioSeleccionado}</p>
        <p><strong>Fecha:</strong> ${new Date(fechaSeleccionada).toLocaleDateString('es-ES')}</p>
    `;
    
    // Cargar productos existentes de la reserva
    await cargarProductosExistentes();
    
    // Limpiar campos de entrada
    document.getElementById('nombreProducto').value = '';
    document.getElementById('precioProducto').value = '';
    
    const modal = document.getElementById('modalProductos');
    modal.style.display = 'block';
}

async function cargarProductosExistentes() {
    // Obtener la reserva actual para cargar sus productos
    try {
        const response = await fetch('/api/obtener_disponibilidad', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                horario: datosProductosActual.horario,
                fecha: datosProductosActual.fecha
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Buscar la cancha específica
            const cancha = data.canchas.find(c => c.id === datosProductosActual.canchaId);
            if (cancha && cancha.reserva && cancha.reserva.productos_lista) {
                listaProductosTemp = [...cancha.reserva.productos_lista];
            } else {
                listaProductosTemp = [];
            }
            actualizarVistaProductos();
        }
    } catch (error) {
        console.error('Error al cargar productos:', error);
        listaProductosTemp = [];
        actualizarVistaProductos();
    }
}

function agregarProductoALista() {
    const nombre = document.getElementById('nombreProducto').value.trim();
    const precio = parseFloat(document.getElementById('precioProducto').value);
    
    if (!nombre) {
        mostrarNotificacion('⚠️ Por favor ingrese el nombre del producto');
        return;
    }
    
    if (!precio || precio <= 0) {
        mostrarNotificacion('⚠️ Por favor ingrese un precio válido');
        return;
    }
    
    // Agregar a la lista temporal
    listaProductosTemp.push({
        nombre: nombre,
        precio: precio
    });
    
    // Limpiar campos
    document.getElementById('nombreProducto').value = '';
    document.getElementById('precioProducto').value = '';
    document.getElementById('nombreProducto').focus();
    
    // Actualizar vista
    actualizarVistaProductos();
}

function eliminarProducto(index) {
    if (confirm('¿Eliminar este producto?')) {
        listaProductosTemp.splice(index, 1);
        actualizarVistaProductos();
    }
}

function actualizarVistaProductos() {
    const contenedor = document.getElementById('listaProductosAgregados');
    
    if (listaProductosTemp.length === 0) {
        contenedor.innerHTML = `
            <div style="text-align: center; padding: 12px; color: var(--text-light); background: var(--bg-color); border-radius: 8px; font-size: 13px;">
                📦 No hay productos agregados todavía
            </div>
        `;
        document.getElementById('totalProductos').textContent = '0';
        return;
    }
    
    let html = '<div style="display: flex; flex-direction: column; gap: 6px;">';
    let total = 0;
    
    listaProductosTemp.forEach((producto, index) => {
        total += producto.precio;
        html += `
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        background: white; padding: 8px 10px; border-radius: 6px; 
                        border: 1px solid var(--border-color); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="flex: 1; display: flex; align-items: center; gap: 8px;">
                    <div style="font-weight: 600; color: var(--text-color); font-size: 13px;">
                        ${producto.nombre}
                    </div>
                    <div style="color: var(--success-color); font-size: 14px; font-weight: bold;">
                        $${producto.precio.toLocaleString('es-AR')}
                    </div>
                </div>
                <button onclick="eliminarProducto(${index})" 
                        style="background: var(--accent-color); color: white; border: none; 
                               padding: 6px 10px; border-radius: 5px; cursor: pointer; 
                               font-size: 16px; transition: all 0.3s; line-height: 1;"
                        onmouseover="this.style.transform='scale(1.1)'"
                        onmouseout="this.style.transform='scale(1)'"
                        title="Eliminar producto">
                    🗑️
                </button>
            </div>
        `;
    });
    
    html += '</div>';
    contenedor.innerHTML = html;
    document.getElementById('totalProductos').textContent = total.toLocaleString('es-AR');
}

async function guardarTodosLosProductos() {
    if (listaProductosTemp.length === 0) {
        mostrarNotificacion('⚠️ No hay productos para guardar');
        return;
    }
    
    try {
        const response = await fetch('/api/agregar_productos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fecha: datosProductosActual.fecha,
                horario: datosProductosActual.horario,
                cancha_id: datosProductosActual.canchaId,
                es_fijo: datosProductosActual.esFijo,
                id_turno_fijo: datosProductosActual.idTurnoFijo,
                productos_lista: listaProductosTemp
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarNotificacion('✅ Productos guardados correctamente');
            cerrarModalProductos();
            cargarCanchas(horarioSeleccionado);
        } else {
            mostrarNotificacion('❌ ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error: ' + error.message);
    }
}

function cerrarModalProductos() {
    const modal = document.getElementById('modalProductos');
    modal.style.display = 'none';
    // No limpiamos listaProductosTemp aquí para mantener los productos
    // Solo se limpia al cargar productos existentes en abrirModalProductos
}

// ====================================
// FUNCIONES BACKUP/RESTAURACIÓN
// ====================================

async function exportarBackup() {
    try {
        const response = await fetch('/api/exportar_backup');
        const data = await response.json();
        
        if (data.success) {
            const archivos = data.archivos.join(', ');
            mostrarNotificacion(`✅ Backup guardado exitosamente - ${archivos}`);
        } else {
            mostrarNotificacion('❌ Error: ' + data.message);
        }
    } catch (error) {
        mostrarNotificacion('❌ Error al exportar: ' + error.message);
    }
}

function abrirModalImportarBackup() {
    document.getElementById('modalImportarBackup').style.display = 'block';
    document.getElementById('formImportarBackup').reset();
    document.getElementById('mensajeImportarBackup').style.display = 'none';
}

function cerrarModalImportarBackup() {
    document.getElementById('modalImportarBackup').style.display = 'none';
}

document.getElementById('formImportarBackup').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const archivoInput = document.getElementById('archivoBackup');
    const archivo = archivoInput.files[0];
    
    if (!archivo) {
        mostrarNotificacion('⚠️ Por favor selecciona un archivo');
        return;
    }
    
    if (!confirm('⚠️ ADVERTENCIA: Esta acción reemplazará todos los datos actuales. ¿Continuar?')) {
        return;
    }
    
    const mensajeDiv = document.getElementById('mensajeImportarBackup');
    mensajeDiv.style.display = 'block';
    mensajeDiv.style.backgroundColor = '#d1ecf1';
    mensajeDiv.style.color = '#0c5460';
    mensajeDiv.style.border = '2px solid #bee5eb';
    mensajeDiv.textContent = '⏳ Importando datos...';
    
    try {
        const formData = new FormData();
        formData.append('archivo', archivo);
        
        const response = await fetch('/api/importar_backup', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            mensajeDiv.style.backgroundColor = '#d4edda';
            mensajeDiv.style.color = '#155724';
            mensajeDiv.style.border = '2px solid #c3e6cb';
            mensajeDiv.innerHTML = `
                ✅ <strong>Datos importados correctamente</strong><br>
                📊 Reservas: ${data.estadisticas.reservas}<br>
                📋 Turnos Fijos: ${data.estadisticas.turnos_fijos}<br>
                🔵 Ausencias: ${data.estadisticas.ausencias}
            `;
            
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            mensajeDiv.style.backgroundColor = '#f8d7da';
            mensajeDiv.style.color = '#721c24';
            mensajeDiv.style.border = '2px solid #f5c6cb';
            mensajeDiv.textContent = '❌ Error: ' + data.message;
        }
    } catch (error) {
        mensajeDiv.style.backgroundColor = '#f8d7da';
        mensajeDiv.style.color = '#721c24';
        mensajeDiv.style.border = '2px solid #f5c6cb';
        mensajeDiv.textContent = '❌ Error: ' + error.message;
    }
});

// ====================================
// VERIFICACIÓN DE LICENCIA (Ya no se usa, reemplazada por cargarInfoFooter)
// ====================================
// Función eliminada - ahora se usa cargarInfoFooter() que muestra el badge temporal

// ============================================
// FUNCIÓN DE FOOTER CON INFO DE LICENCIA
// ============================================

async function cargarInfoFooter() {
    try {
        const response = await fetch('/api/info_licencia');
        const data = await response.json();
        
        const licenciaInfo = document.getElementById('licenciaInfo');
        const badgeLicencia = document.getElementById('badgeLicencia');
        
        if (data.success && data.valida) {
            if (data.dias_restantes <= 7) {
                // Advertencia - licencia por vencer
                licenciaInfo.innerHTML = `Licencia: ${data.dias_restantes} días restantes`;
                badgeLicencia.style.background = 'linear-gradient(135deg, #ff9800, #f57c00)';
            } else {
                // Licencia válida
                licenciaInfo.innerHTML = `Licencia: ${data.dias_restantes} días restantes`;
                badgeLicencia.style.background = 'linear-gradient(135deg, #4caf50, #388e3c)';
            }
        } else {
            licenciaInfo.innerHTML = `${data.mensaje || 'Sin licencia'}`;
            badgeLicencia.style.background = 'linear-gradient(135deg, #f44336, #d32f2f)';
        }
        
        // Ocultar SOLO el badge de licencia después de 10 segundos
        setTimeout(() => {
            badgeLicencia.classList.add('hidden');
            // Remover del DOM después de la animación
            setTimeout(() => {
                badgeLicencia.style.display = 'none';
            }, 500);
        }, 10000);
        
    } catch (error) {
        console.error('Error al cargar info de licencia:', error);
        const licenciaInfo = document.getElementById('licenciaInfo');
        const badgeLicencia = document.getElementById('badgeLicencia');
        
        licenciaInfo.innerHTML = 'Error al verificar';
        badgeLicencia.style.background = 'linear-gradient(135deg, #9e9e9e, #616161)';
        
        // Ocultar badge después de 10 segundos aunque haya error
        setTimeout(() => {
            badgeLicencia.classList.add('hidden');
            setTimeout(() => {
                badgeLicencia.style.display = 'none';
            }, 500);
        }, 10000);
    }
}

