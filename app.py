from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///aritbiz.db")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("All fields required")
            return redirect("/register")

        existing = db.execute("SELECT * FROM users WHERE username = ?", username)

        if existing:
            flash("Username already exists")
            return redirect("/register")

        hash_pw = generate_password_hash(password)

        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            hash_pw
        )

        flash("Registration successful")
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            username
        )

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid login")
            return redirect("/login")

        session["user_id"] = rows[0]["id"]

        return redirect("/clients")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/clients", methods=["GET", "POST"])
@login_required
def clients():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        db.execute(
            "INSERT INTO clients (name, email) VALUES (?, ?)",
            name,
            email
        )

        return redirect("/clients")

    clients = db.execute("SELECT * FROM clients")
    return render_template("clients.html", clients=clients)


@app.route("/projects")
@login_required
def projects():
    projects = db.execute("SELECT * FROM projects")
    return render_template("projects.html", projects=projects)


@app.route("/invoices", methods=["GET", "POST"])
@login_required
def invoices():
    if request.method == "POST":
        client = request.form.get("client")
        amount = request.form.get("amount")

        db.execute(
            "INSERT INTO invoices (user_id, client, amount, status) VALUES (?, ?, ?, ?)",
            session["user_id"],
            client,
            amount,
            "Pending"
        )

        return redirect("/invoices")

    invoices = db.execute("SELECT * FROM invoices WHERE user_id = ?", session["user_id"])
    return render_template("invoices.html", invoices=invoices)


@app.route("/analytics")
@login_required
def analytics():
    total_clients = db.execute(
        "SELECT COUNT(*) as count FROM clients"
    )[0]["count"]

    total_invoices = db.execute(
        "SELECT COUNT(*) as count FROM invoices"
    )[0]["count"]

    revenue = db.execute(
        "SELECT SUM(amount) as total FROM invoices"
    )[0]["total"]

    if revenue is None:
        revenue = 0

    return render_template(
        "analytics.html",
        total_clients=total_clients,
        total_invoices=total_invoices,
        total_revenue=revenue
    )