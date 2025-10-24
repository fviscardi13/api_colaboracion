from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt
from flask import jsonify
from functools import wraps
import os

jwt = JWTManager()

def init_jwt(app):
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt_super_secret_key")
    jwt.init_app(app)

def generate_service_token():
    return create_access_token(identity="bonita_service", additional_claims={"service":"bonita"})

def bonita_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        # Allow internal service tokens OR user tokens that include a 'bonita_user' claim
        # Tokens created at /api/auth/token include additional_claims: 'bonita_user' and 'role': 'ong'
        if (
            claims.get("service") == "bonita" or
            claims.get("sub") == "bonita_service" or
            claims.get("bonita_user") is not None or
            claims.get("role") == "ong"
        ):
            return fn(*args, **kwargs)

        return jsonify({"msg": "Acceso restringido: token no válido para Bonita"}), 403
    return wrapper

