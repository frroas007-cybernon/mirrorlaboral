from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError

from app.db import Base, engine, get_db
from app.models import Mirror1Response, Mirror2Response
from app.config import SALUD_RESPONDE_TELEFONO, MODO_PAGO_SIMULADO, SITE_URL
from app.scoring_mirror1 import (
    DIMENSIONS,
    TIEMPO_OPCIONES,
    RIESGO_OPCIONES,
    compute_result,
    build_result_text,
)
from app import mirror2_data as m2
from app.risk import contiene_senales_riesgo
from app.mailer import alertar_riesgo_interno, enviar_correo
from app.mirror2_flow import procesar_pago_confirmado
from app.mercadopago_client import crear_preferencia, obtener_pago, MercadoPagoNoConfigurado
from app.panel_auth import verificar_password, crear_token, leer_token, PROFESIONALES, COOKIE_NAME

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Mirror Laboral")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
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
    # no es un error real (la tabla ya quedó creada por la otra instancia),
    # así que lo ignoramos en vez de tumbar el arranque de la app.
    try:
        Base.metadata.create_all(bind=engine)
    except ProgrammingError as exc:
        if "already exists" not in str(exc):
            raise


# ---------------------------------------------------------------- LANDING --
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/elegir", response_class=HTMLResponse)
def elegir(request: Request):
    return templates.TemplateResponse("elegir.html", {"request": request})


# ---------------------------------------------------------------- MIRROR 1 -
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

    if riesgo_flag:
        alertar_riesgo_interno("Mirror 1 (screening R.1)", email.strip())

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


# ---------------------------------------------------------------- MIRROR 2 -
@app.get("/mirror2", response_class=HTMLResponse)
def mirror2_intro(request: Request):
    return templates.TemplateResponse(
        "mirror2_intro.html",
        {"request": request, "tiers": m2.TIERS, "tier_orden": m2.TIER_ORDEN},
    )


@app.get("/mirror2/formulario", response_class=HTMLResponse)
def mirror2_formulario(request: Request, tier: str):
    if tier not in m2.TIERS:
        return RedirectResponse("/mirror2")
    return templates.TemplateResponse(
        "mirror2_form.html",
        {
            "request": request,
            "tier": tier,
            "tier_info": m2.TIERS[tier],
            "telefono_ayuda": SALUD_RESPONDE_TELEFONO,
            "riesgo_opciones": m2.RIESGO_OPCIONES,
            "escala_frecuencia": m2.ESCALA_FRECUENCIA,
            "escala_impacto": m2.ESCALA_IMPACTO,
            "psico_dimensiones": m2.PSICO_DIMENSIONES,
            "inventario_impacto": m2.INVENTARIO_IMPACTO,
            "red_apoyo_opciones": m2.RED_APOYO_OPCIONES,
            "ayuda_previa_opciones": m2.AYUDA_PREVIA_OPCIONES,
            "situacion_actual_opciones": m2.SITUACION_ACTUAL_OPCIONES,
            "en_tratamiento_opciones": m2.EN_TRATAMIENTO_OPCIONES,
            "otras_areas_opciones": m2.OTRAS_AREAS_OPCIONES,
            "estrategias_opciones": m2.ESTRATEGIAS_OPCIONES,
            "antiguedad_opciones": m2.ANTIGUEDAD_OPCIONES,
            "tipo_contrato_opciones": m2.TIPO_CONTRATO_OPCIONES,
            "relacion_opciones": m2.RELACION_OPCIONES,
            "evidencia_opciones": m2.EVIDENCIA_OPCIONES,
            "testigo_activo_opciones": m2.TESTIGO_ACTIVO_OPCIONES,
            "gestion_previa_opciones": m2.GESTION_PREVIA_OPCIONES,
            "intencion_opciones": m2.INTENCION_OPCIONES,
            "protocolo_vigente_opciones": m2.PROTOCOLO_VIGENTE_OPCIONES,
            "fuero_opciones": m2.FUERO_OPCIONES,
            "finiquito_opciones": m2.FINIQUITO_OPCIONES,
            "incluye_psico": m2.incluye_psico(tier),
            "incluye_legal": m2.incluye_legal(tier),
            "incluye_legal_completo": m2.incluye_legal_completo(tier),
        },
    )


def _campo(form, nombre):
    valor = form.get(nombre)
    return valor.strip() if isinstance(valor, str) and valor.strip() else None


def _lista(form, nombre):
    valores = [v for v in form.getlist(nombre) if v]
    return "; ".join(valores) if valores else None


@app.post("/mirror2/formulario")
async def mirror2_formulario_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    tier = form.get("tier")
    if tier not in m2.TIERS:
        return RedirectResponse("/mirror2", status_code=303)

    nombre = _campo(form, "nombre") or "—"
    email = _campo(form, "email")
    riesgo_screening = _campo(form, "riesgo_screening") or "No"

    m = Mirror2Response(
        nombre=nombre,
        email=email or "",
        tier=tier,
        precio=m2.TIERS[tier]["precio"],
        payment_status="pending",
        riesgo_screening=riesgo_screening,
        contacto_confianza=_campo(form, "contacto_confianza"),
        trato_1=_campo(form, "trato_1"), trato_2=_campo(form, "trato_2"), trato_3=_campo(form, "trato_3"),
        presion_1=_campo(form, "presion_1"), presion_2=_campo(form, "presion_2"), presion_3=_campo(form, "presion_3"),
        aislamiento_1=_campo(form, "aislamiento_1"), aislamiento_2=_campo(form, "aislamiento_2"),
        aislamiento_3=_campo(form, "aislamiento_3"),
        amenazas_1=_campo(form, "amenazas_1"), amenazas_2=_campo(form, "amenazas_2"),
        amenazas_3=_campo(form, "amenazas_3"),
        impacto_1=_campo(form, "impacto_1"), impacto_2=_campo(form, "impacto_2"), impacto_3=_campo(form, "impacto_3"),
        impacto_inv_1=_campo(form, "impacto_inv_1"), impacto_inv_2=_campo(form, "impacto_inv_2"),
        impacto_inv_3=_campo(form, "impacto_inv_3"), impacto_inv_4=_campo(form, "impacto_inv_4"),
        red_apoyo=_campo(form, "red_apoyo"),
        ayuda_psicologica_previa=_campo(form, "ayuda_psicologica_previa"),
        motivo_consulta=_campo(form, "motivo_consulta"),
        situacion_actual=_campo(form, "situacion_actual"),
        en_tratamiento=_campo(form, "en_tratamiento"),
        otras_areas_afectadas=_campo(form, "otras_areas_afectadas"),
        estrategias_afrontamiento=_lista(form, "estrategias_afrontamiento"),
        open_text=_campo(form, "open_text"),
        cargo=_campo(form, "cargo"),
        antiguedad=_campo(form, "antiguedad"),
        tipo_contrato=_campo(form, "tipo_contrato"),
        persona_senalada=_campo(form, "persona_senalada"),
        relacion=_campo(form, "relacion"),
        empresa_nombre=_campo(form, "empresa_nombre"),
        empresa_rut=_campo(form, "empresa_rut"),
        inicio=_campo(form, "inicio"),
        relato_libre=_campo(form, "relato_libre"),
        evidencia_lista=_lista(form, "evidencia_lista"),
        testigo_activo=_campo(form, "testigo_activo"),
        gestion_previa=_campo(form, "gestion_previa"),
        gestion_previa_hace_cuanto=_campo(form, "gestion_previa_hace_cuanto"),
        intencion=_campo(form, "intencion"),
        protocolo_vigente=_campo(form, "protocolo_vigente"),
        fuero=_lista(form, "fuero"),
        remuneracion=_campo(form, "remuneracion"),
        firmo_finiquito=_campo(form, "firmo_finiquito"),
    )

    # Protocolo de riesgo: R.1 distinto de "No", o señales en cualquier texto libre.
    señales_en_texto = contiene_senales_riesgo(m.open_text, m.motivo_consulta, m.relato_libre)
    m.riesgo_flag = (riesgo_screening != "No") or señales_en_texto

    db.add(m)
    db.commit()
    db.refresh(m)

    if m.riesgo_flag:
        alertar_riesgo_interno("Mirror 2 (formulario)", m.email, m.nombre)

    if MODO_PAGO_SIMULADO:
        # No hay credenciales de Mercado Pago configuradas todavía -- se deja avanzar el
        # flujo igual (modo de prueba) para poder revisar el formulario completo y la
        # generación de documentos sin depender de un pago real.
        m.payment_status = "approved"
        db.add(m)
        db.commit()
        procesar_pago_confirmado(db, m)
        return RedirectResponse(f"/mirror2/gracias/{m.id}", status_code=303)

    try:
        preferencia = crear_preferencia(m.id, tier, m.email)
    except MercadoPagoNoConfigurado:
        return RedirectResponse(f"/mirror2/pago-fallido/{m.id}", status_code=303)

    m.preference_id = preferencia.get("id")
    db.add(m)
    db.commit()

    init_point = preferencia.get("init_point") or preferencia.get("sandbox_init_point")
    return RedirectResponse(init_point, status_code=303)


@app.post("/mirror2/webhook")
async def mirror2_webhook(request: Request, db: Session = Depends(get_db)):
    # Mercado Pago manda la notificación por query params (?type=payment&data.id=...)
    # o por body JSON, según el tipo de integración -- cubrimos ambos casos.
    params = dict(request.query_params)
    payment_id = params.get("data.id") or params.get("id")
    tipo = params.get("type") or params.get("topic")

    if not payment_id:
        try:
            body = await request.json()
            payment_id = (body.get("data") or {}).get("id") or body.get("id")
            tipo = tipo or body.get("type") or body.get("topic")
        except Exception:
            pass

    if tipo not in (None, "payment") or not payment_id:
        return PlainTextResponse("ok")

    try:
        pago = obtener_pago(payment_id)
    except Exception:
        return PlainTextResponse("ok")

    response_id = pago.get("external_reference")
    estado = pago.get("status")
    if not response_id:
        return PlainTextResponse("ok")

    m = db.query(Mirror2Response).filter(Mirror2Response.id == response_id).first()
    if not m:
        return PlainTextResponse("ok")

    m.payment_id = str(payment_id)
    if estado == "approved":
        m.payment_status = "approved"
        db.add(m)
        db.commit()
        procesar_pago_confirmado(db, m)
    else:
        m.payment_status = estado or m.payment_status
        db.add(m)
        db.commit()

    return PlainTextResponse("ok")


@app.get("/mirror2/gracias/{response_id}", response_class=HTMLResponse)
def mirror2_gracias(request: Request, response_id: str, db: Session = Depends(get_db)):
    m = db.query(Mirror2Response).filter(Mirror2Response.id == response_id).first()
    if not m:
        return RedirectResponse("/mirror2")

    # Respaldo: si Mercado Pago todavía no mandó el webhook pero la persona ya volvió
    # del checkout con el pago aprobado, lo confirmamos aquí mismo.
    qp = request.query_params
    if not m.documentos_generados and qp.get("status") == "approved" and qp.get("payment_id"):
        m.payment_status = "approved"
        m.payment_id = qp.get("payment_id")
        db.add(m)
        db.commit()
        procesar_pago_confirmado(db, m)

    return templates.TemplateResponse(
        "mirror2_gracias.html",
        {
            "request": request,
            "m": m,
            "telefono_ayuda": SALUD_RESPONDE_TELEFONO,
        },
    )


@app.get("/mirror2/pago-fallido/{response_id}", response_class=HTMLResponse)
def mirror2_pago_fallido(request: Request, response_id: str):
    return templates.TemplateResponse(
        "mirror2_pago_fallido.html", {"request": request, "response_id": response_id}
    )


@app.post("/mirror2/derivar/{response_id}", response_class=HTMLResponse)
def mirror2_derivar(
    request: Request,
    response_id: str,
    db: Session = Depends(get_db),
    quiere_paz: bool = Form(False),
    quiere_abogada: bool = Form(False),
):
    m = db.query(Mirror2Response).filter(Mirror2Response.id == response_id).first()
    if not m:
        return RedirectResponse("/mirror2")

    nuevo_para_paz = quiere_paz and m.doc_psicologico and not m.deriva_paz
    nuevo_para_abogada = quiere_abogada and m.doc_legal and not m.deriva_abogada

    if quiere_paz and m.doc_psicologico:
        m.deriva_paz = True
        m.estado_paz = m.estado_paz or "nuevo"
    if quiere_abogada and m.doc_legal:
        m.deriva_abogada = True
        m.estado_abogada = m.estado_abogada or "nuevo"
    db.add(m)
    db.commit()

    # Notificación a la profesional -- nunca lleva el contenido sensible, solo el aviso.
    # El detalle se revisa dentro del panel, con login.
    aviso_html = (
        "<p>Hay un nuevo caso disponible en tu panel de Mirror Laboral.</p>"
        f"<p>Ingresa con tu contraseña habitual para revisarlo: {SITE_URL}/panel</p>"
    )
    if nuevo_para_paz and PROFESIONALES["paz"]["email"]:
        enviar_correo(PROFESIONALES["paz"]["email"], "Nuevo caso disponible — Mirror Laboral", aviso_html)
    if nuevo_para_abogada and PROFESIONALES["abogada"]["email"]:
        enviar_correo(PROFESIONALES["abogada"]["email"], "Nuevo caso disponible — Mirror Laboral", aviso_html)

    return templates.TemplateResponse(
        "mirror2_gracias.html",
        {"request": request, "m": m, "telefono_ayuda": SALUD_RESPONDE_TELEFONO, "derivacion_ok": True},
    )


# ------------------------------------------------------ PANEL PROFESIONALES
@app.get("/panel/login", response_class=HTMLResponse)
def panel_login_form(request: Request):
    return templates.TemplateResponse("panel_login.html", {"request": request, "error": None})


@app.post("/panel/login", response_class=HTMLResponse)
def panel_login_submit(request: Request, profesional: str = Form(...), password: str = Form(...)):
    if not verificar_password(profesional, password):
        return templates.TemplateResponse(
            "panel_login.html", {"request": request, "error": "Usuario o contraseña incorrectos."}
        )
    token = crear_token(profesional)
    resp = RedirectResponse("/panel", status_code=303)
    resp.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", max_age=60 * 60 * 12)
    return resp


@app.get("/panel/logout")
def panel_logout():
    resp = RedirectResponse("/panel/login", status_code=303)
    resp.delete_cookie(COOKIE_NAME)
    return resp


def _sesion_actual(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    return leer_token(token)


@app.get("/panel", response_class=HTMLResponse)
def panel_dashboard(request: Request, db: Session = Depends(get_db)):
    profesional_id = _sesion_actual(request)
    if not profesional_id:
        return RedirectResponse("/panel/login")

    if profesional_id == "paz":
        leads = db.query(Mirror2Response).filter(Mirror2Response.deriva_paz.is_(True)).order_by(
            Mirror2Response.created_at.desc()
        ).all()
    else:
        leads = db.query(Mirror2Response).filter(Mirror2Response.deriva_abogada.is_(True)).order_by(
            Mirror2Response.created_at.desc()
        ).all()

    return templates.TemplateResponse(
        "panel_dashboard.html",
        {
            "request": request,
            "profesional": PROFESIONALES[profesional_id],
            "profesional_id": profesional_id,
            "leads": leads,
        },
    )


@app.post("/panel/lead/{response_id}/estado")
def panel_actualizar_estado(request: Request, response_id: str, db: Session = Depends(get_db)):
    profesional_id = _sesion_actual(request)
    if not profesional_id:
        return RedirectResponse("/panel/login")
    m = db.query(Mirror2Response).filter(Mirror2Response.id == response_id).first()
    if m:
        if profesional_id == "paz" and m.deriva_paz:
            m.estado_paz = "contactado" if m.estado_paz != "contactado" else "nuevo"
        elif profesional_id == "abogada" and m.deriva_abogada:
            m.estado_abogada = "contactado" if m.estado_abogada != "contactado" else "nuevo"
        db.add(m)
        db.commit()
    return RedirectResponse("/panel", status_code=303)


@app.get("/panel/documento/{response_id}")
def panel_descargar_documento(request: Request, response_id: str, db: Session = Depends(get_db)):
    profesional_id = _sesion_actual(request)
    if not profesional_id:
        return RedirectResponse("/panel/login")
    m = db.query(Mirror2Response).filter(Mirror2Response.id == response_id).first()
    if not m:
        return RedirectResponse("/panel")

    if profesional_id == "paz" and m.deriva_paz and m.doc_psicologico:
        contenido, nombre_archivo = m.doc_psicologico, "Discovery_Psicologico.docx"
    elif profesional_id == "abogada" and m.deriva_abogada and m.doc_legal:
        contenido, nombre_archivo = m.doc_legal, "Discovery_Legal.docx"
    else:
        return RedirectResponse("/panel")

    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )
