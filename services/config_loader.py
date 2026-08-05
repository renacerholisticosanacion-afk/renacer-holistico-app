"""Combina la configuración estática de terapias (config_terapias.py) con los overrides
editables desde el panel admin, y expone el catálogo de productos administrado
íntegramente desde el admin (ver config_productos.py para la semilla inicial)."""
from config_terapias import TERAPIAS, DATOS_PAGO
from config_productos import PRODUCTOS_SEED

CATALOGO_PRODUCTOS_KEY = "catalogo_productos"


def cargar_terapias_y_pago(backends):
    overrides = backends.config.get_all()

    terapias = {key: dict(t) for key, t in TERAPIAS.items()}
    for key, precio in overrides.get("precios", {}).items():
        if key in terapias:
            terapias[key]["precio"] = precio

    datos_pago = dict(DATOS_PAGO)
    datos_pago.update(overrides.get("datos_pago", {}))

    return terapias, datos_pago


def cargar_productos(backends):
    catalogo = backends.config.get_all().get(CATALOGO_PRODUCTOS_KEY)
    if catalogo is None:
        catalogo = {key: dict(p) for key, p in PRODUCTOS_SEED.items()}
        backends.config.set(CATALOGO_PRODUCTOS_KEY, catalogo)
    return catalogo


def guardar_productos(backends, catalogo):
    backends.config.set(CATALOGO_PRODUCTOS_KEY, catalogo)
