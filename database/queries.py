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


def get_category_breakdown(user_id, start_date=None, end_date=None):
    """
    Returns a breakdown of spending by category for a user.
    Returns a list of dicts: [{"name": str, "amount": float, "pct": int}, ...]
    """
    conn = get_db()
    try:
        # Build dynamic WHERE clause
        where_clause = "WHERE user_id = ?"
        params = [user_id]
        if start_date:
            where_clause += " AND date >= ?"
            params.append(start_date)
        if end_date:
            where_clause += " AND date <= ?"
            params.append(end_date)

        # Get total sum per category, ordered by sum descending
        rows = conn.execute(
            f"SELECT category, SUM(amount) as total FROM expenses {where_clause} GROUP BY category ORDER BY total DESC",
            params
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


def get_summary_stats(user_id, start_date=None, end_date=None):
    """
    Calculates summary statistics for a user's expenses.
    Returns a dict with total_spent, transaction_count, and top_category.
    """
    conn = get_db()
    try:
        # Build dynamic WHERE clause
        where_clause = "WHERE user_id = ?"
        params = [user_id]
        if start_date:
            where_clause += " AND date >= ?"
            params.append(start_date)
        if end_date:
            where_clause += " AND date <= ?"
            params.append(end_date)

        # Get total spent and total transactions
        totals = conn.execute(
            f"SELECT SUM(amount) as total_spent, COUNT(*) as transaction_count FROM expenses {where_clause}",
            params
        ).fetchone()

        total_spent = totals["total_spent"] or 0.0
        transaction_count = totals["transaction_count"] or 0

        # Get top category by amount spent
        top_cat_row = conn.execute(
            f"SELECT category FROM expenses {where_clause} GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            params
        ).fetchone()

        top_category = top_cat_row["category"] if top_cat_row else "—"

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category
        }
    finally:
        conn.close()

def get_recent_transactions(user_id, limit=10, start_date=None, end_date=None):
    """
    Retrieves the most recent transactions for a user.
    """
    conn = get_db()
    try:
        # Build dynamic WHERE clause
        where_clause = "WHERE user_id = ?"
        params = [user_id]
        if start_date:
            where_clause += " AND date >= ?"
            params.append(start_date)
        if end_date:
            where_clause += " AND date <= ?"
            params.append(end_date)

        cursor = conn.execute(
            f"SELECT date, description, category, amount FROM expenses {where_clause} ORDER BY date DESC LIMIT ?",
            params + [limit]
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
