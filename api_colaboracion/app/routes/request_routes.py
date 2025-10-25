from flask import Blueprint, jsonify, request
from app.models.project_model import Project
from app.database import db
from app.models.request_model import Request
from flask_jwt_extended import jwt_required
from app.jwt_auth import bonita_required
from flask_jwt_extended import get_jwt

request_bp = Blueprint("requests", __name__)

@request_bp.route("/", methods=["POST"])
@jwt_required()
@bonita_required
def create_request():
    data = request.get_json()
    claims = get_jwt()
    ong_id = claims.get("ong_id")

    if not ong_id:
        return jsonify({"msg": "Token no contiene 'ong_id'. Autenticación de ONG requerida."}), 400

    project_id = data.get("project_id")
    if not project_id:
        return jsonify({"msg": "Debe especificarse el 'project_id'."}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": f"No existe un proyecto con ID {project_id}."}), 404

    existing_request = Request.query.filter_by(project_id=project_id).first()
    if existing_request:
        return jsonify({
            "msg": f"El proyecto con ID {project_id} ya tiene un pedido de colaboración asignado (ID: {existing_request.id})."
        }), 400

    new_req = Request(
        project_id=project_id,
        ong_id=ong_id,
        type=data["type"],
        description=data.get("description"),
        amount=data.get("amount")
    )

    db.session.add(new_req)
    db.session.commit()

    return jsonify({
        "msg": f"Pedido de colaboración creado correctamente para el proyecto {project_id}.",
        "id": new_req.id
    }), 201

@request_bp.route("/proyecto/<int:project_id>/no-asignados", methods=["GET"])
@jwt_required()
@bonita_required
def get_unassigned_requests(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({
            "msg": f"No existe un proyecto con ID {project_id}"
        }), 404

    reqs = Request.query.filter_by(project_id=project_id, assigned=False).all()

    if not reqs:
        return jsonify({
            "msg": "El proyecto existe pero no tiene pedidos no asignados.",
            "requests": []
        }), 200

    return jsonify({
        "msg": f"Pedidos no asignados del proyecto {project_id}",
        "requests": [{
            "id": r.id,
            "type": r.type,
            "description": r.description,
            "amount": r.amount
        } for r in reqs]
    }), 200
