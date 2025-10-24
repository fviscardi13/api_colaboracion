from app.database import db

class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    ong_id = db.Column(db.Integer, db.ForeignKey("ongs.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float)
    assigned = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    commitments = db.relationship("Commitment", backref="request", cascade="all, delete-orphan")