"""Combina la configuración estática (config_terapias.py) con los overrides editables desde el panel admin."""
from config_terapias import TERAPIAS, DATOS_PAGO


def cargar_terapias_y_pago(backends):
    overrides = backends.config.get_all()

    terapias = {key: dict(t) for key, t in TERAPIAS.items()}
    for key, precio in overrides.get("precios", {}).items():
        if key in terapias:
            terapias[key]["precio"] = precio

    datos_pago = dict(DATOS_PAGO)
    datos_pago.update(overrides.get("datos_pago", {}))

    return terapias, datos_pago
