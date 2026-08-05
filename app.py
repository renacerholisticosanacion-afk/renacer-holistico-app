import base64

import streamlit as st

st.set_page_config(
    page_title="Renacer Holístico",
    page_icon="assets/logo.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def _logo_base64():
    with open("assets/logo.png", "rb") as f:
        return base64.b64encode(f.read()).decode()


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Poppins:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background-color: #FBF8FC; }
    div.block-container { padding-top: 3.2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #6B4E7D; font-family: 'Cormorant Garamond', serif !important; font-weight: 600; }
    h2 { font-size: 1.25rem !important; }
    .logo-renacer { display: block; margin: 0 auto -1rem auto; width: 150px; height: auto; }
    div[data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
        padding: 0.45rem 0.8rem !important;
    }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem; }
    .terapia-nombre { font-family: 'Cormorant Garamond', serif; font-size: 1.4rem !important; font-weight: 700; color: #6B4E7D; margin: 0; }
    .terapia-detalle { font-size: 0.7rem !important; color: #4A3B57; margin: 0; }
    div.stButton > button {
        background-color: #8E6FA1; color: white; border: none; border-radius: 5px;
        padding: 0.3rem 1.1rem;
    }
    div.stButton > button:hover { background-color: #6B4E7D; color: white; }
    .aviso-lila {
        background-color: #F0E6F6;
        border-left: 4px solid #8E6FA1;
        color: #4A3B57;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.8rem;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<img class="logo-renacer" src="data:image/png;base64,{_logo_base64()}">',
    unsafe_allow_html=True,
)

pages = [
    st.Page("pages/home.py", title="Inicio", icon="🏠", default=True),
    st.Page("pages/turnos.py", title="Turnos", icon="🗓️"),
    st.Page("pages/productos.py", title="Productos", icon="🛍️"),
    st.Page("pages/admin.py", title="Admin", url_path="admin", visibility="hidden"),
]

st.navigation(pages, position="top").run()
