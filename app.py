from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from database.db import init_db, seed_db, get_user_by_email, create_user
from database.queries import get_category_breakdown, get_summary_stats, get_recent_transactions, get_user_by_id

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

    user_id = session["user_id"]
    user_data = get_user_by_id(user_id)

    if not user_data:
        return redirect(url_for("login"))

    # Get date filters from request arguments
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    user = {
        "name": user_data["name"],
        "email": user_data["email"],
        "joined": user_data["member_since"],
        "initials": user_data["name"][0:2].upper() if user_data["name"] else "U"
    }

    stats_data = get_summary_stats(user_id, start_date, end_date)
    stats = {
        "total_spent": f"₹{stats_data['total_spent']:,.2f}",
        "transactions": stats_data["transaction_count"],
        "top_category": stats_data["top_category"]
    }

    transactions = [
        {
            "date": tx["date"],
            "desc": tx["description"],
            "cat": tx["category"],
            "amt": f"₹{tx['amount']:,.2f}"
        }
        for tx in get_recent_transactions(user_id, start_date=start_date, end_date=end_date)
    ]

    categories = [
        {"name": cat["name"], "spent": f"₹{cat['amount']:,.2f}", "pct": cat["pct"]}
        for cat in get_category_breakdown(user_id, start_date, end_date)
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
        start_date=start_date,
        end_date=end_date
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
