import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Si no hay DATABASE_URL (Supabase) configurada, usamos SQLite local para poder
# probar el flujo completo sin depender todavía de Supabase.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./local_dev.db")

SALUD_RESPONDE_TELEFONO = "600 360 7777"
