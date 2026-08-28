import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "books_data.json"

default_books = [
    {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021, "tags": [], "publisher": None},
    {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023, "tags": [], "publisher": None},
    {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022, "tags": [], "publisher": None},
    {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020, "tags": [], "publisher": None},
    {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year": 2024, "tags": [], "publisher": None},
]

books: list[dict] = []

def load_books() -> None:
    """파일에서 도서 목록을 읽어 books에 채운다. 파일이 없으면 기본값을 쓴다."""
    books.clear()
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            books.extend(json.load(f))
    else:
        books.extend(default_books)
        save_books()

def save_books() -> None:
    """현재 books 내용을 파일에 저장한다."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

load_books()