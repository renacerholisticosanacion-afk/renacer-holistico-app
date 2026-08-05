import os

import streamlit as st

IMAGEN_SOBRE_MI = "assets/sobre_mi.jpg"


def _imagen_sobre_mi():
    if os.path.exists(IMAGEN_SOBRE_MI):
        st.image(IMAGEN_SOBRE_MI, use_container_width=True)
    else:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #E9DFF0, #D9C7E8);
                border-radius: 12px;
                height: 260px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #6B4E7D;
                font-family: 'Cormorant Garamond', serif;
                font-size: 1.1rem;
                text-align: center;
                padding: 1rem;
            ">
                Tu foto va acá<br>(guardá el archivo como assets/sobre_mi.jpg)
            </div>
            """,
            unsafe_allow_html=True,
        )


st.markdown('<h2>Sobre mí</h2>', unsafe_allow_html=True)

_imagen_sobre_mi()

st.write(
    """
    ¡Hola! Soy Antonella, y creé Renacer Holístico como un espacio de acompañamiento
    para quienes están atravesando un proceso de sanación y autoconocimiento.

    Trabajo con distintas herramientas —biodescodificación, reiki, radiestesia, tarot
    evolutivo y numerología, entre otras— para ayudarte a identificar bloqueos
    emocionales, entender sus raíces y encontrar un camino más liviano hacia
    adelante.

    Cada terapia se adapta a lo que estés atravesando en este momento de tu vida.
    Si tenés dudas sobre cuál elegir, escribime y lo vemos juntas.
    """
)

st.info("Este texto es un borrador — editá pages/home.py con tu presentación definitiva cuando quieras.")
