import json
from flask import Flask, render_template, jsonify, request
from datetime import datetime, date
from copy import deepcopy
import os

app = Flask(__name__)

DBS = {
    "ruen": "words_ruen.json",
    "enru": "words_enru.json"
}

PROGRESS_FILE = "progress.json"


# -------------------------
# 🔹 Работа с базой слов
# -------------------------
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
    # index 0 = 1 день, 1 = 3 дня, 2 = 7 дней и т.д.
    base = [1, 3, 7, 21, 30, 60, 90, 120]
    if index < 0:
        return 1
    if index < len(base):
        return base[index]
    return 120 + 60 * (index - len(base) + 1)


def is_due_today(word):
    if not isinstance(word, dict):
        return False

    marks = word.get("marks", [])

    # 1. Если слово совсем новое — показываем сразу
    if not marks:
        return True

    # 2. Считаем разницу с последнего повторения
    last = datetime.strptime(word["last_repeated"], "%Y-%m-%d").date()
    today = date.today()
    days_passed = (today - last).days

    # 3. 🔹 ЛОГИКА СТРИКА (Серии успехов)
    # Если в последний раз была ошибка (попыток > 1) — интервал 1 день
    if marks[-1] > 1:
        interval = 1
    else:
        # Считаем серию ответов "с первой попытки" с конца списка
        strike = 0
        for m in reversed(marks):
            if m == 1:
                strike += 1
            else:
                break  # Любая ошибка (2, 3...) прерывает серию

        # Интервал зависит от длины текущей чистой серии
        # Если strike=1 (вспомнил после ошибки), берем get_interval(0) = 1 день
        # Если strike=2 (дважды вспомнил сам), берем get_interval(1) = 3 дня
        interval = get_interval(strike - 1)

    return days_passed >= interval


# -------------------------
# 🔹 Работа с прогрессом
# -------------------------
def load_progress(mode):
    if not os.path.exists(PROGRESS_FILE):
        return None
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    today_str = date.today().strftime("%Y-%m-%d")
    prog = data.get(mode)
    if prog and prog["words"] and prog["date"] == today_str:
        return prog["words"]
    return None


def save_progress(mode, words):
    today_str = date.today().strftime("%Y-%m-%d")
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            progress = json.load(f)
    progress[mode] = {
        "date": today_str,
        "words": words
    }
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


# -------------------------
# 📄 Страницы
# -------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ruen')
def ruen():
    return render_template('ruen.html')


@app.route('/enru')
def enru():
    return render_template('enru.html')


@app.route('/add_word')
def add_word_page():
    return render_template('add_word.html')


# -------------------------
# 🔌 API
# -------------------------
@app.route('/get_words/<mode>')
def get_words(mode):
    saved_words = load_progress(mode)
    if saved_words is not None:
        return jsonify(saved_words)

    db = load_db(mode)
    today_words = [w for w in db if is_due_today(w)]
    return jsonify(today_words)


@app.route('/save_result/<mode>', methods=['POST'])
def save_result(mode):
    data = request.json  # { "word": "...", "attempts": 1 }
    db = load_db(mode)
    for w in db:
        if w["word"] == data["word"]:
            w["marks"].append(data["attempts"])
            w["last_repeated"] = date.today().strftime("%Y-%m-%d")
            break
    save_db(mode, db)
    return jsonify({"status": "ok"})


@app.route('/add_word', methods=['POST'])
def add_word_api():
    data = request.json
    word_entry = {
        "word": data["word"].strip(),
        "translation": data["translation"].strip(),
        "transcription": data["transcription"].strip(),
        "marks": [],
        "last_repeated": None
    }

    duplicate = False
    for mode in ["ruen", "enru"]:
        db = load_db(mode)
        if any(w["word"].lower() == word_entry["word"].lower() for w in db):
            duplicate = True
            break

    if duplicate:
        return jsonify({"status": "duplicate"})

    for mode in ["ruen", "enru"]:
        db = load_db(mode)
        db.append(deepcopy(word_entry))
        save_db(mode, db)

    return jsonify({"status": "ok"})


@app.route('/finish_later/<mode>', methods=['POST'])
def finish_later(mode):
    data = request.json
    save_progress(mode, data["words"])
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(debug=True)
