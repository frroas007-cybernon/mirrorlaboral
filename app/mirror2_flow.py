"""
Orquestacion del flujo de negocio del Mirror 2: arma los diccionarios que
esperan scoring.py / generar_documentos_v3.py a partir de la fila guardada
en base de datos, genera los documentos que correspondan al tier comprado,
los guarda en la fila y envia el correo con los adjuntos. Se llama tanto
desde el webhook de Mercado Pago como desde la pagina de "gracias" (como
respaldo, por si el webhook todavia no llega) y desde el modo de pago
simulado (cuando no hay credenciales de Mercado Pago configuradas).
"""
from app.mirror2_engine.service import generar_documentos, NOMBRE_ARCHIVO
from app.mailer import enviar_correo
from app.models import Mirror2Response


def construir_answers_y_legal(m: Mirror2Response):
    answers = {
        "nombre": m.nombre,
        "open": m.open_text or "",
        "riesgo_screening": m.riesgo_screening or "No recopilado",
        "contacto_confianza": m.contacto_confianza or "No recopilado",
        "situacion_actual": m.situacion_actual,
        "en_tratamiento": m.en_tratamiento,
        "motivo_consulta": m.motivo_consulta or "No recopilado en este envío.",
        "estrategias_afrontamiento": m.estrategias_afrontamiento,
        "red_apoyo": m.red_apoyo,
        "trato_1": m.trato_1, "trato_2": m.trato_2, "trato_3": m.trato_3,
        "presion_1": m.presion_1, "presion_2": m.presion_2, "presion_3": m.presion_3,
        "aislamiento_1": m.aislamiento_1, "aislamiento_2": m.aislamiento_2, "aislamiento_3": m.aislamiento_3,
        "amenazas_1": m.amenazas_1, "amenazas_2": m.amenazas_2, "amenazas_3": m.amenazas_3,
        "impacto_1": m.impacto_1, "impacto_2": m.impacto_2, "impacto_3": m.impacto_3,
    }
    legal = {
        "cargo": m.cargo,
        "antiguedad": m.antiguedad,
        "tipo_contrato": m.tipo_contrato,
        "persona_señalada": m.persona_senalada,
        "relacion": m.relacion,
        "empresa": m.empresa_nombre,
        "rut_empresa": m.empresa_rut,
        "inicio": m.inicio,
        "relato_libre": m.relato_libre,
        "evidencia_lista": (m.evidencia_lista or "").split("; ") if m.evidencia_lista else [],
        "testigo_activo": m.testigo_activo,
        "gestion_previa": m.gestion_previa,
        "intencion": m.intencion,
        "protocolo_vigente": m.protocolo_vigente,
        "fuero": m.fuero,
        "remuneracion": m.remuneracion,
        "firmo_finiquito": m.firmo_finiquito,
    }
    return answers, legal


ASUNTOS = {
    "completo": "Tu Mirror completo ya está listo",
    "psicologico": "Tu Discovery Psicológico ya está listo",
    "legal": "Tu Discovery Legal ya está listo",
    "dt": "Tu Anexo listo para la DT ya está listo",
}


def procesar_pago_confirmado(db, m: Mirror2Response) -> None:
    """Genera los documentos del tier comprado, los guarda en la fila y envía
    el correo con los adjuntos. Idempotente: si ya se generaron, no hace nada."""
    if m.documentos_generados:
        return

    answers, legal = construir_answers_y_legal(m)
    documentos = generar_documentos(m.tier, answers, legal)

    if "completo" in documentos:
        m.doc_completo = documentos["completo"]
    if "psicologico" in documentos:
        m.doc_psicologico = documentos["psicologico"]
    if "legal" in documentos:
        m.doc_legal = documentos["legal"]
    if "dt" in documentos:
        m.doc_dt = documentos["dt"]

    m.documentos_generados = True
    db.add(m)
    db.commit()

    adjuntos = [(NOMBRE_ARCHIVO[clave], contenido) for clave, contenido in documentos.items()]
    clave_principal = "completo" if "completo" in documentos else next(iter(documentos))
    cuerpo = f"""
    <p>Hola, {m.nombre}.</p>
    <p>Adjunto encontrarás tu Mirror. Esto lo revisó y armó nuestro equipo -- si algo no te
    hace sentido, escríbenos a mirrorlaboral@gmail.com.</p>
    <p style="color:#6b6259;font-size:13px;">Este documento organiza tu autoreporte y ofrece una
    primera lectura orientadora. No reemplaza una evaluación profesional ni constituye
    asesoría legal o médica.</p>
    <p>Mirror Laboral<br>Claridad antes de decidir</p>
    """
    enviado = enviar_correo(m.email, ASUNTOS.get(clave_principal, "Tu Mirror ya está listo"), cuerpo, adjuntos)
    m.documentos_enviados = enviado
    db.add(m)
    db.commit()
