import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "red",
    "difficulty": "normal"
}


def load_json(filename, default_data):
    """Load data from JSON file. If file does not exist, create it."""
    if not os.path.exists(filename):
        save_json(filename, default_data)
        return default_data

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        save_json(filename, default_data)
        return default_data


def save_json(filename, data):
    """Save data to JSON file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_settings():
    """Load game settings."""
    return load_json(SETTINGS_FILE, DEFAULT_SETTINGS.copy())


def save_settings(settings):
    """Save game settings."""
    save_json(SETTINGS_FILE, settings)


def load_leaderboard():
    """Load leaderboard list."""
    return load_json(LEADERBOARD_FILE, [])


def add_score(username, score, distance, coins):
    """Add a new result and keep only top 10 scores."""
    leaderboard = load_leaderboard()

    leaderboard.append({
        "username": username,
        "score": score,
        "distance": distance,
        "coins": coins
    })

    leaderboard.sort(key=lambda item: item["score"], reverse=True)
    leaderboard = leaderboard[:10]
    save_json(LEADERBOARD_FILE, leaderboard)
