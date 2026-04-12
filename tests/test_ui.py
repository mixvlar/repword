from playwright.sync_api import Page, expect


def test_add_new_word_flow(page: Page):
    page.goto("http://127.0.0.1:5000/add_word")

    expect(page.locator("#modeChooser")).to_be_visible()

    page.click("#showSingleForm")

    expect(page.locator("#addWordForm")).to_be_visible()

    page.fill("#word", "Apple")
    page.fill("#translation", "Яблоко")
    page.fill("#transcription", "/ˈæp.əl/")
    page.fill("#level", "A1")
    page.fill("#use", "I eat an apple")
    page.fill("#example", "I eat an apple every day.")

    page.click("#addWordForm button[type='submit']")

    feedback = page.locator("#feedback")
    expect(feedback).to_be_visible()
    expect(feedback).to_have_text("Слово добавлено!")

    expect(page.locator("#btnHome")).to_be_visible()


def test_add_json_word_list_flow(page: Page):
    page.goto("http://127.0.0.1:5000/add_word")

    page.click("#showJsonForm")

    expect(page.locator("#addJsonForm")).to_be_visible()

    page.fill(
        "#jsonWords",
        """[
  {
    "word": "Banana",
    "translation": "Банан",
    "transcription": "/bəˈnɑː.nə/",
    "level": "A1",
    "use": ["yellow", "fruit"],
    "example": "Bananas are my favorite fruit.",
    "progress": {
      "ruen": {"marks": [], "last_repeated": null, "stage_index": 0, "first_try_streak": 0},
      "enru": {"marks": [], "last_repeated": null, "stage_index": 0, "first_try_streak": 0}
    }
  },
  {
    "word": "Apple",
    "translation": "Яблоко",
    "transcription": "/ˈæp.əl/",
    "level": "A1",
    "use": ["I", "eat", "an", "apple"],
    "example": "I eat an apple every day.",
    "progress": {
      "ruen": {"marks": [], "last_repeated": null, "stage_index": 0, "first_try_streak": 0},
      "enru": {"marks": [], "last_repeated": null, "stage_index": 0, "first_try_streak": 0}
    }
  }
]""",
    )

    page.click("#addJsonForm button[type='submit']")

    feedback = page.locator("#feedback")
    expect(feedback).to_be_visible()
    expect(feedback).to_have_text("Импорт завершен: добавлено 1, пропущено 1.")

    expect(page.locator("#btnHome")).to_be_visible()
