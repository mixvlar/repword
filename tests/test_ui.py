from playwright.sync_api import Page, expect


def test_add_new_word_flow(page: Page):
    page.goto("http://127.0.0.1:5000/add_word")

    expect(page.locator("#addWordForm")).to_be_visible()

    page.fill("#word", "Apple")
    page.fill("#translation", "Яблоко")
    page.fill("#transcription", "ˈæp.əl")
    page.fill("#level", "A1")
    page.fill("#use", "I eat an apple")

    page.click("button[type='submit']")

    feedback = page.locator("#feedback")
    expect(feedback).to_be_visible()
    expect(feedback).to_have_text("Слово добавлено!")

    expect(page.locator("#btnHome")).to_be_visible()
