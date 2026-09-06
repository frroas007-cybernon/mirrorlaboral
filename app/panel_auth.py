"""
Autenticacion muy simple para el panel de leads derivados: una contrasena fija
por profesional (Paz / abogada), configurada como variable de entorno, y una
cookie firmada (no una tabla de usuarios ni un flujo de registro/recuperacion
-- decision explicita del usuario, dado que esto lo opera una sola persona).
"""
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.config import SESSION_SECRET, PAZ_PASSWORD, ABOGADA_PASSWORD, PAZ_EMAIL, ABOGADA_EMAIL

COOKIE_NAME = "mirror_panel_session"
MAX_EDAD_SEGUNDOS = 60 * 60 * 12  # 12 horas

PROFESIONALES = {
    "paz": {"password": PAZ_PASSWORD, "nombre": "Paz", "rol": "psicologa", "email": PAZ_EMAIL},
    "abogada": {"password": ABOGADA_PASSWORD, "nombre": "Abogada", "rol": "abogada", "email": ABOGADA_EMAIL},
}

_serializer = URLSafeTimedSerializer(SESSION_SECRET, salt="mirror-panel")


def verificar_password(profesional_id: str, password: str) -> bool:
    datos = PROFESIONALES.get(profesional_id)
    if not datos or not datos["password"]:
        return False
    return password == datos["password"]


def crear_token(profesional_id: str) -> str:
    return _serializer.dumps({"id": profesional_id})


def leer_token(token: str):
    if not token:
        return None
    try:
        data = _serializer.loads(token, max_age=MAX_EDAD_SEGUNDOS)
    except (BadSignature, SignatureExpired):
        return None
    profesional_id = data.get("id")
    if profesional_id not in PROFESIONALES:
        return None
    return profesional_id
