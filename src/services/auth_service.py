# src/services/auth_service.py
import bcrypt
from src.services.db import get_conn

def create_user(username: str, password: str, role: str = "student") -> bool:
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )
            conn.commit()
        return True
    except Exception:
        return False

def authenticate(username: str, password: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if not row:
        return None

    user_id, uname, password_hash, role = row
    if bcrypt.checkpw(password.encode("utf-8"), password_hash):
        return {"id": user_id, "username": uname, "role": role}

    return None
