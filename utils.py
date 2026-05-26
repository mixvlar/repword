import json
import os
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILENAME = "words.json"
VALID_MODES = {"ruen", "enru"}
BASE_INTERVALS = [1, 1, 3, 7, 21, 30, 60, 90, 120]


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


def build_default_progress():
    return {
        mode: {
            "marks": [],
            "last_repeated": None,
            "stage_index": 0,
            "first_try_streak": 0,
        }
        for mode in VALID_MODES
    }


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
            "stage_index": normalize_stage_index(mode_progress.get("stage_index"), marks),
            "first_try_streak": normalize_first_try_streak(
                mode_progress.get("first_try_streak"), marks
            ),
        }

    word["progress"] = progress
    return word


def normalize_use(use_value):
    if isinstance(use_value, str):
        return use_value.strip().split()

    if isinstance(use_value, list):
        normalized = []
        for item in use_value:
            if not isinstance(item, str):
                raise ValueError("Each item in 'use' must be a string")

            clean_item = item.strip()
            if clean_item:
                normalized.append(clean_item)
        return normalized

    raise ValueError("'use' must be a string or a list of strings")


def normalize_example(example_value):
    if example_value is None:
        return ""

    if not isinstance(example_value, str):
        raise ValueError("Field 'example' must be a string")

    return example_value.strip()


def normalize_explanation(explanation_value):
    if explanation_value is None:
        return ""

    if not isinstance(explanation_value, str):
        raise ValueError("Field 'explanation' must be a string")

    return explanation_value.strip()


def normalize_word_entry(raw_word):
    if not isinstance(raw_word, dict):
        raise ValueError("Each word entry must be a JSON object")

    required_fields = ["word", "translation", "transcription", "level", "use"]
    normalized = {}

    for field in required_fields:
        if field not in raw_word:
            raise ValueError(f"Missing required field: {field}")

    for field in ["word", "translation", "transcription", "level"]:
        value = raw_word.get(field)
        if not isinstance(value, str):
            raise ValueError(f"Field '{field}' must be a string")

        clean_value = value.strip()
        if not clean_value:
            raise ValueError(f"Field '{field}' cannot be empty")

        normalized[field] = clean_value

    normalized["use"] = normalize_use(raw_word.get("use"))
    normalized["example"] = normalize_example(raw_word.get("example"))
    normalized["explanation"] = normalize_explanation(raw_word.get("explanation"))
    normalized["progress"] = raw_word.get("progress", build_default_progress())
    ensure_progress(normalized)
    return normalized


def derive_stage_index_from_marks(marks):
    stage_index, _first_try_streak = derive_stage_state_from_marks(marks)
    return stage_index


def derive_first_try_streak_from_marks(marks):
    _stage_index, first_try_streak = derive_stage_state_from_marks(marks)
    return first_try_streak


def derive_stage_state_from_marks(marks):
    stage_index = 0
    first_try_streak = 0

    for mark in marks:
        if mark == 1:
            first_try_streak += 1
            stage_index += 2 if first_try_streak >= 2 else 1
        else:
            stage_index = max(0, stage_index - 1)
            first_try_streak = 0

    return stage_index, first_try_streak


def normalize_stage_index(stage_index, marks):
    if isinstance(stage_index, int) and stage_index >= 0:
        return stage_index
    return derive_stage_index_from_marks(marks)


def normalize_first_try_streak(first_try_streak, marks):
    if isinstance(first_try_streak, int) and first_try_streak >= 0:
        return first_try_streak
    return derive_first_try_streak_from_marks(marks)


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
    if index < 0:
        return 1
    if index < len(BASE_INTERVALS):
        return BASE_INTERVALS[index]
    return BASE_INTERVALS[-1] + 30 * (index - len(BASE_INTERVALS) + 1)


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
    stage_index = derive_stage_index_from_marks(marks)
    interval = get_interval(stage_index)

    return days_passed >= interval


def apply_review_result(word, mode, attempts_count, today=None):
    ensure_valid_mode(mode)

    if today is None:
        today = date.today()

    if not isinstance(attempts_count, int) or attempts_count < 1:
        raise ValueError("attempts_count must be a positive integer")

    progress = get_mode_progress(word, mode)
    progress["marks"].append(attempts_count)

    current_stage = progress.get("stage_index", 0)
    current_streak = progress.get("first_try_streak", 0)

    if attempts_count == 1:
        new_streak = current_streak + 1
        step_up = 2 if new_streak >= 2 else 1
        progress["stage_index"] = current_stage + step_up
        progress["first_try_streak"] = new_streak
    else:
        rollback = 2 if get_interval(current_stage) >= 60 else 1
        progress["stage_index"] = max(0, current_stage - rollback)
        progress["first_try_streak"] = 0

    progress["last_repeated"] = today.strftime("%Y-%m-%d")
    return progress
