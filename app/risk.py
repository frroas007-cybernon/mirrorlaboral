"""
Revision basica de palabras clave de riesgo en campos de texto libre.
Parte del protocolo de riesgo definido en Sistema_Mirror_3_Niveles.md: si el
screening formal (R.1) dio "No" pero el texto libre contiene señales de
riesgo, igual debe activarse el mismo aviso en pantalla.
"""

PALABRAS_RIESGO = [
    "suicid",
    "matarme",
    "quitarme la vida",
    "no quiero vivir",
    "no quiero seguir viviendo",
    "acabar con todo",
    "acabar con mi vida",
    "terminar con mi vida",
    "terminar con todo",
    "hacerme daño",
    "hacerme dano",
    "autolesion",
    "autolesión",
    "no aguanto mas",
    "no aguanto más",
    "no puedo mas",
    "no puedo más",
    "quiero morir",
    "prefiero estar muerto",
    "prefiero estar muerta",
    "desaparecer para siempre",
]


def contiene_senales_riesgo(*textos) -> bool:
    for texto in textos:
        if not texto:
            continue
        bajo = texto.lower()
        for palabra in PALABRAS_RIESGO:
            if palabra in bajo:
                return True
    return False
