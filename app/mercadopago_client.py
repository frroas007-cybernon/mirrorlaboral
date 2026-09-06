"""
Integracion minima con Mercado Pago (Checkout Pro) via REST, sin el SDK
oficial para mantener las dependencias simples. Usa el Access Token que el
usuario configura como variable de entorno (nunca hardcodeado, nunca
tipeado en un formulario web por Claude).
"""
import requests

from app.config import MERCADOPAGO_ACCESS_TOKEN, SITE_URL

TIER_PRECIOS = {"dt": 15000, "psico": 20000, "legal": 20000, "completo": 25000}

TIER_TITULOS = {
    "dt": "Mirror Laboral — Listo para la DT",
    "psico": "Mirror Laboral — Discovery Psicológico",
    "legal": "Mirror Laboral — Discovery Legal",
    "completo": "Mirror Laboral — Informe Completo",
}


class MercadoPagoNoConfigurado(Exception):
    pass


def crear_preferencia(response_id: str, tier: str, email: str) -> dict:
    if not MERCADOPAGO_ACCESS_TOKEN:
        raise MercadoPagoNoConfigurado(
            "Falta MERCADOPAGO_ACCESS_TOKEN — configúralo como variable de entorno en Vercel."
        )
    precio = TIER_PRECIOS[tier]
    payload = {
        "items": [
            {
                "title": TIER_TITULOS[tier],
                "quantity": 1,
                "currency_id": "CLP",
                "unit_price": precio,
            }
        ],
        "payer": {"email": email},
        "external_reference": response_id,
        "back_urls": {
            "success": f"{SITE_URL}/mirror2/gracias/{response_id}",
            "pending": f"{SITE_URL}/mirror2/gracias/{response_id}",
            "failure": f"{SITE_URL}/mirror2/pago-fallido/{response_id}",
        },
        "auto_return": "approved",
        "notification_url": f"{SITE_URL}/mirror2/webhook",
    }
    r = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        json=payload,
        headers={"Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def obtener_pago(payment_id: str) -> dict:
    r = requests.get(
        f"https://api.mercadopago.com/v1/payments/{payment_id}",
        headers={"Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()
