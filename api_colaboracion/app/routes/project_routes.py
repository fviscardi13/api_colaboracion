from flask import Blueprint, json, jsonify, request
from app.database import db
from app.models.project_model import Project, WorkPlan, EconomicPlan
from flask_jwt_extended import jwt_required, get_jwt
from app.jwt_auth import bonita_required
from datetime import date
from sqlalchemy.exc import IntegrityError

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


# --- Work Plans endpoints ---
@projects_bp.route("/<int:project_id>/work-plans", methods=["GET"])
@jwt_required()
@bonita_required
def get_work_plans(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": f"No existe un proyecto con ID {project_id}"}), 404

    plans = WorkPlan.query.filter_by(project_id=project_id).all()
    def serialize_wp(p):
        return {
            "id": p.id,
            "name": p.name,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "status": p.status
        }

    return jsonify([serialize_wp(p) for p in plans]), 200


@projects_bp.route("/<int:project_id>/work-plans", methods=["POST"])
@jwt_required()
@bonita_required
def create_work_plan(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": f"No existe un proyecto con ID {project_id}"}), 404

    payload = request.get_json(force=True)
    # Validaciones básicas
    name = payload.get("name")
    start_raw = payload.get("start_date")
    end_raw = payload.get("end_date")
    status = payload.get("status", "pendiente")

    if not name or not start_raw or not end_raw:
        return jsonify({"msg": "Faltan campos requeridos: 'name', 'start_date', 'end_date'"}), 400

    try:
        # esperar ISO format 'YYYY-MM-DD'
        start_date = date.fromisoformat(start_raw)
        end_date = date.fromisoformat(end_raw)
    except Exception:
        return jsonify({"msg": "Fechas inválidas. Usar formato 'YYYY-MM-DD'."}), 400

    if start_date > end_date:
        return jsonify({"msg": "'start_date' no puede ser posterior a 'end_date'."}), 400

    try:
        wp = WorkPlan(
            name=name,
            start_date=start_date,
            end_date=end_date,
            status=status,
            project_id=project_id
        )
        db.session.add(wp)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"msg": f"Error de integridad al crear work plan: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error creando work plan: {str(e)}"}), 500

    return jsonify({"msg": "Work plan creado correctamente", "id": wp.id}), 201


# --- Economic Plans endpoints ---
@projects_bp.route("/<int:project_id>/economic-plans", methods=["GET"])
@jwt_required()
@bonita_required
def get_economic_plans(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": f"No existe un proyecto con ID {project_id}"}), 404

    plans = EconomicPlan.query.filter_by(project_id=project_id).all()
    return jsonify([{"id": p.id, "type": p.type, "amount": p.amount, "description": p.description} for p in plans]), 200


@projects_bp.route("/<int:project_id>/economic-plans", methods=["POST"])
@jwt_required()
@bonita_required
def create_economic_plan(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": f"No existe un proyecto con ID {project_id}"}), 404

    payload = request.get_json(force=True)
    plan_type = payload.get("type")
    amount = payload.get("amount")
    description = payload.get("description")

    allowed_types = ("económico", "materiales", "mano_obra", "técnico", "otro")
    if plan_type not in allowed_types:
        return jsonify({"msg": f"Tipo inválido. Debe ser uno de: {', '.join(allowed_types)}"}), 400

    try:
        amount = float(amount)
    except Exception:
        return jsonify({"msg": "'amount' inválido. Debe ser numérico."}), 400

    if not description:
        return jsonify({"msg": "'description' es requerido."}), 400

    try:
        ep = EconomicPlan(
            type=plan_type,
            amount=amount,
            description=description,
            project_id=project_id
        )
        db.session.add(ep)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"msg": f"Error de integridad al crear economic plan: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error creando economic plan: {str(e)}"}), 500

    return jsonify({"msg": "Economic plan creado correctamente", "id": ep.id}), 201


