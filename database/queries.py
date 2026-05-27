import sqlite3
from database.db import get_db
from datetime import datetime

def get_user_by_id(user_id):
    """
    Retrieves user profile information by ID.
    Returns a dict with name, email, and formatted member_since date.
    """
    conn = get_db()
    try:
        user = conn.execute("SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return None

        # Format created_at (ISO string) to "Month YYYY"
        dt = datetime.fromisoformat(user["created_at"])
        member_since = dt.strftime("%B %Y")

        return {
            "name": user["name"],
            "email": user["email"],
            "member_since": member_since
        }
    finally:
        conn.close()


def get_category_breakdown(user_id):
    """
    Returns a breakdown of spending by category for a user.
    Returns a list of dicts: [{"name": str, "amount": float, "pct": int}, ...]
    """
    conn = get_db()
    try:
        # Get total sum per category, ordered by sum descending
        rows = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
            (user_id,)
        ).fetchall()

        if not rows:
            return []

        total_spent = sum(row["total"] for row in rows)
        breakdown = []
        sum_pct = 0

        for row in rows:
            amount = row["total"]
            # Round to nearest int
            pct = int(round((amount / total_spent) * 100)) if total_spent > 0 else 0
            breakdown.append({"name": row["category"], "amount": amount, "pct": pct})
            sum_pct += pct

        # Adjust the largest category to ensure sum of pct is exactly 100
        if breakdown and sum_pct != 100:
            diff = 100 - sum_pct
            breakdown[0]["pct"] += diff

        return breakdown
    finally:
        conn.close()


def get_summary_stats(user_id):
    """
    Calculates summary statistics for a user's expenses.
    Returns a dict with total_spent, transaction_count, and top_category.
    """
    conn = get_db()
    try:
        # Get total spent and total transactions
        totals = conn.execute(
            "SELECT SUM(amount) as total_spent, COUNT(*) as transaction_count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        total_spent = totals["total_spent"] or 0.0
        transaction_count = totals["transaction_count"] or 0

        # Get top category by amount spent
        top_cat_row = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,)
        ).fetchone()

        top_category = top_cat_row["category"] if top_cat_row else "—"

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category
        }
    finally:
        conn.close()

def get_recent_transactions(user_id, limit=10):
    """
    Retrieves the most recent transactions for a user.
    """
    conn = get_db()
    try:
        cursor = conn.execute(
            "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?",
            (user_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
