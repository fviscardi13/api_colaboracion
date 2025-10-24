from app.database import db
from sqlalchemy import Enum

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    ong_id = db.Column(db.Integer, db.ForeignKey("ongs.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    neighborhood = db.Column(db.String(80), nullable=False)
    bonita_case_id = db.Column(db.String(50), nullable=True)

    work_plans = db.relationship('WorkPlan', backref='project', cascade="all, delete-orphan")
    economic_plans = db.relationship('EconomicPlan', backref='project', cascade="all, delete-orphan")
    requests = db.relationship('Request', backref='project', cascade="all, delete-orphan")

class WorkPlan(db.Model):
    __tablename__ = 'work_plans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default="pendiente")
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

class EconomicPlan(db.Model):
    __tablename__ = 'economic_plans'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(
        Enum('económico', 'materiales', 'mano_obra', 'técnico', 'otro', name='coverage_type_enum'),
        nullable=False
    )
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)