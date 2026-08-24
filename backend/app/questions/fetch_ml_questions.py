"""Fetches the MLQuestions GitHub repo (https://github.com/andrewekhalel/MLQuestions)
and writes it to backend/data/ml_questions.md, tagging each question with a field so
the retriever can filter by the candidate's classified field (nlp / cv / other).

Run directly: `python -m app.questions.fetch_ml_questions`
"""

from pathlib import Path

import requests

ROOT_README = "https://raw.githubusercontent.com/andrewekhalel/MLQuestions/master/README.md"
NLP_README = "https://raw.githubusercontent.com/andrewekhalel/MLQuestions/master/NLP/README.md"

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
OUTPUT_PATH = DATA_DIR / "ml_questions.md"


def fetch(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def build_markdown() -> str:
    general = fetch(ROOT_README)
    nlp = fetch(NLP_README)

    parts = [
        "<!-- Fetched from github.com/andrewekhalel/MLQuestions. -->",
        "",
        "<!-- field: cv -->",
        general,
        "",
        "<!-- field: nlp -->",
        nlp,
    ]
    return "\n".join(parts)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_markdown(), encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
