document.addEventListener('DOMContentLoaded', function() {
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
