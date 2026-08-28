import httpx
# import requests
import os
from dotenv import load_dotenv
import asyncio
from routers.schemas import GoogleBooks, WeatherResponse
import json
from pathlib import Path

from routers.schemas import GoogleBooks

load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
EXTERNAL_TIMEOUT = float(os.getenv("EXTERNAL_TIMEOUT", "5.0"))

from routers.schemas import WeatherResponse, GoogleBooks

async def fetch_weather(latitude: float, longitude: float) -> WeatherResponse:
    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
            },
        )
        response.raise_for_status()
        data = response.json()

    return WeatherResponse(
        latitude=data["latitude"],
        longitude=data["longitude"],
        temperature=data["current"]["temperature_2m"],
        time=data["current"]["time"],
    )


async def fetch_books(keyword:str, limit:int=5) -> list[GoogleBooks]:
    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT) as client:
        response = await client.get(
            "https://www.googleapis.com/books/v1/volumes", 
            params = {
                    "q":keyword, "maxResults":limit,
                    "key":GOOGLE_BOOKS_API_KEY 
                },
            )
        response.raise_for_status()
        data = response.json()

    # GoogleBooks 생성
    result = []
    for item in data.get('items',[]):
        book_info = item.get('volumeInfo',{}) #책 한권 정보
        result.append(GoogleBooks(
            title = book_info.get('title', "제목없음"),
            authors = book_info.get('authors', []),
            published_data=book_info.get('publishedDate', "없음ㅋ")
        ))

    return result




if not GOOGLE_BOOKS_API_KEY:
    print("경고: GOOGLE_BOOKS_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")


async def fetch_books(keyword: str, limit: int = 5) -> list[GoogleBooks]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": keyword, "maxResults": limit, "key": GOOGLE_BOOKS_API_KEY},
        )
        response.raise_for_status()
        data = response.json()

    result = []
    for item in data.get("items", []):
        info = item.get("volumeInfo", {})
        result.append(
            GoogleBooks(
                title=info.get("title", "제목 없음"),
                authors=info.get("authors", []),
                published_date=info.get("publishedDate", ""),
            )
        )
    return result



def load_fallback_books() -> list[GoogleBooks]:
    path = Path(__file__).parent / "sample_books.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [GoogleBooks(**item) for item in raw]

async def _fetch_titles(client: httpx.AsyncClient, keyword: str) -> dict:
    response = await client.get(
        "https://www.googleapis.com/books/v1/volumes",
        params={"q": keyword, "maxResults": 3, "key": GOOGLE_BOOKS_API_KEY},
    )
    data = response.json()
    titles = [
        item.get("volumeInfo", {}).get("title", "제목 없음")
        for item in data.get("items", [])
    ]
    return {"keyword": keyword, "titles": titles}


async def fetch_books_multi(keywords: list[str]) -> list[dict]:
    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT * 2) as client:
        return await asyncio.gather(*[_fetch_titles(client, k) for k in keywords])