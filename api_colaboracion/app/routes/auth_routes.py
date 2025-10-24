from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.database import db
from app.models.ong_model import ONG
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/token", methods=["POST"])
def get_token():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    bonita_user = data.get("bonita_user")
    if not email or not password or not bonita_user:
        return jsonify({"msg": "email, password y bonita_user son obligatorios"}), 400

    ong = ONG.query.filter_by(email=email).first()
    if not ong or not ong.check_password(password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    additional_claims = {"role": "ong", "ong_id": ong.id, "bonita_user": bonita_user}
    access_token = create_access_token(
        identity=ong.email,
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=4)
    )
    return jsonify({"access_token": access_token}), 200
