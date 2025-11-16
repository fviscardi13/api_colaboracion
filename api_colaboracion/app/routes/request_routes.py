from flask import Blueprint, jsonify, request
from app.models.project_model import Project, WorkPlan, EconomicPlan
from app.database import db
from app.models.request_model import Request
from flask_jwt_extended import jwt_required
from app.jwt_auth import bonita_required
from flask_jwt_extended import get_jwt
import json

request_bp = Blueprint("requests", __name__)


def parse_json_payload():
    """Permite recibir JSON normal o JSON como string."""
    raw = request.get_data(as_text=True)

    try:
        data = json.loads(raw)
        if isinstance(data, str):
            data = json.loads(data)
        return data
    except Exception:
        return request.get_json(force=True)


def create_full_project(project_data, ong_id):
    """Crea un proyecto completo con planes de trabajo y económicos."""
    project = Project(
        ong_id=ong_id,
        name=project_data["name"],
        description=project_data["description"],
        type=project_data["type"],
        country=project_data["country"],
        neighborhood=project_data["neighborhood"],
        bonita_case_id=project_data.get("bonita_case_id")
    )
    db.session.add(project)
    db.session.flush()

    if "work_plans" in project_data:
        for wp in project_data["work_plans"]:
            wp_obj = WorkPlan(
                name=wp["name"],
                start_date=wp["start_date"],
                end_date=wp["end_date"],
                status="pendiente",
                project_id=project.id
            )
            db.session.add(wp_obj)

    if "economic_plans" in project_data:
        for ep in project_data["economic_plans"]:
            ep_obj = EconomicPlan(
                type=ep["type"],
                amount=ep["amount"],
                description=ep["description"],
                project_id=project.id
            )
            db.session.add(ep_obj)

    db.session.commit()
    return project.id


@request_bp.route("/", methods=["POST"])
@jwt_required()
@bonita_required
def create_request():
    data = parse_json_payload()
    claims = get_jwt()
    ong_id = claims.get("ong_id")

    if not ong_id:
        return jsonify({"msg": "Token no contiene 'ong_id'. Autenticación de ONG requerida."}), 400

    if "project" not in data:
        return jsonify({"msg": "Debe enviarse un 'project' completo. Ya no se acepta 'project_id'."}), 400

    try:
        project_id = create_full_project(data["project"], ong_id)
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error creando proyecto completo: {str(e)}"}), 400

    existing_request = Request.query.filter_by(project_id=project_id).first()
    if existing_request:
        return jsonify({
            "msg": f"El proyecto con ID {project_id} ya tiene un pedido asignado (ID: {existing_request.id})."
        }), 400

    new_req = Request(
        project_id=project_id,
        ong_id=ong_id,
        type=data.get("type"),
        description=data.get("description"),
        amount=data.get("amount")
    )

    db.session.add(new_req)
    db.session.commit()

    return jsonify({
        "msg": "Pedido creado correctamente",
        "id": new_req.id,
        "project_id": project_id
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
