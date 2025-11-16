from flask import Blueprint, jsonify, request
from app.models.project_model import Project, WorkPlan, EconomicPlan
from app.database import db
from app.models.request_model import Request
from flask_jwt_extended import jwt_required, get_jwt
from app.jwt_auth import bonita_required
import json

request_bp = Blueprint("requests", __name__)

def parse_json_payload():
    raw = request.get_data(as_text=True)
    try:
        data = json.loads(raw)
        if isinstance(data, str):
            data = json.loads(data)
        return data
    except Exception:
        return request.get_json(force=True)


def create_full_project(project_data, ong_id):
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

    for wp in project_data.get("work_plans", []):
        db.session.add(WorkPlan(
            name=wp["name"],
            start_date=wp["start_date"],
            end_date=wp["end_date"],
            status="pendiente",
            project_id=project.id
        ))

    for ep in project_data.get("economic_plans", []):
        db.session.add(EconomicPlan(
            type=ep["type"],
            amount=ep["amount"],
            description=ep["description"],
            project_id=project.id
        ))

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
        return jsonify({"msg": "Token no contiene 'ong_id'. Autenticación requerida."}), 400

    project_id = data.get("project_id")
    if project_id is None:
        return jsonify({"msg": "Debe enviarse 'project_id'."}), 400

    if Project.query.get(project_id):
        return jsonify({
            "msg": f"Ya existe un proyecto con ID {project_id}. No se pueden duplicar project_id."
        }), 400

    project_data = data.get("project")
    if not project_data:
        return jsonify({"msg": "Debe enviarse el objeto 'project'."}), 400

    project = Project(
        id=project_id,
        ong_id=ong_id,
        name=project_data.get("name"),
        description=project_data.get("description"),
        type=project_data.get("type"),
        country=project_data.get("country"),
        neighborhood=project_data.get("neighborhood"),
        bonita_case_id=project_data.get("bonita_case_id")
    )
    db.session.add(project)

    for wp in project_data.get("work_plans", []):
        db.session.add(WorkPlan(
            project_id=project_id,
            name=wp["name"],
            start_date=wp["start_date"],
            end_date=wp["end_date"],
            status="pendiente"
        ))

    for ep in project_data.get("economic_plans", []):
        db.session.add(EconomicPlan(
            project_id=project_id,
            type=ep["type"],
            amount=ep["amount"],
            description=ep["description"]
        ))

    wp_list = project_data.get("work_plans", [])
    wp_selected = wp_list[0] if wp_list else None

    wp_name = wp_selected["name"] if wp_selected else None
    wp_start = wp_selected["start_date"] if wp_selected else None
    wp_end = wp_selected["end_date"] if wp_selected else None


    new_req = Request(
        project_id=project_id,
        ong_id=ong_id,
        type=data.get("type"),
        description=data.get("description"),
        amount=data.get("amount"),
        wp_name=wp_name,
        wp_start_date=wp_start,
        wp_end_date=wp_end
    )

    db.session.add(new_req)
    db.session.commit()

    return jsonify({
        "msg": "Proyecto y pedido creados correctamente",
        "request_id": new_req.id,
        "project_id": project_id,
        "work_plan_stored": {
            "name": wp_name,
            "start_date": wp_start,
            "end_date": wp_end
        }
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
