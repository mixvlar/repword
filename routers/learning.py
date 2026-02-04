from flask import Blueprint, render_template, jsonify, request
from utils import load_db, save_db, is_due_today
from datetime import date, timedelta
import random


learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/ruen')
def ruen(): return render_template('ruen.html')

@learning_bp.route('/enru')
def enru(): return render_template('enru.html')

@learning_bp.route('/get_words/<mode>')
def get_words(mode):
    db = load_db(mode)
    today_words = [w for w in db if is_due_today(w)]
    random.shuffle(today_words)
    return jsonify(today_words)

@learning_bp.route('/save_result/<mode>', methods=['POST'])
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


@learning_bp.route('/tomorrow')
def get_tomorrow_words():
    ruen = len([w for w in load_db("ruen") if is_due_today(w,date.today()+timedelta(days=1))])
    enru = len([w for w in load_db("enru") if is_due_today(w,date.today()+timedelta(days=1))])
    return render_template("tomorrow.html", ruen=ruen, enru=enru)