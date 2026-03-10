import sqlite3
from pathlib import Path

DB_PATH = Path("data/app.db")


def get_connection():
    return sqlite3.connect(DB_PATH)

def create_progress_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_name TEXT,
            score REAL NOT NULL,
            total_questions INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def log_quiz_attempt(user_id, topic_name, score, total_questions):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO quiz_attempts (user_id, topic_name, score, total_questions)
        VALUES (?, ?, ?, ?)
    """, (user_id, topic_name, score, total_questions))

    conn.commit()
    conn.close()


def get_quiz_summary(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*) as quizzes_completed,
            AVG(score) as average_score,
            MAX(score) as best_score
        FROM quiz_attempts
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()

    return {
        "quizzes_completed": result[0] or 0,
        "average_score": round(result[1], 2) if result[1] is not None else 0,
        "best_score": result[2] if result[2] is not None else 0
    }

def get_recent_quiz_attempts(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic_name, score, total_questions, attempted_at
        FROM quiz_attempts
        WHERE user_id = ?
        ORDER BY attempted_at DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_topic_progress(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic_name, AVG(score) as avg_score
        FROM quiz_attempts
        WHERE user_id = ?
        GROUP BY topic_name
        ORDER BY topic_name
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_quiz_scores_over_time(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT attempted_at, score
        FROM quiz_attempts
        WHERE user_id = ?
        ORDER BY attempted_at ASC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows

    return rows