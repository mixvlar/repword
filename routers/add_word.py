from flask import Blueprint, render_template, request, jsonify
from utils import load_db, save_db
from copy import deepcopy

add_word_bp = Blueprint('add_word', __name__)

@add_word_bp.route('/add_word', methods=['GET'])
def add_word_page():
    return render_template('add_word.html')

@add_word_bp.route('/add_word', methods=['POST'])
def add_word_api():
    data = request.json
    word_entry = {
        "word": data["word"].strip(),
        "translation": data["translation"].strip(),
        "transcription": data["transcription"].strip(),
        "level": data["level"].strip(),
        "use": data["use"].strip().split(),
        "marks": [],
        "last_repeated": None
    }
    for mode in ["ruen", "enru"]:
        db = load_db(mode)
        if not any(w["word"].lower() == word_entry["word"].lower() for w in db):
            db.append(deepcopy(word_entry))
            save_db(mode, db)
    return jsonify({"status": "ok"})
