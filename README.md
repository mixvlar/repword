# Simple SRS Vocabulary Trainer

Small Flask app for drilling vocabulary with spaced repetition.

## What It Does

- Lets you learn words in two directions: `ruen` and `enru`
- Stores all words in one file: `words.json`
- Keeps progress for each direction separately inside each word
- Shows words due today and how many will be due tomorrow

## Data Format

The app uses a single JSON file in the project root:

```json
[
  {
    "word": "Apple",
    "translation": "Яблоко",
    "transcription": "/ˈæp.əl/",
    "level": "A1",
    "use": ["I", "eat", "an", "apple"],
    "progress": {
      "ruen": {
        "marks": [],
        "last_repeated": null
      },
      "enru": {
        "marks": [],
        "last_repeated": null
      }
    }
  }
]
```

## Getting Started

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
python main.py
```

3. Open:

```text
http://127.0.0.1:5000
```

## Notes

- Invalid learning URLs now redirect to the home page instead of crashing.
- In tests, the app uses `tests/data_template/words.json`.
