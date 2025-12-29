from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- TOURIST ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route("/sos", methods=["GET", "POST"])
def sos():
    return render_template("sos.html")

# ---------------- ADMIN ----------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    alerts = [
        {"lat": 13.0827, "lng": 80.2707},
        {"lat": 13.0674, "lng": 80.2376}
    ]
    return render_template("admin_dashboard.html", alerts=alerts)

@app.route("/admin/sos")
def admin_sos():
    return render_template("admin_sos.html")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
