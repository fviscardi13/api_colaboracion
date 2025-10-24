import psycopg2
from psycopg2 import sql
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import os

db = SQLAlchemy()

def ensure_postgres_ready():
    """Garantiza que existan el usuario, la base y los permisos antes de usar SQLAlchemy."""
    from app.config import Config

    url = urlparse(Config.SQLALCHEMY_DATABASE_URI)
    dbname = url.path[1:] 
    user = url.username
    password = url.password
    host = url.hostname or "localhost"
    port = url.port or 5432

    admin_user = os.getenv("POSTGRES_ADMIN_USER", "postgres")
    admin_pass = os.getenv("POSTGRES_ADMIN_PASS", "postgres")
    print(f"🔧 Verificando base '{dbname}' y usuario '{user}'...")

    admin_conn = psycopg2.connect(
        dbname="postgres",
        user=admin_user,
        password=admin_pass,
        host=host,
        port=port
    )
    admin_conn.autocommit = True
    cur = admin_conn.cursor()

    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", (user,))
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s;").format(sql.Identifier(user)), [password])
        print(f"Usuario '{user}' creado.")
    else:
        print(f"Usuario '{user}' ya existe.")

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (dbname,))
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE DATABASE {} OWNER {};").format(
            sql.Identifier(dbname),
            sql.Identifier(user)
        ))
        print(f"Base de datos '{dbname}' creada.")
    else:
        print(f"Base de datos '{dbname}' ya existe.")

    cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {};").format(
        sql.Identifier(dbname),
        sql.Identifier(user)
    ))
    cur.close()
    admin_conn.close()

    user_conn = psycopg2.connect(
        dbname=dbname,
        user=admin_user,
        password=admin_pass,
        host=host,
        port=port
    )
    user_conn.autocommit = True
    cur2 = user_conn.cursor()
    cur2.execute(sql.SQL("""
        CREATE SCHEMA IF NOT EXISTS public;
        GRANT USAGE, CREATE ON SCHEMA public TO {};
        ALTER SCHEMA public OWNER TO {};
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {};
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {};
    """).format(
        sql.Identifier(user),
        sql.Identifier(user),
        sql.Identifier(user),
        sql.Identifier(user)
    ))
    cur2.close()
    user_conn.close()

    print("PostgreSQL listo para usarse.\n")


def init_database(app):
    """Inicializa SQLAlchemy y garantiza que todo esté creado."""
    ensure_postgres_ready()
    db.init_app(app)

    with app.app_context():
        from app.models.ong_model import ONG
        from app.models.project_model import Project
        from app.models.request_model import Request
        from app.models.commitment_model import Commitment

        db.create_all()
        print("Tablas verificadas/creadas correctamente.\n")
