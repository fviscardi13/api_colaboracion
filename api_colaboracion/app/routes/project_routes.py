from flask import Blueprint, json, jsonify, request
from app.database import db
from app.models.project_model import Project, WorkPlan, EconomicPlan
from flask_jwt_extended import jwt_required, get_jwt
from app.jwt_auth import bonita_required

projects_bp = Blueprint("projects", __name__)

@projects_bp.route("/", methods=["GET"])
@jwt_required()
@bonita_required
def get_projects():
    projects = Project.query.all()

    def project_compact(p):
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "type": p.type,
            "country": p.country,
            "neighborhood": p.neighborhood
        }

    return jsonify([project_compact(p) for p in projects])

@projects_bp.route("/", methods=["POST"])
@jwt_required()
@bonita_required
def create_project():
    raw = request.get_data(as_text=True)
    try:
        data = json.loads(raw)
        if isinstance(data, str):
            data = json.loads(data)
    except:
        data = request.get_json(force=True)

    claims = get_jwt()
    ong_id = claims.get("ong_id")

    if not ong_id:
        return jsonify({"msg": "Token no contiene 'ong_id'. Autenticación de ONG requerida."}), 400

    project = Project(
        ong_id=ong_id,
        name=data["name"],
        description=data["description"],
        type=data["type"],
        country=data["country"],
        neighborhood=data["neighborhood"],
        bonita_case_id=data.get("bonita_case_id")
    )
    db.session.add(project)
    db.session.commit()

    return jsonify({"msg": "Proyecto creado correctamente", "id": project.id}), 201
