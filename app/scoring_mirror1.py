"""
Scoring y textos de resultado del Mirror 1.
Contenido copiado tal cual de Mirror1_Preguntas_y_Resultados.md (documento
aprobado del proyecto KARIN) -- no reformular ni resumir estos textos.
"""

DIMENSIONS = ["trato", "presion", "aislamiento", "amenazas", "impacto"]

DIMENSION_LABELS = {
    "trato": "trato y comunicación",
    "presion": "presión y sobrecarga",
    "aislamiento": "aislamiento",
    "amenazas": "amenazas y persecución",
    "impacto": "impacto en ti",
}

# Orden de prioridad para desempatar en primer lugar, igual al definido en el documento.
PRIORITY = ["impacto", "amenazas", "trato", "aislamiento", "presion"]

TIEMPO_MAP = {
    "unas_semanas": "unas semanas",
    "unos_meses": "unos meses",
    "mas_6_meses": "más de 6 meses",
    "mas_1_anio": "más de un año",
}

TIEMPO_OPCIONES = [
    ("unas_semanas", "Hace unas semanas"),
    ("unos_meses", "Hace unos meses"),
    ("mas_6_meses", "Hace más de 6 meses"),
    ("mas_1_anio", "Hace más de un año"),
]

RIESGO_OPCIONES = [
    ("no", "No"),
    ("a_veces", "A veces lo he pensado"),
    ("si", "Sí, con frecuencia"),
]


def compute_result(scores: dict, contexto_key: str):
    """
    scores: dict con las 5 dimensiones -> puntaje 0-3.
    Devuelve (patron_principal, patron_secundario) según la lógica del documento:
    - Si las 5 respuestas son 0 o 1 -> (None, None) = "sin patrón marcado".
    - Si no, el más alto es el principal; el segundo más alto es secundario
      solo si tiene 2 puntos o más.
    - Empates en primer lugar se resuelven con PRIORITY.
    """
    if all(scores[d] <= 1 for d in DIMENSIONS):
        return None, None

    ordered = sorted(DIMENSIONS, key=lambda d: (-scores[d], PRIORITY.index(d)))
    principal = ordered[0]
    secundario = None
    for d in ordered[1:]:
        if scores[d] >= 2:
            secundario = d
            break
    return principal, secundario


def _secundario_frase(dim_secundario, plantilla):
    if not dim_secundario:
        return None
    return plantilla.format(secundario=DIMENSION_LABELS[dim_secundario])


def build_result_text(principal, secundario, contexto_key):
    """Devuelve una lista de párrafos (strings) para el resultado, en el orden
    exacto en que deben mostrarse."""
    tiempo = TIEMPO_MAP.get(contexto_key, "un tiempo")

    if principal is None:
        return {
            "titulo": "Por lo que respondiste, no aparece un patrón fuerte en ninguna de las seis áreas que preguntamos.",
            "parrafos": [
                "Eso, en principio, es una buena noticia. Pero si de todas formas sientes que algo no está del todo bien "
                "y este primer vistazo no logró capturarlo —porque seis preguntas rápidas nunca cuentan la historia "
                "completa—, tu Mirror completo tiene más profundidad y puede ayudarte a verlo con más detalle."
            ],
        }

    if principal == "trato":
        parrafos = [
            f"Hace {tiempo} que sientes que te hablan de una forma que te hace sentir menos — y que eso pasa, muchas "
            "veces, frente a otras personas. Eso no es solo \"un jefe difícil\" o \"así es el ambiente acá\": es un "
            "patrón que se repite, y los patrones que se repiten dejan huella, aunque a veces cueste nombrarla.",
        ]
        sec = _secundario_frase(secundario, "Y no es lo único que aparece en lo que contaste — también hay señales de "
                                              "{secundario}, algo que muchas veces va de la mano con esto, aunque no "
                                              "siempre se conecta a simple vista.")
        if sec:
            parrafos.append(sec)
        parrafos.append("Tu Mirror completo te muestra cómo se conectan estas piezas entre sí, y qué caminos tienen "
                         "sentido para tu situación específica.")
        return {"titulo": "Lo que más se repite en tu respuesta: el trato.", "parrafos": parrafos}

    if principal == "presion":
        parrafos = [
            f"Hace {tiempo} que sientes que lo que te piden no es proporcional ni justo. Esto es de las señales más "
            "fáciles de minimizar — \"es que el cargo es así\", \"es que estamos en una etapa exigente\" — y de las "
            "que más cuesta ver con claridad desde adentro, precisamente porque el trabajo mismo se supone que "
            "exige esfuerzo.",
        ]
        sec = _secundario_frase(secundario, "Sumado a esto, tu respuesta también muestra señales de {secundario} — "
                                              "dos cosas que, juntas, cuentan una historia más completa que "
                                              "cualquiera de las dos por separado.")
        if sec:
            parrafos.append(sec)
        parrafos.append("Tu Mirror completo te ayuda a ver si lo que estás viviendo es exigencia normal del cargo, "
                         "o algo más.")
        return {"titulo": "Lo que más se repite en tu respuesta: la presión.", "parrafos": parrafos}

    if principal == "aislamiento":
        parrafos = [
            f"Hace {tiempo} que sientes que te dejaron fuera — de conversaciones, de decisiones, de espacios donde "
            "antes estabas con naturalidad. Esta es, de las seis señales que preguntamos, una de las que menos se "
            "nombra en voz alta, porque no deja marca visible ni una frase que puedas repetir. Pero se siente, y "
            "se acumula.",
        ]
        sec = _secundario_frase(secundario, "Tu respuesta también muestra {secundario} — el aislamiento rara vez "
                                              "llega solo.")
        if sec:
            parrafos.append(sec)
        parrafos.append("Tu Mirror completo profundiza en cómo se conecta esto con el resto de tu situación.")
        return {"titulo": "Lo que más se repite en tu respuesta: el aislamiento.", "parrafos": parrafos}

    if principal == "amenazas":
        parrafos = [
            "De las seis áreas que preguntamos, esta es la que con más frecuencia indica que algo necesita mirarse "
            f"pronto, no después. Hace {tiempo} que sientes esto, y eso ya es información importante por sí sola.",
        ]
        sec = _secundario_frase(secundario, "Esto además viene acompañado de {secundario} en lo que nos contaste — "
                                              "una combinación que conviene mirar completa, no por partes.")
        if sec:
            parrafos.append(sec)
        parrafos.append("Te recomendamos avanzar directamente a tu Mirror completo.")
        return {
            "titulo": "Lo que más se repite en tu respuesta: la sensación de estar siendo vigilado/a o presionado/a "
                      "con consecuencias.",
            "parrafos": parrafos,
        }

    if principal == "impacto":
        parrafos = [
            f"Hace {tiempo} que esto te sigue fuera del horario laboral: te acompaña cuando intentas dormir, cuando "
            "deberías estar pensando en otra cosa. De las seis señales que preguntamos, esta es la que habla menos "
            "de \"qué está pasando\" y más de \"qué te está costando\" — y eso, aunque sea difícil de medir, es tan "
            "real como cualquier otra.",
        ]
        sec = _secundario_frase(secundario, "Esto no ocurre en el vacío: tu respuesta también muestra señales de "
                                              "{secundario}, que probablemente sea parte de lo que está pesando.")
        if sec:
            parrafos.append(sec)
        parrafos.append("Tu Mirror completo te ayuda a ordenar esto y ver qué alternativas tiene sentido "
                         "considerar — no solo para la situación, también para ti.")
        return {
            "titulo": "Lo que más se repite en tu respuesta: cómo te está afectando a ti — no solo lo que ocurre en "
                      "el trabajo.",
            "parrafos": parrafos,
        }

    raise ValueError(f"Dimensión desconocida: {principal}")
