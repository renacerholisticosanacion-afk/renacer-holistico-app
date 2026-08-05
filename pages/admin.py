import streamlit as st
from datetime import datetime, date, time

from config_terapias import TERAPIAS as TERAPIAS_BASE
from config_productos import generar_key
from services.bootstrap import get_backends
from services.config_loader import cargar_terapias_y_pago, cargar_productos, guardar_productos
from services.secrets_utils import to_dict

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
    for key, t in sorted(TERAPIAS_BASE.items(), key=lambda kv: kv[1]["nombre"]):
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
st.subheader("Productos (tinturas)")

catalogo_productos = cargar_productos(backends)

with st.expander("Agregar producto nuevo"):
    with st.form("nuevo_producto_form", clear_on_submit=True):
        nombre_nuevo = st.text_input("Nombre (podés incluir un emoji, ej: 💤 Sueño reparador)")
        plantas_nuevo = st.text_input("Plantas (ej: Valeriana + Pasiflora + Melisa)")
        uso_nuevo = st.text_area("Uso / para qué sirve")
        ideal_para_nuevo = st.text_input("Ideal para (opcional)")
        precio_nuevo = st.number_input("Precio", min_value=0, step=1000, key="precio_nuevo_prod")
        stock_nuevo = st.number_input("Stock inicial", min_value=0, step=1, key="stock_nuevo_prod")
        crear_producto = st.form_submit_button("Agregar producto")

    if crear_producto:
        if not nombre_nuevo:
            st.error("Ingresá un nombre para el producto.")
        else:
            nueva_key = generar_key(catalogo_productos, nombre_nuevo)
            catalogo_productos[nueva_key] = {
                "nombre": nombre_nuevo,
                "plantas": plantas_nuevo,
                "uso": uso_nuevo,
                "ideal_para": ideal_para_nuevo,
                "precio": precio_nuevo,
                "stock": stock_nuevo,
            }
            guardar_productos(backends, catalogo_productos)
            st.success(f"'{nombre_nuevo}' agregado al catálogo.")
            st.rerun()

for key, p in catalogo_productos.items():
    with st.expander(p["nombre"]):
        with st.form(f"editar_producto_{key}"):
            nombre_ed = st.text_input("Nombre", value=p["nombre"], key=f"nombre_ed_{key}")
            plantas_ed = st.text_input("Plantas", value=p.get("plantas", ""), key=f"plantas_ed_{key}")
            uso_ed = st.text_area("Uso / para qué sirve", value=p.get("uso", ""), key=f"uso_ed_{key}")
            ideal_para_ed = st.text_input("Ideal para", value=p.get("ideal_para", ""), key=f"ideal_ed_{key}")
            precio_ed = st.number_input("Precio", min_value=0, step=1000, value=int(p["precio"]), key=f"precio_ed_{key}")
            stock_ed = st.number_input("Stock", min_value=0, step=1, value=int(p["stock"]), key=f"stock_ed_{key}")
            col_a, col_b = st.columns(2)
            with col_a:
                guardar_producto = st.form_submit_button("Guardar cambios")
            with col_b:
                eliminar_producto = st.form_submit_button("Eliminar producto")

        if guardar_producto:
            catalogo_productos[key] = {
                "nombre": nombre_ed, "plantas": plantas_ed, "uso": uso_ed,
                "ideal_para": ideal_para_ed, "precio": precio_ed, "stock": stock_ed,
            }
            guardar_productos(backends, catalogo_productos)
            st.success("Producto actualizado.")
            st.rerun()

        if eliminar_producto:
            del catalogo_productos[key]
            guardar_productos(backends, catalogo_productos)
            st.success("Producto eliminado.")
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

filtro = st.selectbox("Filtrar por estado", ["Todos", "Pendiente pago", "Pagado", "Cancelado", "Bloqueado"], key="filtro_turnos")
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

st.divider()
st.subheader("Pedidos")

orders = backends.orders.list_orders()
orders = sorted(orders, key=lambda o: o.get("creado", ""))

filtro_pedidos = st.selectbox("Filtrar por estado", ["Todos", "Pendiente pago", "Pagado", "Cancelado"], key="filtro_pedidos")
if filtro_pedidos != "Todos":
    orders = [o for o in orders if o.get("estado") == filtro_pedidos]

if not orders:
    st.write("No hay pedidos para este filtro.")


def _restaurar_stock(producto_key, cantidad):
    catalogo_actual = cargar_productos(backends)
    if producto_key not in catalogo_actual:
        return
    catalogo_actual[producto_key]["stock"] += cantidad
    guardar_productos(backends, catalogo_actual)


for o in orders:
    with st.container(border=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write(f"**{o['producto_nombre']}** x{o['cantidad']}")
            if o.get("nombre"):
                st.write(f"{o['nombre']} · {o.get('telefono', '')} · {o.get('email', '')}")
            if o.get("precio_total"):
                st.write(f"Total: ${int(o['precio_total']):,.0f}".replace(",", "."))
            if o.get("notas"):
                st.caption(o["notas"])
            st.write(f"Estado: **{o['estado']}**")
        with col2:
            if o["estado"] == "Pendiente pago":
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("Marcar pagado", key=f"pagar_pedido_{o['id']}"):
                        backends.orders.update_order(o["id"], {"estado": "Pagado"})
                        st.rerun()
                with cc2:
                    if st.button("Cancelar pedido", key=f"cancelar_pedido_{o['id']}"):
                        backends.orders.update_order(o["id"], {"estado": "Cancelado"})
                        _restaurar_stock(o["producto_key"], int(o["cantidad"]))
                        st.rerun()
            elif o["estado"] == "Pagado":
                if st.button("Cancelar pedido", key=f"cancelar_pedido_{o['id']}"):
                    backends.orders.update_order(o["id"], {"estado": "Cancelado"})
                    _restaurar_stock(o["producto_key"], int(o["cantidad"]))
                    st.rerun()
