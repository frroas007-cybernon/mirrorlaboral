import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, LargeBinary

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

    nombre = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
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


class Mirror2Response(Base):
    """
    Una respuesta completa del Mirror 2 (pago). Guarda el tier comprado, el
    estado del pago en Mercado Pago, todas las respuestas de los bloques
    psicológico y legal (según lo definido en Mirror2_Preguntas_Detalladas.md),
    y los documentos ya generados (en binario, porque el hosting serverless no
    tiene disco persistente entre invocaciones).
    """
    __tablename__ = "mirror2_responses"

    id = Column(String, primary_key=True, default=_uuid)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)

    tier = Column(String, nullable=False)  # dt / psico / legal / completo
    precio = Column(Integer, nullable=False)

    # Estado de pago (Mercado Pago)
    payment_status = Column(String, nullable=False, default="pending")  # pending/approved/rejected
    preference_id = Column(String, nullable=True)
    payment_id = Column(String, nullable=True)
    documentos_generados = Column(Boolean, default=False, nullable=False)
    documentos_enviados = Column(Boolean, default=False, nullable=False)

    # --- Protocolo de riesgo (R.1 / R.2) ---
    riesgo_screening = Column(String, nullable=True)
    riesgo_flag = Column(Boolean, default=False, nullable=False)
    contacto_confianza = Column(String, nullable=True)

    # --- Bloque psicológico ---
    trato_1 = Column(String, nullable=True)
    trato_2 = Column(String, nullable=True)
    trato_3 = Column(String, nullable=True)
    presion_1 = Column(String, nullable=True)
    presion_2 = Column(String, nullable=True)
    presion_3 = Column(String, nullable=True)
    aislamiento_1 = Column(String, nullable=True)
    aislamiento_2 = Column(String, nullable=True)
    aislamiento_3 = Column(String, nullable=True)
    amenazas_1 = Column(String, nullable=True)
    amenazas_2 = Column(String, nullable=True)
    amenazas_3 = Column(String, nullable=True)
    impacto_1 = Column(String, nullable=True)
    impacto_2 = Column(String, nullable=True)
    impacto_3 = Column(String, nullable=True)

    impacto_inv_1 = Column(String, nullable=True)
    impacto_inv_2 = Column(String, nullable=True)
    impacto_inv_3 = Column(String, nullable=True)
    impacto_inv_4 = Column(String, nullable=True)

    red_apoyo = Column(String, nullable=True)
    ayuda_psicologica_previa = Column(String, nullable=True)

    motivo_consulta = Column(Text, nullable=True)
    situacion_actual = Column(String, nullable=True)
    en_tratamiento = Column(String, nullable=True)
    otras_areas_afectadas = Column(String, nullable=True)
    estrategias_afrontamiento = Column(String, nullable=True)  # opciones unidas con "; "
    open_text = Column(Text, nullable=True)

    # --- Bloque legal ---
    cargo = Column(String, nullable=True)
    antiguedad = Column(String, nullable=True)
    tipo_contrato = Column(String, nullable=True)
    persona_senalada = Column(String, nullable=True)
    relacion = Column(String, nullable=True)
    empresa_nombre = Column(String, nullable=True)
    empresa_rut = Column(String, nullable=True)
    inicio = Column(String, nullable=True)
    relato_libre = Column(Text, nullable=True)
    evidencia_lista = Column(String, nullable=True)  # opciones unidas con "; "
    testigo_activo = Column(String, nullable=True)
    gestion_previa = Column(String, nullable=True)
    gestion_previa_hace_cuanto = Column(String, nullable=True)
    intencion = Column(String, nullable=True)
    protocolo_vigente = Column(String, nullable=True)
    fuero = Column(String, nullable=True)  # opciones unidas con "; "
    remuneracion = Column(String, nullable=True)
    firmo_finiquito = Column(String, nullable=True)

    # --- Documentos generados (bytes .docx) ---
    doc_completo = Column(LargeBinary, nullable=True)
    doc_psicologico = Column(LargeBinary, nullable=True)
    doc_legal = Column(LargeBinary, nullable=True)
    doc_dt = Column(LargeBinary, nullable=True)

    # --- Anexo de derivación (opt-in, nunca marcado por defecto) ---
    deriva_paz = Column(Boolean, default=False, nullable=False)
    deriva_abogada = Column(Boolean, default=False, nullable=False)
    estado_paz = Column(String, nullable=True)      # "nuevo" / "contactado" -- solo si deriva_paz
    estado_abogada = Column(String, nullable=True)  # "nuevo" / "contactado" -- solo si deriva_abogada
