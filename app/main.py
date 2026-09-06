from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError

from app.db import Base, engine, get_db
from app.models import Mirror1Response
from app.config import SALUD_RESPONDE_TELEFONO
from app.scoring_mirror1 import (
    DIMENSIONS,
    TIEMPO_OPCIONES,
    RIESGO_OPCIONES,
    compute_result,
    build_result_text,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Mirror Laboral")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

ESCALA = [("0", "Nunca"), ("1", "Rara vez"), ("2", "A veces"), ("3", "Frecuentemente")]

PREGUNTAS_DIMENSION = [
    ("trato", "En el último mes, ¿con qué frecuencia sentiste que te hablaron de forma humillante, "
              "descalificadora o en un tono que te hizo sentir menos, especialmente frente a otras personas?"),
    ("presion", "En el último mes, ¿con qué frecuencia sentiste que las exigencias, los plazos o los cambios en "
                "tus funciones eran desproporcionados o injustos?"),
    ("aislamiento", "En el último mes, ¿con qué frecuencia sentiste que te dejaron fuera de conversaciones, "
                    "decisiones o espacios en los que antes participabas con normalidad?"),
    ("amenazas", "En el último mes, ¿con qué frecuencia sentiste que alguien te vigilaba, te seguía de cerca o te "
                 "insinuaba consecuencias si no hacías algo específico?"),
    ("impacto", "En el último mes, ¿con qué frecuencia pensaste en tu trabajo fuera del horario laboral de una "
                "forma que te generó angustia, mal dormir o ansiedad?"),
]


@app.on_event("startup")
def on_startup():
    # Crea las tablas si no existen. En serverless pueden arrancar varias
    # instancias en paralelo e intentar crear la misma tabla a la vez -- eso
    # no es un error real (la tabla ya quedo creada por la otra instancia),
    # asi que lo ignoramos en vez de tumbar el arranque de la app.
    try:
        Base.metadata.create_all(bind=engine)
    except ProgrammingError as exc:
        if "already exists" not in str(exc):
            raise


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/mirror1", response_class=HTMLResponse)
def mirror1_form(request: Request):
    return templates.TemplateResponse(
        "mirror1_form.html",
        {
            "request": request,
            "riesgo_opciones": RIESGO_OPCIONES,
            "escala": ESCALA,
            "preguntas": PREGUNTAS_DIMENSION,
            "tiempo_opciones": TIEMPO_OPCIONES,
            "telefono_ayuda": SALUD_RESPONDE_TELEFONO,
        },
    )


@app.post("/mirror1", response_class=HTMLResponse)
def mirror1_submit(
    request: Request,
    db: Session = Depends(get_db),
    riesgo: str = Form(...),
    trato: int = Form(...),
    presion: int = Form(...),
    aislamiento: int = Form(...),
    amenazas: int = Form(...),
    impacto: int = Form(...),
    contexto: str = Form(...),
    email: str = Form(...),
):
    scores = {
        "trato": trato,
        "presion": presion,
        "aislamiento": aislamiento,
        "amenazas": amenazas,
        "impacto": impacto,
    }
    principal, secundario = compute_result(scores, contexto)

    riesgo_flag = riesgo != "no"

    respuesta = Mirror1Response(
        email=email.strip(),
        riesgo_respuesta=riesgo,
        riesgo_flag=riesgo_flag,
        trato=trato,
        presion=presion,
        aislamiento=aislamiento,
        amenazas=amenazas,
        impacto=impacto,
        contexto_tiempo=contexto,
        patron_principal=principal,
        patron_secundario=secundario,
    )
    db.add(respuesta)
    db.commit()

    resultado = build_result_text(principal, secundario, contexto)

    return templates.TemplateResponse(
        "mirror1_result.html",
        {
            "request": request,
            "resultado": resultado,
            "riesgo_flag": riesgo_flag,
            "telefono_ayuda": SALUD_RESPONDE_TELEFONO,
        },
    )
