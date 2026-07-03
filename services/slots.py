"""Lógica pura de generación de turnos disponibles (sin dependencias externas)."""
from datetime import datetime, timedelta, time

from config_terapias import TERAPIAS, HORARIOS_ATENCION, HORIZONTE_DIAS


def _parse_hora(hora_str):
    h, m = hora_str.split(":")
    return time(int(h), int(m))


def generar_turnos_disponibles(terapia_key, ahora, busy_intervals, horizonte_dias=HORIZONTE_DIAS):
    """Devuelve lista de (inicio: datetime, fin: datetime) libres para una terapia.

    ahora: datetime actual (inyectado para poder testear).
    busy_intervals: lista de (inicio: datetime, fin: datetime) ya ocupados (calendario + bloqueos manuales).
    """
    terapia = TERAPIAS[terapia_key]
    duracion = timedelta(minutes=terapia["duracion_min"])
    ventanas_por_dia = HORARIOS_ATENCION[terapia["grupo"]]

    fecha_minima = (ahora + timedelta(days=terapia["min_dias"])).date()
    fecha_inicio = max(fecha_minima, ahora.date())

    disponibles = []
    for offset in range(horizonte_dias):
        dia = fecha_inicio + timedelta(days=offset)
        ventanas = ventanas_por_dia.get(dia.weekday())
        if not ventanas:
            continue
        for hora_ini_str, hora_fin_str in ventanas:
            ventana_inicio = datetime.combine(dia, _parse_hora(hora_ini_str))
            ventana_fin = datetime.combine(dia, _parse_hora(hora_fin_str))
            cursor = ventana_inicio
            while cursor + duracion <= ventana_fin:
                slot_fin = cursor + duracion
                if not _solapa(cursor, slot_fin, busy_intervals):
                    disponibles.append((cursor, slot_fin))
                cursor += duracion
    return disponibles


def _solapa(inicio, fin, busy_intervals):
    for b_ini, b_fin in busy_intervals:
        if inicio < b_fin and fin > b_ini:
            return True
    return False


def agrupar_por_dia(slots):
    """Agrupa una lista de (inicio, fin) por fecha, para mostrar en la UI."""
    agrupados = {}
    for inicio, fin in slots:
        agrupados.setdefault(inicio.date(), []).append((inicio, fin))
    return dict(sorted(agrupados.items()))
