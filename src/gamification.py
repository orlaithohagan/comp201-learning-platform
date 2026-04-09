# src/gamification.py
BADGES = [
    {
        "id": "quiz_starter",
        "name": "Quiz Starter",
        "description": "Complete your first quiz.",
    },
    {
        "id": "streak_3",
        "name": "3-Day Streak",
        "description": "Study for 3 days in a row.",
    },
    {
        "id": "topic_master",
        "name": "Topic Master",
        "description": "Score 80% or more in a topic quiz.",
    },
    {
        "id": "game_explorer",
        "name": "Game Explorer",
        "description": "Play all mini-games at least once.",
    },
    {
        "id": "consistent_learner",
        "name": "Consistent Learner",
        "description": "Complete 3 quizzes.",
    },
        {
        "id": "high_achiever",
        "name": "High Achiever",
        "description": "Achieve an average score of 70% or higher.",
    },
]

def get_user_badges(user_stats):
    earned = []

    if user_stats.get("quizzes_completed", 0) >= 1:
        earned.append("quiz_starter")

    if user_stats.get("streak", 0) >= 3:
        earned.append("streak_3")

    if user_stats.get("best_topic_score", 0) >= 80:
        earned.append("topic_master")

    if user_stats.get("quizzes_completed", 0) >= 3:
        earned.append("consistent_learner")

    if user_stats.get("average_score", 0) >= 70:
        earned.append("high_achiever")

    return earned