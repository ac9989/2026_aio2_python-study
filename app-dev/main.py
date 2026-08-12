from fastapi import FastAPI

app = FastAPI()

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")


books = [
     {"id": 1, "title": " 파이썬   입문 ", "author": " 김철수 ", "year": 2021},
     {"id": 2, "title": "FastAPI  실전 ", "author": " 이영희 ", "year": 2023},
     {"id": 3, "title": " 파이썬   웹개발 ", "author": " 김철수 ", "year": 2022},
     {"id": 4, "title": " 데이터   분석   기초 ", "author": " 박민수 ", "year": 2020},
     {"id": 5, "title": "FastAPI 로   배우는   백엔드 ", "author": " 이영희 ", "year": 2024}, 
 ]

@app.get("/")
def read_root():
    return {"message": "환경 구축 완료~~!!"}


@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/info")
def info():
    return {"name": "도서 관리 API", "version": "0.1.0"}

# 도서의 목록을 제공하는 엔드 포인트
@app.get("/books")
def list_books():
    return books

# 리터럴 경로는 /books/{book_id}보다 먼저 선언한다
@app.get("/books/search")
def search_books(keyword: str = ""):
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]

@app.get("/books/{book_id}")
def read_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return {"error": "not found"}
