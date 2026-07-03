import streamlit as st
from datetime import datetime, date, time

from config_terapias import TERAPIAS as TERAPIAS_BASE
from services.bootstrap import get_backends
from services.config_loader import cargar_terapias_y_pago
from services.secrets_utils import to_dict

st.set_page_config(page_title="Admin – Renacer Holístico", page_icon="assets/logo.png", layout="wide")

secrets = to_dict(st.secrets)
backends = get_backends(secrets)
CLAVE_ADMIN = secrets.get("admin_password", "demo123")

if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False

if not st.session_state.admin_ok:
    st.title("Panel de administración")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if clave == CLAVE_ADMIN:
            st.session_state.admin_ok = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop()

st.title("Panel de administración")
if backends.demo_mode:
    st.info("Modo demo: datos guardados localmente, todavía no conectado a Google.")

terapias_actuales, datos_pago_actuales = cargar_terapias_y_pago(backends)

st.subheader("Precios de las terapias")
with st.form("precios_form"):
    nuevos_precios = {}
    for key, t in TERAPIAS_BASE.items():
        nuevos_precios[key] = st.number_input(
            t["nombre"], min_value=0, step=1000,
            value=int(terapias_actuales[key]["precio"]),
            key=f"precio_{key}",
        )
    guardar_precios = st.form_submit_button("Guardar precios")

if guardar_precios:
    backends.config.set("precios", nuevos_precios)
    st.success("Precios actualizados.")
    st.rerun()

st.divider()
st.subheader("Datos bancarios")
with st.form("datos_pago_form"):
    alias = st.text_input("Alias", value=datos_pago_actuales["alias"])
    banco = st.text_input("Banco", value=datos_pago_actuales["banco"])
    nota_exterior = st.text_area("Nota para pagos desde el exterior", value=datos_pago_actuales["nota_exterior"])
    guardar_datos_pago = st.form_submit_button("Guardar datos bancarios")

if guardar_datos_pago:
    backends.config.set("datos_pago", {"alias": alias, "banco": banco, "nota_exterior": nota_exterior})
    st.success("Datos bancarios actualizados.")
    st.rerun()

st.divider()
st.subheader("Bloqueo manual de agenda")
with st.form("bloqueo_manual"):
    c1, c2, c3 = st.columns(3)
    with c1:
        fecha = st.date_input("Fecha", value=date.today())
    with c2:
        hora_inicio = st.time_input("Hora inicio", value=time(9, 0))
    with c3:
        hora_fin = st.time_input("Hora fin", value=time(10, 0))
    motivo = st.text_input("Motivo (opcional, no lo ven los consultantes)")
    enviar = st.form_submit_button("Bloquear este horario")

if enviar:
    inicio = datetime.combine(fecha, hora_inicio)
    fin = datetime.combine(fecha, hora_fin)
    if fin <= inicio:
        st.error("La hora de fin debe ser posterior a la hora de inicio.")
    else:
        event_id = backends.calendar.create_event(
            summary="Bloqueo de agenda",
            inicio=inicio, fin=fin,
            description=motivo or "Bloqueo manual",
        )
        backends.storage.add_booking({
            "tipo": "bloqueo_manual",
            "terapia_key": "",
            "terapia_nombre": "Bloqueo manual",
            "inicio": inicio.isoformat(),
            "fin": fin.isoformat(),
            "nombre": "",
            "telefono": "",
            "email": "",
            "precio": 0,
            "sena": 0,
            "estado": "Bloqueado",
            "calendar_event_id": event_id,
            "notas": motivo,
            "creado": datetime.now().isoformat(),
        })
        st.success("Horario bloqueado.")
        st.rerun()

st.divider()
st.subheader("Turnos y bloqueos")

bookings = backends.storage.list_bookings()
bookings = sorted(bookings, key=lambda b: b.get("inicio", ""))

filtro = st.selectbox("Filtrar por estado", ["Todos", "Pendiente pago", "Pagado", "Cancelado", "Bloqueado"])
if filtro != "Todos":
    bookings = [b for b in bookings if b.get("estado") == filtro]

if not bookings:
    st.write("No hay registros para este filtro.")

for b in bookings:
    with st.container(border=True):
        inicio = datetime.fromisoformat(b["inicio"])
        fin = datetime.fromisoformat(b["fin"])
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write(f"**{b['terapia_nombre']}** – {inicio.strftime('%d/%m/%Y %H:%M')} a {fin.strftime('%H:%M')}")
            if b.get("nombre"):
                st.write(f"{b['nombre']} · {b.get('telefono', '')} · {b.get('email', '')}")
            if b.get("precio"):
                st.write(f"Precio: ${int(b['precio']):,.0f} · Seña: ${int(b['sena']):,.0f}".replace(",", "."))
            if b.get("notas"):
                st.caption(b["notas"])
            st.write(f"Estado: **{b['estado']}**")
        with col2:
            if b["estado"] == "Pendiente pago":
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("Marcar pagado", key=f"pagar_{b['id']}"):
                        backends.storage.update_booking(b["id"], {"estado": "Pagado"})
                        st.rerun()
                with cc2:
                    if st.button("Liberar turno", key=f"liberar_{b['id']}"):
                        backends.calendar.delete_event(b["calendar_event_id"])
                        backends.storage.update_booking(b["id"], {"estado": "Cancelado"})
                        st.rerun()
            elif b["estado"] == "Pagado":
                if st.button("Cancelar turno", key=f"cancelar_{b['id']}"):
                    backends.calendar.delete_event(b["calendar_event_id"])
                    backends.storage.update_booking(b["id"], {"estado": "Cancelado"})
                    st.rerun()
            elif b["estado"] == "Bloqueado":
                if st.button("Liberar bloqueo", key=f"desbloquear_{b['id']}"):
                    backends.calendar.delete_event(b["calendar_event_id"])
                    backends.storage.update_booking(b["id"], {"estado": "Cancelado"})
                    st.rerun()
