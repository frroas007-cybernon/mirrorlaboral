from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def agregar_columnas_faltantes():
    """
    Migración minima: Base.metadata.create_all() solo crea tablas nuevas, no
    agrega columnas nuevas a una tabla que ya existe (por ejemplo, al agregar
    `nombre`/`telefono` a mirror1_responses despues de que la tabla ya vivia
    en produccion). No usamos Alembic por simplicidad de mantenimiento (una
    sola persona opera esto) -- en vez de eso, comparamos las columnas que
    SQLAlchemy espera contra las que existen de verdad y agregamos las que
    falten con ALTER TABLE. Cada columna nueva debe ser nullable.
    """
    inspector = inspect(engine)
    for tabla in Base.metadata.tables.values():
        if not inspector.has_table(tabla.name):
            continue
        columnas_existentes = {c["name"] for c in inspector.get_columns(tabla.name)}
        for columna in tabla.columns:
            if columna.name in columnas_existentes:
                continue
            tipo_sql = columna.type.compile(dialect=engine.dialect)
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE {tabla.name} ADD COLUMN {columna.name} {tipo_sql}'))
