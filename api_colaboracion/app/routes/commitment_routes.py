from flask import Blueprint, jsonify, request
from app.database import db
from app.models.commitment_model import Commitment
from flask_jwt_extended import jwt_required
from app.jwt_auth import bonita_required

commitment_bp = Blueprint("commitments", __name__)

@commitment_bp.route("/", methods=["GET"])
@jwt_required()
@bonita_required
def get_commitments():
    commitments = Commitment.query.all()
    return jsonify([{
        "id": c.id,
        "request_id": c.request_id,
        "ong_name": c.ong_name,
        "help_type": c.help_type,
        "fulfilled": c.fulfilled
    } for c in commitments])

@commitment_bp.route("/", methods=["POST"])
@jwt_required()
@bonita_required
def create_commitment():
    data = request.get_json()
    new_commitment = Commitment(
        request_id=data["request_id"],
        ong_name=data["ong_name"],
        help_type=data["help_type"],
        accepted=True
    )
    db.session.add(new_commitment)
    db.session.commit()
    return jsonify({"msg": "Compromiso registrado correctamente"}), 201

@commitment_bp.route("/<int:id>/cumplido", methods=["PATCH"])
@jwt_required()
@bonita_required
def mark_fulfilled(id):
    commitment = Commitment.query.get_or_404(id)
    commitment.fulfilled = True
    db.session.commit()
    return jsonify({"msg": "Compromiso marcado como cumplido ✅"})
