// Devuelve true si existe un turno fijo para la cancha, día y horario dados
async function existeTurnoFijo(canchaId, fecha, horario) {
    // Obtener día de la semana (0=Lunes, 6=Domingo)
    const fechaObj = new Date(fecha);
    const diaSemana = fechaObj.getDay(); // 0=Domingo, 1=Lunes...
    // Ajustar a 0=Lunes, 6=Domingo
    const diaSemanaPadel = (diaSemana === 0) ? 6 : diaSemana - 1;

    // Obtener todos los turnos fijos
    let turnosFijos = [];
    try {
        const resp = await fetch('/api/obtener_turnos_fijos');
        const data = await resp.json();
        if (data.success && Array.isArray(data.turnos_fijos)) {
            turnosFijos = data.turnos_fijos;
        }
    } catch (e) {
        return false;
    }
    // Buscar si existe uno para ese día, horario y cancha
    return turnosFijos.some(t => t.dia_semana === diaSemanaPadel && t.horario === horario && t.cancha_id === canchaId);
}
