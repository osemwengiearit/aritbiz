from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///aritbiz.db")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hash_pw = generate_password_hash(password)

        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            hash_pw
        )

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            username
        )

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Invalid login"

        session["user_id"] = rows[0]["id"]

        return redirect("/clients")

    return render_template("login.html")


@app.route("/clients")
def clients():
    clients = db.execute("SELECT * FROM clients")
    return render_template("clients.html", clients=clients)


@app.route("/projects")
def projects():
    projects = db.execute("SELECT * FROM projects")
    return render_template("projects.html", projects=projects)


@app.route("/invoices")
def invoices():
    invoices = db.execute("SELECT * FROM invoices")
    return render_template("invoices.html", invoices=invoices)


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


if __name__ == "__main__":
    app.run(debug=True)