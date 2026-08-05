from datetime import datetime

import streamlit as st

from config_terapias import NOTIFICACION_EMAIL
from services.bootstrap import get_backends
from services.config_loader import cargar_terapias_y_pago, cargar_productos, guardar_productos
from services.secrets_utils import to_dict

backends = get_backends(to_dict(st.secrets))
_, DATOS_PAGO = cargar_terapias_y_pago(backends)

if backends.demo_mode:
    st.info("Modo demo: todavía no está conectado a Google Calendar/Sheets reales. Los pedidos se guardan localmente para poder probar el flujo.")

if "pedido_step" not in st.session_state:
    st.session_state.pedido_step = 1


def reiniciar_pedido():
    for key in ["pedido_step", "pedido_producto_key", "pedido_cantidad", "pedido_nombre", "pedido_telefono", "pedido_email", "pedido_id"]:
        st.session_state.pop(key, None)
    st.session_state.pedido_step = 1


def descontar_stock(producto_key, cantidad):
    catalogo_actual = cargar_productos(backends)
    catalogo_actual[producto_key]["stock"] -= cantidad
    guardar_productos(backends, catalogo_actual)


# ---------- Paso 1: elegir producto ----------
if st.session_state.pedido_step == 1:
    st.markdown('<h2>Productos</h2>', unsafe_allow_html=True)
    productos = cargar_productos(backends)
    for key, p in productos.items():
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f'<p class="terapia-nombre">{p["nombre"]}</p>', unsafe_allow_html=True)
                detalle = []
                if p.get("plantas"):
                    detalle.append(f"<b>Plantas:</b> {p['plantas']}")
                if p.get("uso"):
                    detalle.append(p["uso"])
                if p.get("ideal_para"):
                    detalle.append(f"👉 Ideal para {p['ideal_para']}.")
                precio_fmt = f"{p['precio']:,.0f}".replace(",", ".")
                detalle.append(f"Precio: ${precio_fmt} · Stock: {p['stock']}")
                st.markdown(
                    f'<p class="terapia-detalle">{"<br>".join(detalle)}</p>',
                    unsafe_allow_html=True,
                )
            with c2:
                if p["stock"] > 0:
                    if st.button("Elegir", key=f"elegir_prod_{key}"):
                        st.session_state.pedido_producto_key = key
                        st.session_state.pedido_step = 2
                        st.rerun()
                else:
                    st.caption("Sin stock")

# ---------- Paso 2: cantidad ----------
elif st.session_state.pedido_step == 2:
    productos = cargar_productos(backends)
    producto_key = st.session_state.pedido_producto_key
    producto = productos[producto_key]
    st.header(f"Cantidad – {producto['nombre']}")

    cantidad = st.number_input("Cantidad", min_value=1, max_value=producto["stock"], value=1, step=1)
    total = producto["precio"] * cantidad
    st.write(f"**Total:** ${total:,.0f}".replace(",", "."))

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Volver", key="volver_prod_2"):
            st.session_state.pedido_step = 1
            st.rerun()
    with col_b:
        if st.button("Continuar", type="primary", key="continuar_prod_2"):
            st.session_state.pedido_cantidad = cantidad
            st.session_state.pedido_step = 3
            st.rerun()

# ---------- Paso 3: datos de contacto ----------
elif st.session_state.pedido_step == 3:
    st.header("Tus datos de contacto")
    nombre = st.text_input("Nombre y apellido", value=st.session_state.get("pedido_nombre", ""), key="nombre_prod")
    telefono = st.text_input("Teléfono (WhatsApp)", value=st.session_state.get("pedido_telefono", ""), key="telefono_prod")
    email = st.text_input("Email", value=st.session_state.get("pedido_email", ""), key="email_prod")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Volver", key="volver_prod_3"):
            st.session_state.pedido_step = 2
            st.rerun()
    with col_b:
        if st.button("Continuar", type="primary", disabled=not (nombre and telefono), key="continuar_prod_3"):
            st.session_state.pedido_nombre = nombre
            st.session_state.pedido_telefono = telefono
            st.session_state.pedido_email = email
            st.session_state.pedido_step = 4
            st.rerun()

# ---------- Paso 4: confirmar ----------
elif st.session_state.pedido_step == 4:
    productos = cargar_productos(backends)
    producto_key = st.session_state.pedido_producto_key
    producto = productos[producto_key]
    cantidad = st.session_state.pedido_cantidad
    total = producto["precio"] * cantidad

    st.header("Confirmá tu pedido")
    st.write(f"**Producto:** {producto['nombre']}")
    st.write(f"**Cantidad:** {cantidad}")
    st.write(f"**Nombre:** {st.session_state.pedido_nombre}")
    st.write(f"**Total:** ${total:,.0f}".replace(",", "."))

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Volver", key="volver_prod_4"):
            st.session_state.pedido_step = 3
            st.rerun()
    with col_b:
        if st.button("Confirmar pedido", type="primary", key="confirmar_prod_4"):
            productos_actuales = cargar_productos(backends)
            stock_actual = productos_actuales[producto_key]["stock"]
            if stock_actual < cantidad:
                st.error("Justo se agotó el stock disponible. Volvé a elegir la cantidad.")
                st.session_state.pedido_step = 2
                st.rerun()
            else:
                descontar_stock(producto_key, cantidad)
                pedido_id = backends.orders.add_order({
                    "tipo": "pedido",
                    "producto_key": producto_key,
                    "producto_nombre": producto["nombre"],
                    "cantidad": cantidad,
                    "precio_unitario": producto["precio"],
                    "precio_total": total,
                    "nombre": st.session_state.pedido_nombre,
                    "telefono": st.session_state.pedido_telefono,
                    "email": st.session_state.pedido_email,
                    "estado": "Pendiente pago",
                    "notas": "",
                    "creado": datetime.now().isoformat(),
                })
                backends.notifier.enviar(
                    NOTIFICACION_EMAIL,
                    f"Nuevo pedido: {producto['nombre']} x{cantidad} – {st.session_state.pedido_nombre}",
                    (
                        f"Producto: {producto['nombre']}\n"
                        f"Cantidad: {cantidad}\n"
                        f"Total: ${total:,.0f}\n"
                        f"Nombre: {st.session_state.pedido_nombre}\n"
                        f"Teléfono: {st.session_state.pedido_telefono}\n"
                        f"Email: {st.session_state.pedido_email}\n"
                        f"Estado: Pendiente pago\n\n"
                        f"Revisar pago en el panel admin."
                    ),
                )
                st.session_state.pedido_id = pedido_id
                st.session_state.pedido_step = 5
                st.rerun()

# ---------- Paso 5: confirmación + pago ----------
elif st.session_state.pedido_step == 5:
    productos = cargar_productos(backends)
    producto_key = st.session_state.get("pedido_producto_key")
    cantidad = st.session_state.get("pedido_cantidad", 1)
    producto = productos.get(producto_key)
    total = producto["precio"] * cantidad if producto else None

    st.success("¡Tu pedido quedó registrado!")
    st.write("Vamos a coordinar la entrega por WhatsApp una vez confirmado el pago.")

    st.subheader("Datos para la transferencia (100%)")
    if total is not None:
        st.write(f"**Monto a transferir:** ${total:,.0f}".replace(",", "."))
    st.write(f"**Alias:** {DATOS_PAGO['alias']}")
    st.write(f"**Banco:** {DATOS_PAGO['banco']}")
    st.caption(DATOS_PAGO["nota_exterior"])

    if st.button("Comprar otro producto"):
        reiniciar_pedido()
        st.rerun()
