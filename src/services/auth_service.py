"""
Authentication service for user management and login verification.

Provides functions to create users with secure password hashing and authenticate
existing users by validating credentials against stored hashes.
"""
import bcrypt
from src.services.db import get_conn

def create_user(username: str, password: str, role: str = "student") -> bool:
    """Create a new user with the given username, password, and role. Returns True if successful."""
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
    """Authenticate a user by username and password. Returns user dict if successful, else None."""
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
