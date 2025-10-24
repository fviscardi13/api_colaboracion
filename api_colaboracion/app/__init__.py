from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from .database import db
from .jwt_auth import init_jwt
from app.routes.project_routes import projects_bp
from app.routes.request_routes import request_bp
from app.routes.commitment_routes import commitment_bp
from app.routes.auth_routes import auth_bp
from app import seeds_data
from flasgger import Swagger
import yaml
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    allowed_origins = app.config.get("CORS_ALLOWED_ORIGINS", [
        "http://localhost:3000",
        "http://localhost:8080"
    ])
    CORS(app, resources={r"/*": {"origins": "*"}})

    db.init_app(app)
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

    return app
