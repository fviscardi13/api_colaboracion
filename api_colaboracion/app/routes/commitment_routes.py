from flask import Blueprint, jsonify, request
from app.database import db
from app.models.request_model import Request
from app.models.commitment_model import Commitment
from flask_jwt_extended import jwt_required
from app.jwt_auth import bonita_required

commitment_bp = Blueprint("commitments", __name__)

@commitment_bp.route("/", methods=["GET"])
@jwt_required()
@bonita_required
def get_commitments():
    commitments = Commitment.query.all()

    if not commitments:
        return jsonify({
            "msg": "No hay compromisos registrados actualmente.",
            "commitments": []
        }), 200

    return jsonify({
        "msg": "Lista de compromisos registrados",
        "commitments": [{
            "id": c.id,
            "request_id": c.request_id,
            "ong_name": c.ong_name,
            "help_type": c.help_type,
            "fulfilled": c.fulfilled
        } for c in commitments]
    }), 200

@commitment_bp.route("/", methods=["POST"])
@jwt_required()
@bonita_required
def create_commitment():
    data = request.get_json()
    request_obj = Request.query.get(data["request_id"])
    if not request_obj:
        return jsonify({
            "msg": f"No existe un pedido de colaboración con ID {data['request_id']}"
        }), 404
    existing_commitment = Commitment.query.filter_by(request_id=data["request_id"]).first()
    if existing_commitment:
        return jsonify({
            "msg": f"El pedido con ID {data['request_id']} ya tiene un compromiso registrado."
        }), 400

    new_commitment = Commitment(
        request_id=data["request_id"],
        ong_name=data["ong_name"],
        help_type=data["help_type"],
        accepted=True
    )

    db.session.add(new_commitment)
    db.session.commit()
    return jsonify({
        "msg": "Compromiso registrado correctamente",
        "id": new_commitment.id
    }), 201

@commitment_bp.route("/<int:id>/cumplido", methods=["PATCH"])
@jwt_required()
@bonita_required
def mark_fulfilled(id):
    commitment = Commitment.query.get(id)
    if not commitment:
        return jsonify({"msg": f"No existe un compromiso con ID {id}"}), 404

    if commitment.fulfilled:
        return jsonify({"msg": f"El compromiso con ID {id} ya está marcado como cumplido"}), 400

    commitment.fulfilled = True
    db.session.commit()
    return jsonify({"msg": "Compromiso marcado como cumplido"}), 200
