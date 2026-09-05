# Mirror Laboral — Plataforma (v0, Mirror 1 en vivo)

Primer paso de la plataforma propia: el **Mirror 1** (gratis, 6 preguntas, screening de riesgo,
resultado personalizado, captura de correo) corriendo como app web real, lista para Vercel + Supabase.

El Mirror 2 (pago, Mercado Pago, generación de documentos, panel de leads) es la siguiente fase —
ver `BRIEF_PLATAFORMA_v2.md` en el proyecto KARIN para el plan completo.

## Qué incluye esta versión

- Formulario del Mirror 1 con las 6 preguntas exactas de `Mirror1_Preguntas_y_Resultados.md`.
- Screening de riesgo (R.1): si la respuesta no es "No", aparece de inmediato un aviso con
  Salud Responde (600 360 7777), sin bloquear que la persona siga con el formulario.
- Cálculo del patrón dominante/secundario con la misma lógica y textos aprobados.
- Guardado de cada respuesta en base de datos (Postgres vía Supabase en producción; SQLite local
  para pruebas).
- Identidad visual aplicada (paleta y tono de `Guia_Identidad_Validacion.md`).

## Correr localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre `http://127.0.0.1:8000`. Sin configurar nada más, usa un archivo SQLite local
(`local_dev.db`) — sirve para probar el flujo, pero **no uses SQLite en producción**: en Vercel
(serverless) el disco no persiste entre invocaciones, así que sin Supabase conectado se perderían
las respuestas.

## Desplegar en Vercel + Supabase (para tener URL pública)

1. **Supabase** (si aún no tienes el proyecto creado):
   - Crea un proyecto gratis en supabase.com.
   - Ve a *Project Settings → Database → Connection string*, elige el modo **"Transaction pooler"**
     (puerto 6543) y copia la URL, reemplazando `[YOUR-PASSWORD]` por la contraseña de tu proyecto.

2. **Vercel**:
   - En vercel.com → *Add New → Project* → importa este repo de GitHub.
   - En *Environment Variables* agrega `DATABASE_URL` con el connection string de Supabase del
     paso anterior.
   - Deploy. Vercel detecta `vercel.json` y `api/index.py` automáticamente (no hace falta tocar
     nada más).

3. Verifica que `/` y `/mirror1` respondan, completa un envío de prueba, y revisa en Supabase
   (*Table Editor → mirror1_responses*) que la fila haya quedado guardada.

## Estructura

```
api/index.py           # entrypoint que Vercel ejecuta como función serverless
app/main.py             # rutas FastAPI (/, /mirror1)
app/scoring_mirror1.py  # lógica de puntaje + textos de resultado (copiados del doc aprobado)
app/models.py           # tabla mirror1_responses (SQLAlchemy)
app/templates/          # HTML (Jinja2) con la identidad de marca aplicada
```
