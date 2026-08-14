# from fastapi import FastAPI

# app = FastAPI()

# from fastapi.staticfiles import StaticFiles
# app.mount("/static", StaticFiles(directory="static"), name="static")


# books = [
#      {"id": 1, "title": " 파이썬   입문 ", "author": " 김철수 ", "year": 2021},
#      {"id": 2, "title": "FastAPI  실전 ", "author": " 이영희 ", "year": 2023},
#      {"id": 3, "title": " 파이썬   웹개발 ", "author": " 김철수 ", "year": 2022},
#      {"id": 4, "title": " 데이터   분석   기초 ", "author": " 박민수 ", "year": 2020},
#      {"id": 5, "title": "FastAPI 로   배우는   백엔드 ", "author": " 이영희 ", "year": 2024}, 
#  ]

# @app.get("/")
# def read_root():
#     return {"message": "환경 구축 완료~~!!"}


# @app.get("/health")
# def health():
#     return {"status": "healthy"}

# @app.get("/info")
# def info():
#     return {"name": "도서 관리 API", "version": "0.1.0"}

# # 도서의 목록을 제공하는 엔드 포인트
# @app.get("/books")
# def list_books():
#     return books

# # 리터럴 경로는 /books/{book_id}보다 먼저 선언한다
# @app.get("/books/search")
# def search_books(keyword: str = ""):
#     if not keyword:
#         return books
#     return [b for b in books if keyword in b["title"]]

# @app.get("/books/filter")
# def filter_books(author: str = "", sort: str = ""):
#     result = books
#     if author:
#         result = [b for b in result if b["author"] == author]
#     if sort == "year":
#         result = sorted(result, key=lambda b: b["year"])
#     return result


# @app.get("/books/page")
# def page_books(skip: int = 0, limit: int = 2):
#     return books[skip: skip + limit]

# @app.get("/books/{book_id}")
# def read_book(book_id: int):
#     for book in books:
#         if book["id"] == book_id:
#             return book
#     return {"error": "not found"}


# from pydantic import BaseModel, Field
# from fastapi import status

# class Publisher(BaseModel):
#     name: str
#     city: str = "서울"
# class BookCreate(BaseModel):
#     title: str = Field(min_length=1, max_length=100)
#     author: str = Field(min_length=1, max_length=50)
#     year: int = Field(ge=1900, le=2026)
#     tags: list[str] = Field(default_factory=list)
#     publisher : Publisher | None = None


# class BookResponse(BookCreate):
#     id: int

# @app.post("/books", response_model=BookResponse,
# status_code=status.HTTP_201_CREATED)
# def create_book(book: BookCreate):
#     new_id = max([b["id"] for b in books], default=0) + 1
#     new_book = {"id": new_id, **book.model_dump()}
#     books.append(new_book)
#     return new_book

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from schemas import WeatherResponse, BookResponse, GoogleBooks, BookCreate
from external_api import fetch_books, fetch_weather

# import httpx

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


books = [
    {
        "id": 1,
        "title": "파이썬 입문",
        "author": "김철수",
        "year": 2021,
        "tags": [],
        "publisher": None
    },
    {
        "id": 2,
        "title": "FastAPI 실전",
        "author": "이영희",
        "year": 2023,
        "tags": [],
        "publisher": None
    },
    {
        "id": 3,
        "title": "파이썬 웹개발",
        "author": "김철수",
        "year": 2022,
        "tags": [],
        "publisher": None
    },
    {
        "id": 4,
        "title": "데이터 분석 기초",
        "author": "박민수",
        "year": 2020,
        "tags": [],
        "publisher": None
    },
    {
        "id": 5,
        "title": "FastAPI로 배우는 백엔드",
        "author": "이영희",
        "year": 2024,
        "tags": [],
        "publisher": None
    },
]


class Publisher(BaseModel):
    name: str
    city: str = "서울"


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1900, le=2100)
    tags: list[str] = Field(default_factory=list)
    publisher: Publisher | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("제목은 공백일 수 없습니다")

        return v




@app.get("/")
def read_root():
    return {"message": "FastAPI 첫 서버"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/info")
def info():
    return {
        "name": "도서 관리 API",
        "version": "0.2.0"
    }


@app.get("/books", response_model=list[BookResponse])
def list_books():
    return books


@app.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
def create_book(book: BookCreate):
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(
                status_code=409,
                detail="이미 등록된 제목입니다"
            )

    new_id = max([b["id"] for b in books], default=0) + 1

    new_book = {
        "id": new_id,
        **book.model_dump()
    }

    books.append(new_book)

    return new_book


# 리터럴 경로는 /books/{book_id}보다 먼저 선언한다
@app.get("/books/search")
def search_books(keyword: str = ""):
    if not keyword:
        return books

    return [
        b for b in books
        if keyword in b["title"]
    ]


@app.get("/books/filter")
def filter_books(author: str = "", sort: str = ""):
    result = books

    if author:
        result = [
            b for b in result
            if b["author"] == author
        ]

    if sort == "year":
        result = sorted(
            result,
            key=lambda b: b["year"]
        )

    return result


@app.get("/books/page")
def page_books(skip: int = 0, limit: int = 2):
    return books[skip: skip + limit]




# @app.get("/weather/raw")
# async def weather_raw():
#     async with httpx.AsyncClient(timeout=5.0) as client:
#         response = await client.get(
#             "https://api.open-meteo.com/v1/forecast",
#             params={
#                 "latitude": 36.8,
#                 "longitude": 127.1,
#                 "current": "temperature_2m",
#             },
#         )
#         return response.json()


from external_api import fetch_weather

@app.get("/weather", response_model=WeatherResponse)
async def weather(latitude: float=36.8, longitude: float=127.1):
    return await fetch_weather(latitude, longitude)

#엔드 포인트
@app.get("/books/external", response_model=list[GoogleBooks])
async def search_external_books(keyword:str, limit:int=5):
    return await  fetch_books(keyword, limit)

@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(
        status_code=404,
        detail="도서를 찾을 수 없습니다"
    )