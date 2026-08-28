import time

import httpx

from fastapi import APIRouter, HTTPException

from database import books, save_books
from external_api import (
    fetch_books,
    fetch_books_multi,
    fetch_weather,
    load_fallback_books,
)
from routers.schemas import BookResponse, ErrorDetail, GoogleBooks, WeatherResponse

router = APIRouter(tags=["외부 연동"])


@router.get(
    "/weather",
    response_model=WeatherResponse,
    summary="현재 날씨 조회",
    responses={
        502: {"description": "외부 API 연결 실패 또는 오류 응답", "model": ErrorDetail},
        504: {"description": "외부 API 응답 지연", "model": ErrorDetail},
    },
)
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    """
    좌표로 현재 날씨를 조회합니다.

    - **latitude**: 위도. 기본값은 천안(36.8)
    - **longitude**: 경도. 기본값은 천안(127.1)
    """
    try:
        return await fetch_weather(latitude, longitude)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")


@router.get(
    "/books/external",
    response_model=list[GoogleBooks],
    summary="Google Books 검색",
    responses={
        502: {"description": "외부 API 연결 실패 또는 오류 응답", "model": ErrorDetail},
        504: {"description": "외부 API 응답 지연", "model": ErrorDetail},
    },
)
async def search_external_books(keyword: str, limit: int = 5, fallback: bool = False):
    """
    Google Books에서 도서를 검색합니다.

    - **keyword**: 검색어. 한국어도 가능합니다
    - **limit**: 가져올 개수. 기본 5
    - **fallback**: true이면 외부 API 실패 시 예비 데이터를 반환합니다
    """
    try:
        return await fetch_books(keyword, limit)
    except httpx.TimeoutException:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")


@router.get("/books/external/multi", summary="여러 키워드 동시 검색")
async def search_multi(keywords: str = "python,fastapi,django"):
    """쉼표로 구분한 여러 키워드를 동시에 검색합니다."""
    words = [w.strip() for w in keywords.split(",") if w.strip()]

    start = time.perf_counter()
    results = await fetch_books_multi(words)
    elapsed = round(time.perf_counter() - start, 2)

    return {"elapsed_seconds": elapsed, "results": results}


@router.post(
    "/books/from-external",
    response_model=BookResponse,
    status_code=201,
    summary="외부 검색 결과 담기",
    responses={409: {"description": "이미 등록된 제목입니다", "model": ErrorDetail}},
)
def create_from_external(book: GoogleBooks):
    """
    Google Books 검색 결과를 내 도서 목록에 등록합니다.

    - **authors**: 첫 번째 저자만 사용하며, 비어 있으면 "미상"이 됩니다
    - **published_date**: 앞 4자리를 연도로 사용하며, 없으면 2000이 됩니다
    """
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")

    year = 2000
    if book.published_date[:4].isdigit():
        year = int(book.published_date[:4])

    new_id = max([b["id"] for b in books], default=0) + 1
    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.authors[0] if book.authors else "미상",
        "year": year,
        "tags": ["외부검색"],
        "publisher": None,
    }
    books.append(new_book)
    save_books()
    return new_book