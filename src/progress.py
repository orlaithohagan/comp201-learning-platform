import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_date TEXT NOT NULL,
            UNIQUE(user_id, activity_date)
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

def get_attempted_topics(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT topic_name
        FROM quiz_attempts
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows if row[0]]

def get_quiz_attempts_for_topic(user_id, topic_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT score, attempted_at
        FROM quiz_attempts
        WHERE user_id = ? AND topic_name = ?
        ORDER BY attempted_at ASC
    """, (user_id, topic_name))

    rows = cursor.fetchall()
    conn.close()
    return rows

def log_daily_activity(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT OR IGNORE INTO daily_activity (user_id, activity_date)
        VALUES (?, ?)
    """, (user_id, today))

    conn.commit()
    conn.close()

def get_learning_streak(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT activity_date
        FROM daily_activity
        WHERE user_id = ?
        ORDER BY activity_date DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0

    activity_dates = {row[0] for row in rows}

    streak = 0
    current_day = datetime.now().date()

    while current_day.strftime("%Y-%m-%d") in activity_dates:
        streak += 1
        current_day -= timedelta(days=1)

    return streak