from datetime import date, timedelta

from utils import apply_review_result, build_default_progress, is_due_today_for_mode


def make_word():
    return {
        "word": "apple",
        "translation": "яблоко",
        "transcription": "/apple/",
        "level": "A1",
        "use": ["I", "eat", "an", "apple"],
        "progress": build_default_progress(),
    }


def test_wrong_answer_rolls_back_one_stage():
    word = make_word()
    progress = word["progress"]["ruen"]
    progress["stage_index"] = 3
    progress["first_try_streak"] = 2

    apply_review_result(word, "ruen", 2, date(2026, 4, 12))

    assert progress["stage_index"] == 2
    assert progress["first_try_streak"] == 0
    assert progress["marks"] == [2]
    assert progress["last_repeated"] == "2026-04-12"


def test_two_consecutive_first_try_successes_jump_two_levels_on_second():
    word = make_word()
    progress = word["progress"]["ruen"]
    progress["stage_index"] = 1
    progress["first_try_streak"] = 1

    apply_review_result(word, "ruen", 1, date(2026, 4, 12))

    assert progress["stage_index"] == 3
    assert progress["first_try_streak"] == 2
    assert progress["marks"] == [1]


def test_due_date_uses_new_stage_index():
    word = make_word()
    progress = word["progress"]["ruen"]
    progress["stage_index"] = 4
    progress["last_repeated"] = "2026-04-12"
    progress["marks"] = [1, 1, 1, 1]

    assert not is_due_today_for_mode(word, "ruen", date(2026, 5, 11))
    assert is_due_today_for_mode(word, "ruen", date(2026, 5, 12))


def test_legacy_marks_still_work_without_stage_fields():
    word = make_word()
    progress = word["progress"]["ruen"]
    progress.pop("stage_index")
    progress.pop("first_try_streak")
    progress["marks"] = [1, 1, 1]
    progress["last_repeated"] = "2026-04-12"

    assert not is_due_today_for_mode(word, "ruen", date(2026, 4, 18))
    assert is_due_today_for_mode(word, "ruen", date(2026, 4, 19))


def test_first_stage_is_due_after_one_day():
    word = make_word()

    apply_review_result(word, "ruen", 1, date(2026, 4, 12))

    assert not is_due_today_for_mode(word, "ruen", date(2026, 4, 12))
    assert is_due_today_for_mode(word, "ruen", date(2026, 4, 12) + timedelta(days=1))
