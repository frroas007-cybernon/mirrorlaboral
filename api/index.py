import sys
from pathlib import Path

# Vercel ejecuta este archivo como función serverless; agregamos la raíz del
# proyecto al path para poder importar el paquete `app`.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402,F401  (Vercel busca la variable `app`)
