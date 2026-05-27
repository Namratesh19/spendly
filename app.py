from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from database.db import init_db, seed_db, get_user_by_email, create_user

app = Flask(__name__)
app.secret_key = "spendly-secret-key-change-this-in-production"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required")

        if get_user_by_email(email):
            return render_template("register.html", error="Email already registered")

        hashed_pw = generate_password_hash(password)
        create_user(name, email, hashed_pw)
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))
        return render_template("login.html", error="Invalid email or password")
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")




# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

with app.app_context():
    init_db()
    seed_db()

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "joined": "May 2026",
        "initials": "DU"
    }

    stats = {
        "total_spent": "₹18,240",
        "transactions": 34,
        "top_category": "Food"
    }

    transactions = [
        {"date": "2026-05-20", "desc": "Grocery Store", "cat": "Food", "amt": "₹1,200.00"},
        {"date": "2026-05-18", "desc": "Uber Ride", "cat": "Transport", "amt": "₹450.00"},
        {"date": "2026-05-15", "desc": "Netflix Subscription", "cat": "Entertainment", "amt": "₹499.00"},
        {"date": "2026-05-12", "desc": "Starbucks Coffee", "cat": "Food", "amt": "₹350.00"},
        {"date": "2026-05-10", "desc": "Gym Membership", "cat": "Health", "amt": "₹2,000.00"},
    ]

    categories = [
        {"name": "Food", "spent": "₹5,400", "pct": 30},
        {"name": "Transport", "spent": "₹3,200", "pct": 18},
        {"name": "Entertainment", "spent": "₹4,100", "pct": 22},
        {"name": "Health", "spent": "₹5,540", "pct": 30},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
