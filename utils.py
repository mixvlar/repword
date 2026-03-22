import json
import os
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILENAME = "words.json"
VALID_MODES = {"ruen", "enru"}


def is_valid_mode(mode):
    return mode in VALID_MODES


def ensure_valid_mode(mode):
    if mode not in VALID_MODES:
        raise ValueError(f"Unsupported mode: {mode}")


def get_db_path(mode):
    ensure_valid_mode(mode)

    if os.environ.get("TESTING") == "True":
        data_dir = os.path.join(BASE_DIR, "tests", "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, DB_FILENAME)

    return os.path.join(BASE_DIR, DB_FILENAME)


def ensure_progress(word):
    progress = word.get("progress")
    if not isinstance(progress, dict):
        progress = {}

    for mode in VALID_MODES:
        mode_progress = progress.get(mode)
        if not isinstance(mode_progress, dict):
            mode_progress = {}

        marks = mode_progress.get("marks", [])
        if not isinstance(marks, list):
            marks = []

        progress[mode] = {
            "marks": marks,
            "last_repeated": mode_progress.get("last_repeated"),
        }

    word["progress"] = progress
    return word


def get_mode_progress(word, mode):
    ensure_valid_mode(mode)
    ensure_progress(word)
    return word["progress"][mode]


def load_db(mode):
    db_path = get_db_path(mode)

    if not os.path.exists(db_path):
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = list(data.values())

    if not isinstance(data, list):
        raise ValueError(f"{db_path} must contain a JSON array")

    for word in data:
        if isinstance(word, dict):
            ensure_progress(word)

    return data


def save_db(mode, data):
    db_path = get_db_path(mode)
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_interval(index):
    base = [1, 3, 7, 21, 30, 60, 90, 120]
    if index < 0:
        return 1
    if index < len(base):
        return base[index]
    return 120 + 60 * (index - len(base) + 1)


def is_due_today(word, today=date.today()):
    return is_due_today_for_mode(word, "ruen", today)


def is_due_today_for_mode(word, mode, today=date.today()):
    if not isinstance(word, dict):
        return False

    progress = get_mode_progress(word, mode)
    marks = progress.get("marks", [])
    if not marks:
        return True

    last_repeated = progress.get("last_repeated")
    if not last_repeated:
        return True

    last = datetime.strptime(last_repeated, "%Y-%m-%d").date()
    days_passed = (today - last).days

    if marks[-1] > 1:
        interval = 1
    else:
        strike = 0
        for mark in reversed(marks):
            if mark == 1:
                strike += 1
            else:
                break
        interval = get_interval(strike - 1)

    return days_passed >= interval
