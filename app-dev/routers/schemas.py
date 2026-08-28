from pydantic import BaseModel, Field, field_validator

class Publisher(BaseModel):
    name : str = Field(min_length=1, max_length=100,
                       description="출판사 이름",
                       examples=["플레이 출판사"],)
    city : str= Field(default="서울",
                      description="출판사 소재지",
                       examples=["서울"],)


class BookCreate(BaseModel):
    title : str = Field(min_length=1, max_length=100,
        description="도서 제목",
        examples=["처음 시작하는 FastAPI"],)
    author: str = Field(min_length=1, max_length=50,
        description="도서 저자",
        examples=["홍길동"],)
    year  : int = Field(ge=1900, le=2026,
        description="출판 연도",
        examples=[2024],)
    tags : list[str] = Field(default_factory=list,
        description="도서 태그 목록",
        examples=[["파이썬", "웹 개발"]],)
    publisher : Publisher | None = Field(default=None, description="출판사 정보", examples=[{"name": "한빛미디어", "city": "서울"}])


    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str)-> str:
        v = v.strip()
        if not v:
            raise ValueError("제목은 공백일 수 없습니다")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "처음 시작하는 FastAPI",
                    "author": "빌 루바노빅",
                    "year": 2024,
                    "tags": ["python", "backend"],
                    "publisher": {"name": "한빛미디어", "city": "서울"},
                }
            ]   
        }
    }

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author :str| None = Field(default=None, min_length=1, max_length=50)
    year  : int | None = Field(default=None, ge=1900, le=2026,
                            description="출판 연도",
                            examples=[2024],)
    tags : list[str] | None = Field(default=None,
                                description="도서 태그 목록",
                                examples=["python", "web"],)
    publisher : Publisher | None = Field(default=None, description="출판사 정보")


class BookResponse(BookCreate):
    id: int = Field(description="서버가 발급한 도서 번호", examples=[1])

class WeatherResponse(BaseModel):
    latitude: float = Field(description="위도", examples=[36.8])
    longitude: float = Field(description="경도", examples=[127.1])
    temperature: float = Field(description="현재 기온(섭씨)", examples=[28.9])
    time: str = Field(description="관측 시각", examples=["2026-08-04T09:00"])

class GoogleBooks(BaseModel):
    title: str = Field(description="도서 제목", examples=["처음 시작하는 FastAPI"])
    authors: list[str] = Field(default_factory=list, description="저자 목록", examples=[["김영하"]])
    published_date: str = Field(default="", description="발행일", examples=["2024-05-20"])

class ErrorDetail(BaseModel):
    detail: str = Field(description="오류 메시지", examples=["도서를 찾을 수 없습니다"])