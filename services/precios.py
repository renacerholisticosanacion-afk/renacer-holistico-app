"""Conversión y formato del equivalente en dólares de un precio en pesos."""


def precio_usd(precio_ars):
    return precio_ars / 1000


def formatear_usd(monto_usd):
    if monto_usd == int(monto_usd):
        return f"US$ {int(monto_usd)}"
    return f"US$ {monto_usd:,.2f}"
