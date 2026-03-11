from db_ext import db
from datetime import datetime

# ---------------- USER MODEL ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="tourist")  # tourist / admin

# ---------------- SOS MODEL ----------------
class SOS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20))
    message = db.Column(db.String(255))
    block_hash = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    

class AIReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    location = db.Column(db.String(200))
    risk_level = db.Column(db.String(50))   # Low / Medium / High
    risk_score = db.Column(db.Float)         # e.g. 0.82
    report_text = db.Column(db.Text)         # ✨ NEW: Full paragraph report
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="ai_reports")

    user = db.relationship("User", backref="ai_reports")
    
# ---------------- RISK ZONE MODEL ----------------
class RiskZone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    risk = db.Column(db.String(20))  # safe / warning / danger

