from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from routers import books, external, system

tags_metadata = [
    {"name": "시스템", "description": "서버 상태와 앱 정보 확인"},
    {"name": "도서", "description": "내 도서 목록의 등록, 조회, 수정, 삭제"},
    {"name": "외부 연동", "description": "Google Books 도서 검색과 날씨 조회"},
]

app = FastAPI(
    title="도서 관리 API",
    description="도서를 등록·조회하고, 외부 서비스에서 정보를 가져오는 API",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 등록 순서 주의: /books/external 이 /books/{book_id} 보다 먼저 등록돼야 한다
app.include_router(system.router)
app.include_router(external.router)
app.include_router(books.router)