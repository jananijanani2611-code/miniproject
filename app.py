from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

sos_alerts = []  # temporary storage

@app.route("/sos", methods=["GET", "POST"])
def sos():
    if request.method == "POST":
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        sos_alerts.append({
            "location": f"{lat}, {lon}",
            "status": "ACTIVE"
        })

        return redirect(url_for("dashboard"))

    return render_template("sos.html")

@app.route("/admin/sos")
def admin_sos():
    return render_template("admin_sos.html", alerts=sos_alerts)


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
