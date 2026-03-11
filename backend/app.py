from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import hashlib

from db_ext import db
from models import User, SOS, AIReport, RiskZone

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.secret_key = "super_secret_key_change_in_production"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ================ AI RISK CALCULATION ================
def calculate_risk(minutes_lost):
    """AI-based risk assessment"""
    if minutes_lost > 30:
        return "RED", "🔴 CRITICAL: Tourist in very dangerous zone. Immediate rescue needed!"
    elif minutes_lost > 10:
        return "YELLOW", "🟡 WARNING: Tourist in risky area. Monitor closely and prepare response."
    else:
        return "GREEN", "🟢 SAFE: Tourist location tracked. No immediate danger."


# ================ BLOCKCHAIN HASH GENERATION ================
def generate_hash(data):
    """Generate SHA-256 hash for blockchain integrity"""
    return hashlib.sha256(data.encode()).hexdigest()


# ================ HOME PAGE ================
@app.route("/")
def home():
    return render_template("home.html")


# ================ ABOUT PAGE ================
@app.route("/about")
def about():
    return render_template("about.html")


# ================ AI RISK INFO PAGE ================
@app.route("/risk")
def risk_info():
    return render_template("risk.html")


# ================ GUIDELINES PAGE ================
@app.route("/guidelines")
def guidelines():
    return render_template("guidelines.html")


# ================ USER REGISTRATION ================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered. Please login."

        # AUTO-GENERATE USERNAME
        username = email.split("@")[0]

        # CREATE USER OBJECT
        user = User(
            name=name,
            username=username,
            email=email,
            password=password,
            role="tourist"
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# ================ USER LOGIN ================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # Prevent admin from logging in through tourist login
            if user.role == "admin":
                return "Admin users must use /admin/login"
            
            session["user"] = user.email
            session["role"] = user.role
            return redirect(url_for("dashboard"))

        return "Invalid email or password. Please try again."

    return render_template("login.html")


# ================ TOURIST DASHBOARD ================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    if session.get("role") == "admin":
        return redirect(url_for("admin_sos"))
    
    return render_template("dashboard.html")


# ================ SOS PAGE (For Tourists) ================
@app.route("/sos")
def sos_page():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("sos.html")
# ================ PUBLIC MAP PAGE (No Login Required) ================
@app.route("/map")
def map_page():
    return render_template("map.html")

# ================ SOS API (Website + IoT Device) ================
@app.route("/api/sos", methods=["POST"])
def sos_api():
    """Receives SOS alerts from website or IoT devices"""
    data = request.json

    email = data.get("email")
    lat = data.get("lat")
    lon = data.get("lon")
    minutes_lost = data.get("minutes_lost", 0)
    
    # Calculate AI risk level
    risk, message = calculate_risk(minutes_lost)

    # Generate blockchain hash for data integrity
    timestamp = datetime.utcnow()
    raw_data = f"{email}|{lat}|{lon}|{timestamp}|{minutes_lost}"
    block_hash = generate_hash(raw_data)

    # Store SOS in database
    sos = SOS(
        user_email=email,
        latitude=lat,
        longitude=lon,
        risk_level=risk,
        message=message,
        block_hash=block_hash
    )

    db.session.add(sos)
    db.session.commit()

    # ✨ AUTO-GENERATE AI REPORT
    user = User.query.filter_by(email=email).first()
    
    if user:
        # Create AI Report
        ai_report = AIReport(
            user_id=user.id,
            location=f"Lat: {lat}, Lon: {lon}",
            risk_level="High" if risk == "RED" else ("Medium" if risk == "YELLOW" else "Low"),
            risk_score=0.95 if risk == "RED" else (0.65 if risk == "YELLOW" else 0.25)
        )
        
        db.session.add(ai_report)
        db.session.commit()

    return jsonify({
        "status": "SOS_RECEIVED",
        "risk": risk,
        "message": message,
        "sos_id": sos.id,
        "ai_report_generated": True,
        "timestamp": timestamp.isoformat(),
        "blockchain_hash": block_hash[:16] + "..."
    })


# ================ MAP DATA API ================
@app.route("/api/map-data")
def map_data():
    """Returns all SOS locations with risk levels"""
    sos_list = SOS.query.all()
    data = []

    for s in sos_list:
        data.append({
            "id": s.id,
            "lat": s.latitude,
            "lng": s.longitude,
            "risk": s.risk_level,
            "email": s.user_email,
            "time": s.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(data)


# ================ ADMIN LOGIN ================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        admin = User.query.filter_by(email=email, role="admin").first()

        if admin and check_password_hash(admin.password, password):
            session.clear()
            session["user"] = admin.email
            session["role"] = "admin"
            return redirect(url_for("admin_sos"))

        return "Invalid admin credentials. Access denied."

    return render_template("admin_login.html")


# ================ ADMIN SOS DASHBOARD ================
@app.route("/admin/sos")
def admin_sos():
    """Admin dashboard - Tourists CANNOT access this"""
    if session.get("role") != "admin":
        abort(403)

    sos_list = SOS.query.order_by(SOS.timestamp.desc()).all()
    return render_template("admin_sos.html", sos_list=sos_list)


# ================ ADMIN AI REPORTS ================
@app.route("/admin/ai-reports")
def admin_ai_reports():
    if session.get("role") != "admin":
        abort(403)

    reports = AIReport.query.order_by(AIReport.created_at.desc()).all()
    return render_template("admin_ai_reports.html", reports=reports)


# ================ LOGOUT ================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ================ ERROR HANDLERS ================
@app.errorhandler(403)
def forbidden(e):
    return """
    <h1>403 - Access Forbidden</h1>
    <p>You don't have permission to access this page.</p>
    <p>Tourists cannot access admin areas.</p>
    <p><a href="/">← Back to Home</a></p>
    """, 403


# ================ UTILITY: Create Admin Account ================
@app.route("/create-admin-secret")
def create_admin():
    """One-time route to create admin account"""
    admin_email = "admin@tourist.com"
    existing_admin = User.query.filter_by(email=admin_email).first()
    
    if existing_admin:
        return "✅ Admin already exists! Email: admin@tourist.com | Password: admin123"
    
    admin = User(
        name="Admin",
        username="admin",
        email=admin_email,
        password=generate_password_hash("admin123"),
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()
    
    return "✅ Admin created! Email: admin@tourist.com | Password: admin123"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)