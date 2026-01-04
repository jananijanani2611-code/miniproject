from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, "database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# ================= MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))  # tourist / admin

class SOS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    status = db.Column(db.String(20), default="SENT")
    time = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("home.html")

# ---------- Tourist Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, role="tourist").first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/dashboard")

    return render_template("login.html")

# ---------- Tourist Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(name=name, email=email, password=password, role="tourist")
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

# ---------- Admin Login ----------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        admin = User.query.filter_by(email=email, role="admin").first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect("/admin/dashboard")

    return render_template("admin_login.html")

# ---------- Dashboard ----------
@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "tourist":
        return redirect("/")
    return render_template("dashboard.html")

# ---------- Map ----------
@app.route("/map")
def map_page():
    return render_template("map.html")


# ---------- SOS ----------
@app.route("/sos", methods=["GET", "POST"])
@login_required
def sos():
    if request.method == "POST":
        data = request.json
        alert = SOS(
            user_id=current_user.id,
            lat=data["lat"],
            lng=data["lng"]
        )
        db.session.add(alert)
        db.session.commit()
        return jsonify({"status": "sent"})

    return render_template("sos.html")

# ---------- Admin Dashboard ----------
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect("/")
    alerts = SOS.query.all()
    return render_template("admin_sos.html", alerts=alerts)

# ---------- Logout ----------
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/how-to-use")
def how_to_use():
    return render_template("how_to_use.html")



# ================= INIT =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(role="admin").first():
            admin = User(
                name="Admin",
                email="admin@smart.com",
                password=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
