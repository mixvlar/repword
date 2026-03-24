from flask import Blueprint, render_template, request, jsonify
from utils import load_db, save_db, normalize_word_entry

add_word_bp = Blueprint('add_word', __name__)

@add_word_bp.route('/add_word', methods=['GET'])
def add_word_page():
    return render_template('add_word.html')

@add_word_bp.route('/add_word', methods=['POST'])
def add_word_api():
    data = request.get_json(silent=True) or {}
    db = load_db("ruen")

    if "words" in data:
        raw_words = data["words"]
        if not isinstance(raw_words, list):
            return jsonify({"status": "error", "message": "'words' must be a JSON array"}), 400

        existing_words = {word["word"].lower() for word in db if isinstance(word, dict) and "word" in word}
        added = 0
        skipped = 0

        try:
            for raw_word in raw_words:
                word_entry = normalize_word_entry(raw_word)
                word_key = word_entry["word"].lower()

                if word_key in existing_words:
                    skipped += 1
                    continue

                db.append(word_entry)
                existing_words.add(word_key)
                added += 1
        except ValueError as error:
            return jsonify({"status": "error", "message": str(error)}), 400

        if added:
            save_db("ruen", db)

        return jsonify({"status": "ok", "added": added, "skipped": skipped})

    try:
        word_entry = normalize_word_entry(data)
    except ValueError as error:
        return jsonify({"status": "error", "message": str(error)}), 400

    if not any(w["word"].lower() == word_entry["word"].lower() for w in db):
        db.append(word_entry)
        save_db("ruen", db)
        return jsonify({"status": "ok"})

    return jsonify({"status": "duplicate"})
