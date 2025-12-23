document.addEventListener('DOMContentLoaded', function() {
        // Backup/Restore handlers reutilizados del main.js
        window.exportarBackup = async function() {
            try {
                const response = await fetch('/api/exportar_backup');
                const data = await response.json();
                if (data.success) {
                    alert(`✅ Backup guardado exitosamente - ${data.archivos.join(', ')}`);
                } else {
                    alert('❌ Error: ' + data.message);
                }
            } catch (error) {
                alert('❌ Error al exportar: ' + error.message);
            }
        };

        window.abrirModalImportarBackup = function() {
            document.getElementById('modalImportarBackup').style.display = 'block';
            document.getElementById('formImportarBackup').reset();
            document.getElementById('mensajeImportarBackup').style.display = 'none';
        };

        window.cerrarModalImportarBackup = function() {
            document.getElementById('modalImportarBackup').style.display = 'none';
        };

        document.getElementById('formImportarBackup').addEventListener('submit', async function(e) {
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
    const form = document.getElementById('configForm');
    
    // Actualizar preview al cargar
    actualizarPreview();
    
    // Event listeners para actualizar preview en tiempo real
    document.getElementById('horario_inicio').addEventListener('change', actualizarPreview);
    document.getElementById('horario_fin').addEventListener('change', actualizarPreview);
    document.getElementById('duracion_turno').addEventListener('change', actualizarPreview);
    document.getElementById('cantidad_canchas').addEventListener('change', actualizarPreview);
    
    // Submit del formulario
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            cantidad_canchas: document.getElementById('cantidad_canchas').value,
            horario_inicio: document.getElementById('horario_inicio').value,
            horario_fin: document.getElementById('horario_fin').value,
            duracion_turno: document.getElementById('duracion_turno').value
        };
        
        try {
            const response = await fetch('/api/guardar_config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            const mensaje = document.getElementById('mensaje');
            mensaje.style.display = 'block';
            
            if (data.success) {
                mensaje.className = 'mensaje success';
                mensaje.textContent = '✅ ' + data.message;
                
                // Redirigir después de 2 segundos
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                mensaje.className = 'mensaje error';
                mensaje.textContent = '❌ ' + data.message;
            }
        } catch (error) {
            console.error('Error:', error);
            const mensaje = document.getElementById('mensaje');
            mensaje.style.display = 'block';
            mensaje.className = 'mensaje error';
            mensaje.textContent = '❌ Error al guardar la configuración';
        }
    });
});

function actualizarPreview() {
    const inicio = document.getElementById('horario_inicio').value;
    const fin = document.getElementById('horario_fin').value;
    const duracion = parseInt(document.getElementById('duracion_turno').value);
    const canchas = parseInt(document.getElementById('cantidad_canchas').value);
    
    if (inicio && fin && duracion) {
        const cantidadTurnos = calcularCantidadTurnos(inicio, fin, duracion);
        document.getElementById('cantidadTurnos').textContent = cantidadTurnos;
    }
    
    document.getElementById('cantidadCanchas').textContent = canchas;
}

function calcularCantidadTurnos(inicio, fin, duracion) {
    const [horaInicio, minInicio] = inicio.split(':').map(Number);
    const [horaFin, minFin] = fin.split(':').map(Number);
    
    const minutosInicio = horaInicio * 60 + minInicio;
    const minutosFin = horaFin * 60 + minFin;
    
    const totalMinutos = minutosFin - minutosInicio;
    return Math.floor(totalMinutos / duracion);
}
