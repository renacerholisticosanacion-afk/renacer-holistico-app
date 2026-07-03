import streamlit as st
from datetime import datetime, timedelta

from config_terapias import (
    TERAPIAS, DATOS_PAGO, POLITICA_CANCELACION, HORIZONTE_DIAS, NOTIFICACION_EMAIL,
)
from services.slots import generar_turnos_disponibles, agrupar_por_dia
from services.bootstrap import get_backends
from services.secrets_utils import to_dict

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def formatear_fecha(fecha):
    return f"{DIAS_ES[fecha.weekday()]} {fecha.day} de {MESES_ES[fecha.month]}"


def formatear_hora(dt):
    return dt.strftime("%H:%M")


st.set_page_config(page_title="Renacer Holístico – Reservá tu turno", page_icon="assets/logo.png", layout="centered")

backends = get_backends(to_dict(st.secrets))

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Poppins:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background-color: #FBF8FC; }
    div.block-container { padding-top: 3.2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #6B4E7D; font-family: 'Cormorant Garamond', serif !important; font-weight: 600; }
    h2 { font-size: 1.4rem; }
    div[data-testid="stImage"] { margin-bottom: -1rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
        padding: 0.6rem 1rem !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem; }
    .terapia-nombre { font-family: 'Cormorant Garamond', serif; font-size: 1.25rem; font-weight: 700; color: #6B4E7D; margin: 0; }
    .terapia-detalle { font-size: 0.8rem; color: #4A3B57; margin: 0; }
    div.stButton > button {
        background-color: #8E6FA1; color: white; border: none; border-radius: 8px;
        padding: 0.3rem 0.9rem;
    }
    div.stButton > button:hover { background-color: #6B4E7D; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1.4, 1, 1.4])
with col2:
    st.image("assets/logo.png", width=150)

if backends.demo_mode:
    st.info("Modo demo: todavía no está conectado a Google Calendar/Sheets reales. Las reservas se guardan localmente para poder probar el flujo.")

if "step" not in st.session_state:
    st.session_state.step = 1


def reiniciar():
    for key in ["step", "terapia_key", "slot_inicio", "slot_fin", "nombre", "telefono", "email"]:
        st.session_state.pop(key, None)
    st.session_state.step = 1


# ---------- Paso 1: elegir terapia ----------
if st.session_state.step == 1:
    st.markdown('<h2>Seleccioná tu terapia</h2>', unsafe_allow_html=True)
    for key, t in TERAPIAS.items():
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f'<p class="terapia-nombre">{t["nombre"]}</p>', unsafe_allow_html=True)
                precio_fmt = f"{t['precio']:,.0f}".replace(",", ".")
                st.markdown(
                    f'<p class="terapia-detalle">Duración: {t["duracion_min"]} min · Precio: ${precio_fmt}</p>',
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button("Reservar", key=f"elegir_{key}"):
                    st.session_state.terapia_key = key
                    st.session_state.step = 2
                    st.rerun()

# ---------- Paso 2: elegir día y horario ----------
elif st.session_state.step == 2:
    terapia_key = st.session_state.terapia_key
    terapia = TERAPIAS[terapia_key]
    st.header(f"Elegí día y horario – {terapia['nombre']}")

    ahora = datetime.now()
    desde = ahora
    hasta = ahora + timedelta(days=HORIZONTE_DIAS + terapia["min_dias"] + 2)
    busy = backends.calendar.get_busy_intervals(desde, hasta)
    slots = generar_turnos_disponibles(terapia_key, ahora, busy)
    agrupados = agrupar_por_dia(slots)

    if not agrupados:
        st.warning("No hay turnos disponibles en este momento. Escribime directamente para coordinar.")
    else:
        opciones_dia = list(agrupados.keys())
        dia_elegido = st.selectbox(
            "Día", opciones_dia, format_func=formatear_fecha,
        )
        horarios_dia = agrupados[dia_elegido]
        opciones_hora = [inicio for inicio, fin in horarios_dia]
        hora_elegida = st.radio(
            "Horario", opciones_hora, format_func=formatear_hora, horizontal=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Volver"):
                st.session_state.step = 1
                st.rerun()
        with col_b:
            if st.button("Continuar", type="primary"):
                fin = hora_elegida + timedelta(minutes=terapia["duracion_min"])
                st.session_state.slot_inicio = hora_elegida.isoformat()
                st.session_state.slot_fin = fin.isoformat()
                st.session_state.step = 3
                st.rerun()

# ---------- Paso 3: datos de contacto ----------
elif st.session_state.step == 3:
    terapia = TERAPIAS[st.session_state.terapia_key]
    st.header("Tus datos de contacto")
    nombre = st.text_input("Nombre y apellido", value=st.session_state.get("nombre", ""))
    telefono = st.text_input("Teléfono (WhatsApp)", value=st.session_state.get("telefono", ""))
    email = st.text_input("Email", value=st.session_state.get("email", ""))

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Volver"):
            st.session_state.step = 2
            st.rerun()
    with col_b:
        if st.button("Continuar", type="primary", disabled=not (nombre and telefono)):
            st.session_state.nombre = nombre
            st.session_state.telefono = telefono
            st.session_state.email = email
            st.session_state.step = 4
            st.rerun()

# ---------- Paso 4: confirmar ----------
elif st.session_state.step == 4:
    terapia_key = st.session_state.terapia_key
    terapia = TERAPIAS[terapia_key]
    inicio = datetime.fromisoformat(st.session_state.slot_inicio)
    fin = datetime.fromisoformat(st.session_state.slot_fin)

    st.header("Confirmá tu reserva")
    st.write(f"**Terapia:** {terapia['nombre']}")
    st.write(f"**Día:** {formatear_fecha(inicio.date())}")
    st.write(f"**Horario:** {formatear_hora(inicio)} a {formatear_hora(fin)}")
    st.write(f"**Nombre:** {st.session_state.nombre}")
    st.write(f"**Precio:** ${terapia['precio']:,.0f}".replace(",", "."))

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Volver"):
            st.session_state.step = 3
            st.rerun()
    with col_b:
        if st.button("Confirmar reserva", type="primary"):
            busy_actual = backends.calendar.get_busy_intervals(inicio - timedelta(minutes=1), fin + timedelta(minutes=1))
            ocupado = any(inicio < b_fin and fin > b_ini for b_ini, b_fin in busy_actual)
            if ocupado:
                st.error("Justo se ocupó ese horario. Volvé a elegir otro turno disponible.")
                st.session_state.step = 2
                st.rerun()
            else:
                descripcion = (
                    f"Terapia: {terapia['nombre']}\n"
                    f"Nombre: {st.session_state.nombre}\n"
                    f"Teléfono: {st.session_state.telefono}\n"
                    f"Email: {st.session_state.email}\n"
                    f"Estado: Pendiente pago"
                )
                event_id = backends.calendar.create_event(
                    summary=f"{terapia['nombre']} – {st.session_state.nombre}",
                    inicio=inicio, fin=fin, description=descripcion,
                )
                sena = terapia["precio"] // 2
                booking_id = backends.storage.add_booking({
                    "tipo": "reserva",
                    "terapia_key": terapia_key,
                    "terapia_nombre": terapia["nombre"],
                    "inicio": inicio.isoformat(),
                    "fin": fin.isoformat(),
                    "nombre": st.session_state.nombre,
                    "telefono": st.session_state.telefono,
                    "email": st.session_state.email,
                    "precio": terapia["precio"],
                    "sena": sena,
                    "estado": "Pendiente pago",
                    "calendar_event_id": event_id,
                    "notas": "",
                    "creado": datetime.now().isoformat(),
                })
                backends.notifier.enviar(
                    NOTIFICACION_EMAIL,
                    f"Nueva reserva: {terapia['nombre']} – {st.session_state.nombre}",
                    f"{descripcion}\n\nDía: {formatear_fecha(inicio.date())}\nHorario: {formatear_hora(inicio)} a {formatear_hora(fin)}\n\nRevisar pago en el panel admin.",
                )
                st.session_state.booking_id = booking_id
                st.session_state.step = 5
                st.rerun()

# ---------- Paso 5: confirmación + pago ----------
elif st.session_state.step == 5:
    terapia = TERAPIAS[st.session_state.terapia_key]
    inicio = datetime.fromisoformat(st.session_state.slot_inicio)
    sena = terapia["precio"] // 2

    st.success("¡Tu turno quedó reservado!")
    st.write(f"**{terapia['nombre']}** – {formatear_fecha(inicio.date())} a las {formatear_hora(inicio)} hs")
    st.write(terapia["mensaje_confirmacion"])
    st.warning(POLITICA_CANCELACION)

    st.subheader("Datos para la seña (50%)")
    st.write(f"**Monto a transferir:** ${sena:,.0f}".replace(",", "."))
    st.write(f"**Alias:** {DATOS_PAGO['alias']}")
    st.write(f"**Banco:** {DATOS_PAGO['banco']}")
    st.caption(DATOS_PAGO["nota_exterior"])

    if st.button("Reservar otro turno"):
        reiniciar()
        st.rerun()
