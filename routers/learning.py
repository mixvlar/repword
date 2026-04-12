from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from utils import load_db, save_db, is_due_today_for_mode, apply_review_result, is_valid_mode
from datetime import date, timedelta
import random


learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/ruen')
def ruen(): return render_template('ruen.html')

@learning_bp.route('/enru')
def enru(): return render_template('enru.html')

@learning_bp.route('/get_words/<mode>')
def get_words(mode):
    if not is_valid_mode(mode):
        return redirect(url_for("index"))

    db = load_db(mode)
    today_words = [w for w in db if is_due_today_for_mode(w, mode)]
    random.shuffle(today_words)
    return jsonify(today_words)

@learning_bp.route('/save_result/<mode>', methods=['POST'])
def save_result(mode):
    if not is_valid_mode(mode):
        return redirect(url_for("index"))

    data = request.json
    db = load_db(mode)
    for w in db:
        if w["word"] == data["word"]:
            apply_review_result(w, mode, data["attempts"], date.today())
            break
    save_db(mode, db)
    return jsonify({"status": "ok"})


@learning_bp.route('/tomorrow')
def get_tomorrow_words():
    db = load_db("ruen")
    tomorrow = date.today() + timedelta(days=1)
    ruen = len([w for w in db if is_due_today_for_mode(w, "ruen", tomorrow)])
    enru = len([w for w in db if is_due_today_for_mode(w, "enru", tomorrow)])
    return render_template("tomorrow.html", ruen=ruen, enru=enru)
