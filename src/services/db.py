# src/services/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/app.db")

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
