import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Boolean, DateTime

from app.db import Base


def _uuid():
    return str(uuid.uuid4())


class Mirror1Response(Base):
    """
    Una respuesta completa del Mirror 1 (gratuito).
    Guarda las 5 dimensiones puntuables, la pregunta de contexto, el screening
    de riesgo, el correo, y el resultado ya calculado (para no tener que
    recalcularlo si se audita después).
    """
    __tablename__ = "mirror1_responses"

    id = Column(String, primary_key=True, default=_uuid)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    email = Column(String, nullable=False, index=True)

    # Screening de riesgo (R.1) -- "No" / "A veces lo he pensado" / "Sí, con frecuencia"
    riesgo_respuesta = Column(String, nullable=False)
    riesgo_flag = Column(Boolean, default=False, nullable=False)

    # Las 5 dimensiones puntuables, 0-3 cada una
    trato = Column(Integer, nullable=False)
    presion = Column(Integer, nullable=False)
    aislamiento = Column(Integer, nullable=False)
    amenazas = Column(Integer, nullable=False)
    impacto = Column(Integer, nullable=False)

    # Pregunta de contexto (no puntúa)
    contexto_tiempo = Column(String, nullable=False)

    # Resultado ya calculado
    patron_principal = Column(String, nullable=True)  # None si "sin patrón marcado"
    patron_secundario = Column(String, nullable=True)
