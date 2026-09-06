import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Si no hay DATABASE_URL (Supabase) configurada, usamos SQLite local para poder
# probar el flujo completo sin depender todavía de Supabase.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./local_dev.db")

SALUD_RESPONDE_TELEFONO = "600 360 7777"

# URL pública del sitio (para construir back_urls / notification_url de Mercado Pago).
# En local queda apuntando a localhost; en Vercel se define como variable de entorno
# con el dominio real (ej. https://mirrorlaboral.cl o la URL de Vercel).
SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:8000")

# Mercado Pago (Checkout Pro). Se piden al usuario cuando corresponde -- nunca se
# asumen ni se escriben en el código.
MERCADOPAGO_ACCESS_TOKEN = os.environ.get("MERCADOPAGO_ACCESS_TOKEN", "")
MERCADOPAGO_PUBLIC_KEY = os.environ.get("MERCADOPAGO_PUBLIC_KEY", "")

# Gmail SMTP para correo transaccional.
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

# Correo interno para alertas de riesgo (protocolo de riesgo, Sistema_Mirror_3_Niveles.md).
# Si no se define, se usa GMAIL_USER como destino por defecto.
INTERNAL_ALERT_EMAIL = os.environ.get("INTERNAL_ALERT_EMAIL", "")

# Panel de leads derivados: contraseña simple por profesional (elección del usuario).
PAZ_PASSWORD = os.environ.get("PAZ_PASSWORD", "")
ABOGADA_PASSWORD = os.environ.get("ABOGADA_PASSWORD", "")

# Correo de cada profesional, solo para la notificación de "nuevo caso disponible"
# (el aviso nunca lleva contenido sensible -- el detalle se revisa dentro del panel).
PAZ_EMAIL = os.environ.get("PAZ_EMAIL", "")
ABOGADA_EMAIL = os.environ.get("ABOGADA_EMAIL", "")

# Firma de las cookies de sesión del panel. En producción SIEMPRE debe configurarse
# como variable de entorno propia (valor largo y aleatorio).
SESSION_SECRET = os.environ.get("SESSION_SECRET", "cambia-esto-en-produccion-mirror-laboral")

# Si es True, permite avanzar el flujo de pago sin llamar a Mercado Pago de verdad
# (solo cuando no hay Access Token configurado) -- útil para probar el formulario
# completo de Mirror 2 en desarrollo local antes de tener las credenciales reales.
MODO_PAGO_SIMULADO = not MERCADOPAGO_ACCESS_TOKEN
