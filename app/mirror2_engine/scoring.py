"""
Motor de puntajes del Mirror 2.
Copiado tal cual desde scoring.py (documento aprobado del proyecto KARIN) --
no reformular ni cambiar la logica de negocio. Unico cambio respecto al
original: vive dentro del paquete app.mirror2_engine para poder importarse
desde la app web.
"""

SCALE = {"Nunca": 0, "Rara vez": 1, "A veces": 2, "Frecuentemente": 3}

DIMENSIONS = {
    "trato": ["trato_1", "trato_2", "trato_3"],
    "presion": ["presion_1", "presion_2", "presion_3"],
    "aislamiento": ["aislamiento_1", "aislamiento_2", "aislamiento_3"],
    "amenazas": ["amenazas_1", "amenazas_2", "amenazas_3"],
    "impacto": ["impacto_1", "impacto_2", "impacto_3"],
}

DIMENSION_NAMES = {
    "trato": "Trato y comunicación",
    "presion": "Presión y sobrecarga",
    "aislamiento": "Aislamiento",
    "amenazas": "Amenazas y persecución",
    "impacto": "Impacto en ti",
}

# Orden de prioridad para desempatar, igual al definido en el Mirror 1 y 2
PRIORITY = ["impacto", "amenazas", "trato", "aislamiento", "presion"]


def compute_scores(answers: dict) -> dict:
    """Suma el puntaje 0-9 de cada dimension a partir de las respuestas."""
    scores = {}
    for dim, question_ids in DIMENSIONS.items():
        total = 0
        for qid in question_ids:
            respuesta = answers.get(qid, "Nunca")
            total += SCALE.get(respuesta, 0)
        scores[dim] = total
    return scores


def level_label(score: int) -> str:
    if score >= 6:
        return "Marcado"
    if score >= 3:
        return "Moderado"
    return "Leve"


def top_and_secondary(scores: dict):
    """Devuelve la dimension dominante y la secundaria (si aplica), respetando
    el orden de prioridad definido para desempatar."""
    ordered = sorted(scores.keys(), key=lambda d: (-scores[d], PRIORITY.index(d)))
    top = ordered[0]
    secondary = None
    for dim in ordered[1:]:
        if scores[dim] >= 4:
            secondary = dim
            break
    return top, secondary
