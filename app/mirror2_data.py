"""
Preguntas, opciones y estructura del Mirror 2 -- copiadas palabra por palabra
de Mirror2_Preguntas_Detalladas.md (documento aprobado del proyecto KARIN).
No reformular ni resumir texto de aquí: si falta una pregunta o una opción,
se pide antes de inventarla.
"""

# ---------------------------------------------------------------- TIERS ----
TIERS = {
    "dt": {
        "titulo": "Listo para la DT",
        "precio": 15000,
        "resumen": "Tus datos y tu relato de los hechos, ya ordenados en el formato exacto que "
                    "pide la Dirección del Trabajo para presentar tu propia denuncia.",
        "incluye": ["Ficha de datos", "Relato cronológico listo para copiar", "Checklist de evidencia",
                    "Guía paso a paso para presentarla en el portal Mi DT"],
    },
    "psico": {
        "titulo": "Solo Psicológico",
        "precio": 20000,
        "resumen": "Tu Discovery Psicológico: cómo te ha afectado esto, por dimensión, listo para "
                    "compartir con quien te acompañe psicológicamente.",
        "incluye": ["Las 5 dimensiones evaluadas en profundidad", "Foco clínico preliminar",
                    "Tu propio relato, tal como lo escribiste"],
    },
    "legal": {
        "titulo": "Solo Legal",
        "precio": 20000,
        "resumen": "Tu Discovery Legal: los hechos ordenados, la evidencia disponible y el marco "
                    "legal general aplicable, listo para compartir con una abogada.",
        "incluye": ["Cronología de hechos", "Evaluación preliminar de tu evidencia",
                    "Marco legal general y plazos aplicables"],
    },
    "completo": {
        "titulo": "Completo",
        "precio": 25000,
        "resumen": "Los dos Discovery (Psicológico y Legal) más el Anexo DT, los tres a partir de "
                    "las mismas respuestas -- sin tener que contar tu historia dos veces.",
        "incluye": ["Discovery Psicológico", "Discovery Legal", "Anexo listo para la DT"],
    },
}

TIER_ORDEN = ["dt", "psico", "legal", "completo"]

ESCALA_FRECUENCIA = [
    ("Nunca", "Nunca"),
    ("Rara vez", "Rara vez"),
    ("A veces", "A veces"),
    ("Frecuentemente", "Frecuentemente"),
]

ESCALA_IMPACTO = [
    ("No ha cambiado", "No ha cambiado"),
    ("Cambió un poco", "Cambió un poco"),
    ("Cambió notoriamente", "Cambió notoriamente"),
]

RIESGO_OPCIONES = [
    ("No", "No"),
    ("A veces lo he pensado", "A veces lo he pensado"),
    ("Sí, con frecuencia", "Sí, con frecuencia"),
]

# --------------------------------------------------------- BLOQUE PSICOLÓGICO
PSICO_DIMENSIONES = [
    ("trato", "1. Trato y comunicación", [
        ("trato_1", "¿Con qué frecuencia te hablaron de forma humillante o descalificadora, especialmente frente a otras personas?"),
        ("trato_2", "¿Con qué frecuencia sentiste que se burlaron de ti o de tu trabajo de una forma que te hizo sentir mal?"),
        ("trato_3", "¿Con qué frecuencia te gritaron, alzaron la voz contigo o usaron un tono que te intimidó?"),
    ]),
    ("presion", "2. Presión y sobrecarga", [
        ("presion_1", "¿Con qué frecuencia sentiste que las exigencias o plazos que te pusieron eran desproporcionados?"),
        ("presion_2", "¿Con qué frecuencia te cambiaron funciones o responsabilidades sin explicación ni acuerdo?"),
        ("presion_3", "¿Con qué frecuencia sentiste que se te exigía más que a otras personas en tu mismo puesto, sin razón aparente?"),
    ]),
    ("aislamiento", "3. Aislamiento", [
        ("aislamiento_1", "¿Con qué frecuencia te dejaron fuera de reuniones, conversaciones o decisiones en las que antes participabas?"),
        ("aislamiento_2", "¿Con qué frecuencia sentiste que te ignoraban deliberadamente (no te saludaban, no respondían tus mensajes, etc.)?"),
        ("aislamiento_3", "¿Con qué frecuencia sentiste que hablaban de ti o de tu situación a tus espaldas?"),
    ]),
    ("amenazas", "4. Amenazas y persecución", [
        ("amenazas_1", "¿Con qué frecuencia sentiste que te vigilaban o controlaban de forma desproporcionada?"),
        ("amenazas_2", "¿Con qué frecuencia te insinuaron o dijeron directamente consecuencias negativas si no hacías algo específico?"),
        ("amenazas_3", "¿Con qué frecuencia sentiste miedo real de perder tu trabajo o de alguna represalia por esta situación?"),
    ]),
    ("impacto", "5. Impacto en ti", [
        ("impacto_1", "¿Con qué frecuencia pensaste en esta situación fuera del horario laboral, de una forma que te generó angustia?"),
        ("impacto_2", "¿Con qué frecuencia sentiste que esto afectó tu ánimo general, más allá del trabajo?"),
        ("impacto_3", "¿Con qué frecuencia evitaste ir a trabajar, o sentiste rechazo físico a la idea de ir?"),
    ]),
]

INVENTARIO_IMPACTO = [
    ("impacto_inv_1", "Tu forma de dormir en el último mes."),
    ("impacto_inv_2", "Tu apetito en el último mes."),
    ("impacto_inv_3", "Tu capacidad de concentrarte en tareas simples."),
    ("impacto_inv_4", "Tu ánimo general al despertar."),
]

RED_APOYO_OPCIONES = [
    ("Sí, con alguien de confianza", "Sí, con alguien de confianza"),
    ("A veces", "A veces"),
    ("No, no se lo he contado a nadie", "No, no se lo he contado a nadie"),
]

AYUDA_PREVIA_OPCIONES = [
    ("Sí, actualmente", "Sí, actualmente"),
    ("Sí, en el pasado", "Sí, en el pasado"),
    ("No", "No"),
]

SITUACION_ACTUAL_OPCIONES = [
    ("Voy con normalidad", "Voy con normalidad"),
    ("He faltado algunas veces", "He faltado algunas veces"),
    ("Estoy con licencia médica", "Estoy con licencia médica"),
]

EN_TRATAMIENTO_OPCIONES = [
    ("No", "No"),
    ("Sí, en tratamiento", "Sí, en tratamiento"),
    ("Sí, con medicamento", "Sí, con medicamento"),
    ("Ambos", "Ambos"),
]

OTRAS_AREAS_OPCIONES = [
    ("No especialmente", "No especialmente"),
    ("Un poco", "Un poco"),
    ("Sí, bastante", "Sí, bastante"),
]

ESTRATEGIAS_OPCIONES = [
    "Evito pensar en el tema",
    "He estado más aislado/a de amigos o familia",
    "He aumentado consumo de alcohol u otras sustancias",
    "He hablado con alguien de confianza",
    "Nada en particular",
    "Otro",
]

# -------------------------------------------------------------- BLOQUE LEGAL
ANTIGUEDAD_OPCIONES = [
    ("Menos de 6 meses", "Menos de 6 meses"),
    ("6 meses a 2 años", "6 meses a 2 años"),
    ("2 a 5 años", "2 a 5 años"),
    ("Más de 5 años", "Más de 5 años"),
]

TIPO_CONTRATO_OPCIONES = [
    ("Indefinido", "Indefinido"),
    ("Plazo fijo", "Plazo fijo"),
    ("Honorarios", "Honorarios"),
    ("No estoy seguro/a", "No estoy seguro/a"),
]

RELACION_OPCIONES = [
    ("Es mi jefatura directa", "Es mi jefatura directa"),
    ("Es de otra jefatura", "Es de otra jefatura"),
    ("Es un/a par o colega", "Es un/a par o colega"),
    ("Es un cliente o proveedor externo", "Es un cliente o proveedor externo"),
    ("Es más de una persona", "Es más de una persona"),
]

EVIDENCIA_OPCIONES = [
    "Correos electrónicos",
    "Mensajes de WhatsApp u otra app",
    "Testigos que vieron o vivieron algo similar",
    "Licencias médicas relacionadas",
    "Evaluaciones de desempeño",
    "Ninguno de estos, pero quiero denunciar igual",
]

TESTIGO_ACTIVO_OPCIONES = [
    ("Sí", "Sí"),
    ("No", "No"),
    ("No estoy seguro/a", "No estoy seguro/a"),
]

GESTION_PREVIA_OPCIONES = [
    ("No he hecho nada todavía", "No he hecho nada todavía"),
    ("Hablé informalmente con alguien de RR.HH. o mi jefatura", "Hablé informalmente con alguien de RR.HH. o mi jefatura"),
    ("Ya presenté una denuncia formal", "Ya presenté una denuncia formal"),
    ("Otro", "Otro"),
]

INTENCION_OPCIONES = [
    ("Quiero que la situación se resuelva y seguir en mi puesto", "Quiero que la situación se resuelva y seguir en mi puesto"),
    ("Estoy evaluando irme de la empresa", "Estoy evaluando irme de la empresa"),
    ("Todavía no lo tengo claro, necesito pensarlo con más información", "Todavía no lo tengo claro, necesito pensarlo con más información"),
]

PROTOCOLO_VIGENTE_OPCIONES = [
    ("Sí", "Sí"),
    ("No", "No"),
    ("No lo sé", "No lo sé"),
]

FUERO_OPCIONES = [
    "Embarazo o post natal",
    "Dirigente sindical o delegado/a de personal",
    "Ninguna de las anteriores",
]

FINIQUITO_OPCIONES = [
    ("No, sigo trabajando ahí", "No, sigo trabajando ahí"),
    ("Sí, firmé algo", "Sí, firmé algo"),
    ("No estoy seguro/a", "No estoy seguro/a"),
]


def incluye_psico(tier: str) -> bool:
    return tier in ("psico", "completo")


def incluye_legal_completo(tier: str) -> bool:
    return tier in ("legal", "completo")


def incluye_legal_dt_subset(tier: str) -> bool:
    return tier == "dt"


def incluye_legal(tier: str) -> bool:
    """Cualquier tier que necesita al menos parte del bloque legal (dt, legal o completo)."""
    return tier in ("dt", "legal", "completo")
