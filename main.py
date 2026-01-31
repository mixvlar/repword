import json
from flask import Flask, render_template, jsonify, request
from datetime import datetime, date
from copy import deepcopy
import os
import random

app = Flask(__name__)

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


@app.route('/')
def index(): return render_template('index.html')


@app.route('/ruen')
def ruen(): return render_template('ruen.html')


@app.route('/enru')
def enru(): return render_template('enru.html')


@app.route('/add_word')
def add_word_page(): return render_template('add_word.html')


@app.route('/get_words/<mode>')
def get_words(mode):
    db = load_db(mode)
    today_words = [w for w in db if is_due_today(w)]
    random.shuffle(today_words)
    return jsonify(today_words)


@app.route('/save_result/<mode>', methods=['POST'])
def save_result(mode):
    data = request.json
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
    for mode in ["ruen", "enru"]:
        db = load_db(mode)
        if not any(w["word"].lower() == word_entry["word"].lower() for w in db):
            db.append(deepcopy(word_entry))
            save_db(mode, db)
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
