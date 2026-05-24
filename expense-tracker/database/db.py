import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = "spendly.db"

def get_db():
    """
    Opens a connection to the SQLite database and configures it.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Creates the users and expenses tables if they don't already exist.
    """
    conn = get_db()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
    finally:
        conn.close()

def seed_db():
    """
    Inserts a demo user and sample expenses if the database is empty.
    """
    conn = get_db()
    try:
        # Check if data already exists
        user_exists = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
        if user_exists:
            return

        with conn:
            # Insert demo user
            demo_user_password = generate_password_hash("demo123")
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Demo User", "demo@spendly.com", demo_user_password)
            )
            user_id = cursor.lastrowid

            # Insert 8 sample expenses
            expenses = [
                (user_id, 15.50, "Food", "2026-05-01", "Lunch"),
                (user_id, 10.00, "Transport", "2026-05-02", "Bus ticket"),
                (user_id, 120.00, "Bills", "2026-05-03", "Internet"),
                (user_id, 45.00, "Health", "2026-05-04", "Pharmacy"),
                (user_id, 20.00, "Entertainment", "2026-05-05", "Cinema"),
                (user_id, 60.00, "Shopping", "2026-05-06", "Clothing"),
                (user_id, 5.00, "Other", "2026-05-07", "Parking"),
                (user_id, 25.00, "Food", "2026-05-08", "Dinner"),
            ]
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
    finally:
        conn.close()
