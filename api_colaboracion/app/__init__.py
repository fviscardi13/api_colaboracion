from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from .database import db, init_database
from .jwt_auth import init_jwt
from app.routes.project_routes import projects_bp
from app.routes.request_routes import request_bp
from app.routes.commitment_routes import commitment_bp
from app.routes.auth_routes import auth_bp
from app import seeds_data
from flasgger import Swagger
import yaml
import os
import click


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    allowed_origins = app.config.get("CORS_ALLOWED_ORIGINS", [
        "http://localhost:3000",
        "http://localhost:8080"
    ])
    CORS(app, resources={r"/*": {"origins": "*"}})

    init_database(app)
    init_jwt(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(projects_bp, url_prefix="/api/proyectos")
    app.register_blueprint(request_bp, url_prefix="/api/pedidos")
    app.register_blueprint(commitment_bp, url_prefix="/api/compromisos")

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
    }

    swagger_path = os.path.join(os.path.dirname(__file__), "static", "swagger.yaml")
    with open(swagger_path, "r", encoding="utf-8") as f:
        swagger_template = yaml.safe_load(f)

    Swagger(app, config=swagger_config, template=swagger_template)

    seeds_data.init_app(app)

    @app.route("/")
    def home():
        return jsonify({"status": "ok", "message": "API Colaboración funcionando"})

    @app.cli.command("reset-db")
    @click.option('--yes', is_flag=True, help='Skip confirmation prompt')
    def reset_db_cli(yes):
        """Drop all tables, recreate them and load seeds_data.

        Usage:
          flask reset-db
          flask reset-db --yes
        """
        if not yes:
            confirm = click.confirm('This will DROP ALL TABLES and reload seeds. Continue?')
            if not confirm:
                click.echo('Aborted.')
                return

        click.echo('Resetting database...')
        try:
            with app.app_context():
                db.drop_all()
                db.create_all()
                seeds_data.init_app(app)
            click.echo('Database reset and seeds loaded successfully.')
        except Exception as e:
            click.echo(f'Error resetting database: {e}')
            raise

    return app
