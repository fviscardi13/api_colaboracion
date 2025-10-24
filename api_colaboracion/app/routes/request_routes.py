from flask import Blueprint, jsonify, request
from app.database import db
from app.models.request_model import Request
from flask_jwt_extended import jwt_required
from app.jwt_auth import bonita_required

request_bp = Blueprint("requests", __name__)

@request_bp.route("/", methods=["GET"])
@jwt_required()
@bonita_required
def get_requests():
    reqs = Request.query.all()
    return jsonify([{
        "id": r.id,
        "type": r.type,
        "description": r.description,
        "project_id": r.project_id,
        "amount": r.amount,
        "assigned": r.assigned,
        "completed": r.completed
    } for r in reqs])

@request_bp.route("/", methods=["POST"])
@jwt_required()
@bonita_required
def create_request():
    data = request.get_json()
    new_req = Request(
        project_id=data["project_id"],
        type=data["type"],
        description=data.get("description"),
        amount=data.get("amount")
    )
    db.session.add(new_req)
    db.session.commit()
    return jsonify({"msg": "Pedido de cobertura creado", "id": new_req.id}), 201

@request_bp.route("/proyecto/<int:project_id>/no-asignados", methods=["GET"])
@jwt_required()
@bonita_required
def get_unassigned_requests(project_id):
    reqs = Request.query.filter_by(project_id=project_id, assigned=False).all()
    return jsonify([{
        "id": r.id,
        "type": r.type,
        "description": r.description,
        "amount": r.amount
    } for r in reqs])

@request_bp.route("/<int:id>/terminar", methods=["PATCH"])
@jwt_required()
@bonita_required
def mark_request_done(id):
    req = Request.query.get_or_404(id)
    req.completed = True
    db.session.commit()
    return jsonify({"msg": "Pedido marcado como terminado"})
