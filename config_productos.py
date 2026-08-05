"""Catálogo inicial (semilla) de productos.

A partir del primer arranque, el catálogo real se administra íntegramente
desde el panel admin (agregar, editar y eliminar tinturas) y se guarda a
través del backend de configuración — este archivo solo aporta los datos
de partida la primera vez que se corre la app.
"""
import re
import unicodedata

PRODUCTOS_SEED = {
    "sueno_reparador": {
        "nombre": "💤 Sueño reparador",
        "plantas": "Valeriana + Pasiflora + Melisa",
        "uso": "Ayuda a conciliar el sueño, relaja el sistema nervioso y calma la mente.",
        "ideal_para": "personas con insomnio o ansiedad nocturna",
        "precio": 10000,
        "stock": 5,
    },
}


def _slugify(nombre):
    texto = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto).strip("_").lower()
    return texto or "producto"


def generar_key(catalogo, nombre):
    """Genera una clave única para un producto nuevo a partir de su nombre."""
    base = _slugify(nombre)
    key = base
    i = 2
    while key in catalogo:
        key = f"{base}_{i}"
        i += 1
    return key
