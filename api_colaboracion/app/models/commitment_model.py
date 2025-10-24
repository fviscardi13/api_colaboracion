from app.database import db

class Commitment(db.Model):
    __tablename__ = "commitments"
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    ong_name = db.Column(db.String(120))
    help_type = db.Column(db.String(100))
    accepted = db.Column(db.Boolean, default=False)
    fulfilled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())