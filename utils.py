import os, json
from datetime import date, datetime


DBS = {
    "ruen": "words_ruen.json",
    "enru": "words_enru.json"
}

def load_db(mode):
    if not os.path.exists(DBS[mode]):
        with open(DBS[mode], "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(DBS[mode], 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = list(data.values())
    return data


def save_db(mode, data):
    with open(DBS[mode], 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_interval(index):
    base = [1, 3, 7, 21, 30, 60, 90, 120]
    if index < 0: return 1
    if index < len(base): return base[index]
    return 120 + 60 * (index - len(base) + 1)


def is_due_today(word):
    if not isinstance(word, dict): return False
    marks = word.get("marks", [])
    if not marks: return True
    if not word.get("last_repeated"): return True

    last = datetime.strptime(word["last_repeated"], "%Y-%m-%d").date()
    today = date.today()
    days_passed = (today - last).days

    if marks[-1] > 1:
        interval = 1
    else:
        strike = 0
        for m in reversed(marks):
            if m == 1:
                strike += 1
            else:
                break
        interval = get_interval(strike - 1)
    return days_passed >= interval
