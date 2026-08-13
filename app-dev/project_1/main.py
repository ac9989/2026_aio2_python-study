from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = BASE_DIR / "maison_livre.db"

app = FastAPI(title="Maison Livre")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


SEED_BOOKS = [
    ("파이썬 입문","김철수",2021,"프로그래밍","파이썬을 처음 만나는 독자를 위해 변수, 조건문, 반복문, 함수와 같은 핵심 문법부터 프로그램을 스스로 구성하는 사고방식까지 차근차근 안내합니다. 짧은 예제와 단계적인 설명을 통해 코드가 어떻게 동작하는지 이해하도록 돕고, 이후 웹 개발이나 데이터 분석으로 확장할 수 있는 탄탄한 기초를 마련해 주는 입문서입니다."),
    ("FastAPI 실전","이영희",2023,"백엔드","FastAPI의 라우팅, 요청과 응답 모델, 데이터 검증, 오류 처리 등 API 서버를 만드는 데 필요한 핵심 요소를 실제 서비스의 흐름에 맞춰 다룹니다. 단순히 기능을 구현하는 데 그치지 않고 읽기 좋은 API 구조와 유지보수하기 좋은 백엔드 설계를 함께 생각하도록 구성한 실전 지향 안내서입니다."),
    ("파이썬 웹개발","김철수",2022,"웹 개발","파이썬을 이용해 웹 요청이 서버에 도착하고 데이터가 처리되어 다시 사용자에게 전달되는 전체 흐름을 이해하도록 돕습니다. 웹의 기본 원리에서 시작해 라우팅, 데이터 처리, API 구성과 서버 구조까지 자연스럽게 연결하며, 파이썬 문법을 실제 웹 서비스로 확장하고 싶은 독자에게 적합합니다."),
    ("데이터 분석 기초","박민수",2020,"데이터","데이터를 수집하고 정리하는 단계부터 의미 있는 정보를 찾아 해석하는 과정까지 데이터 분석의 기본 흐름을 소개합니다. 표와 수치만 바라보는 것이 아니라 어떤 질문을 세우고 어떤 기준으로 결과를 읽어야 하는지에 초점을 맞춰, 분석적 사고의 기초를 익히도록 돕습니다."),
    ("FastAPI로 배우는 백엔드","이영희",2024,"백엔드","FastAPI를 중심으로 현대적인 백엔드 서비스가 어떻게 구성되는지 단계적으로 살펴봅니다. API 설계와 데이터 검증은 물론 애플리케이션 구조, 예외 처리, 데이터베이스 연동을 고려한 개발 흐름까지 연결해 설명하여 작은 프로젝트를 실제 서비스 형태로 발전시키는 감각을 익힐 수 있습니다."),
    ("파이썬 프로그래밍 첫걸음","최지훈",2019,"프로그래밍","코딩 경험이 없는 독자도 부담 없이 시작할 수 있도록 파이썬의 기본 문법을 친절한 순서로 소개합니다. 코드 한 줄이 어떤 의미를 가지는지부터 작은 프로그램을 완성하는 과정까지 따라가며, 프로그래밍에서 중요한 논리적 사고와 문제 해결의 즐거움을 자연스럽게 경험하도록 구성했습니다."),
    ("쉽게 배우는 알고리즘","정수빈",2021,"알고리즘","정렬, 탐색과 같은 대표적인 알고리즘을 통해 컴퓨터가 문제를 해결하는 방식을 이해하도록 돕습니다. 결과만 외우기보다 문제를 작은 단계로 나누고 효율적인 해결책을 선택하는 사고 과정에 초점을 맞춰, 코딩 테스트와 실제 프로그래밍 모두에 활용할 수 있는 기반을 제공합니다."),
    ("자료구조의 이해","한민재",2018,"컴퓨터 과학","리스트, 스택, 큐, 트리 등 프로그램에서 자주 사용되는 핵심 자료구조의 특징과 동작 원리를 설명합니다. 각각의 구조가 어떤 상황에서 유리한지 비교하면서 데이터를 효율적으로 저장하고 다루는 방법을 익힐 수 있도록 구성한 컴퓨터 과학 기초서입니다."),
    ("웹 개발의 정석","윤서연",2022,"웹 개발","브라우저에서 보이는 화면부터 서버가 데이터를 처리하는 과정까지 웹 애플리케이션을 이루는 주요 요소를 폭넓게 소개합니다. HTML, CSS, JavaScript와 서버의 역할을 하나의 흐름으로 연결해 이해하도록 하며, 웹 개발 전체 지도를 먼저 그리고 싶은 독자에게 좋은 출발점이 됩니다."),
    ("자바스크립트 기초","오현우",2020,"프론트엔드","웹 페이지에 움직임과 상호작용을 더하는 자바스크립트의 핵심 문법을 기초부터 익힙니다. 변수, 함수, 배열과 객체를 비롯해 DOM과 이벤트 처리까지 자연스럽게 연결하여, 정적인 HTML 페이지를 사용자의 행동에 반응하는 웹 경험으로 발전시키는 방법을 배울 수 있습니다."),
]
# 나머지 초기 도서는 첫 실행 시 자동 생성됩니다.
TOPICS = [
    ("모던 자바스크립트","오현우","프론트엔드"),("HTML과 CSS 디자인","윤서연","프론트엔드"),
    ("프론트엔드 개발 입문","강민서","프론트엔드"),("React 시작하기","강민서","프론트엔드"),
    ("React 실전 프로젝트","강민서","프론트엔드"),("Vue 웹 개발","조성민","프론트엔드"),
    ("Node.js 서버 개발","장유진","백엔드"),("Express 백엔드 개발","장유진","백엔드"),
    ("REST API 설계","이영희","백엔드"),("API 개발 실전","이영희","백엔드"),
    ("SQL 첫걸음","박민수","데이터베이스"),("SQL 데이터 분석","박민수","데이터"),
    ("데이터베이스 입문","한민재","데이터베이스"),("MySQL 실전 가이드","한민재","데이터베이스"),
    ("PostgreSQL 완벽 가이드","정수빈","데이터베이스"),("데이터베이스 설계 원리","한민재","데이터베이스"),
    ("NoSQL 데이터베이스","최지훈","데이터베이스"),("MongoDB 시작하기","최지훈","데이터베이스"),
    ("Redis 활용 가이드","장유진","데이터베이스"),("데이터 모델링 실전","박민수","데이터"),
    ("데이터 과학 입문","서하늘","데이터"),("파이썬 데이터 분석","서하늘","데이터"),
    ("Pandas 데이터 처리","서하늘","데이터"),("NumPy 기초와 활용","김철수","데이터"),
    ("데이터 시각화 입문","박민수","데이터"),("Matplotlib 실전","박민수","데이터"),
    ("통계학과 데이터 분석","서하늘","데이터"),("빅데이터 분석 기초","임도윤","데이터"),
    ("빅데이터 처리 기술","임도윤","데이터"),("데이터 엔지니어링 입문","임도윤","데이터"),
    ("인공지능 첫걸음","신예린","AI"),("머신러닝 입문","신예린","AI"),
    ("파이썬 머신러닝","신예린","AI"),("머신러닝 실전 프로젝트","신예린","AI"),
    ("딥러닝의 이해","배준호","AI"),("딥러닝 실전","배준호","AI"),("신경망 기초","배준호","AI"),
    ("자연어 처리 입문","신예린","AI"),("컴퓨터 비전 기초","배준호","AI"),("생성형 AI의 이해","신예린","AI"),
    ("ChatGPT 활용법","문지호","AI"),("프롬프트 엔지니어링","문지호","AI"),
    ("LLM 애플리케이션 개발","문지호","AI"),("AI 서비스 개발","신예린","AI"),
    ("인공지능과 미래 사회","유채원","AI"),("AI 시대의 개발자","유채원","AI"),
    ("머신러닝 알고리즘","정수빈","AI"),("추천 시스템 입문","신예린","AI"),
    ("AI 데이터 분석","서하늘","AI"),("딥러닝 모델 설계","배준호","AI"),
    ("Git과 GitHub 입문","최지훈","개발 도구"),("Git 협업 가이드","최지훈","개발 도구"),
    ("개발자를 위한 리눅스","조성민","시스템"),("리눅스 서버 관리","조성민","시스템"),
    ("Docker 시작하기","장유진","DevOps"),("Docker 실전 운영","장유진","DevOps"),
    ("쿠버네티스 입문","임도윤","DevOps"),("쿠버네티스 실전","임도윤","DevOps"),
    ("클라우드 컴퓨팅 입문","유채원","클라우드"),("AWS 클라우드 실전","유채원","클라우드"),
    ("DevOps 시작하기","임도윤","DevOps"),("CI CD 파이프라인","임도윤","DevOps"),
    ("소프트웨어 공학 입문","한민재","소프트웨어"),("객체지향 프로그래밍","김철수","소프트웨어"),
    ("클린 코드 작성법","최지훈","소프트웨어"),("리팩터링 실전 가이드","최지훈","소프트웨어"),
    ("디자인 패턴 입문","정수빈","소프트웨어"),("소프트웨어 아키텍처","정수빈","소프트웨어"),
    ("마이크로서비스 설계","이영희","백엔드"),("백엔드 아키텍처 실전","이영희","백엔드"),
    ("컴퓨터 네트워크 기초","조성민","컴퓨터 과학"),("HTTP 완벽 이해","장유진","웹 개발"),
    ("웹 보안 입문","윤서연","보안"),("정보보안 기초","조성민","보안"),
    ("운영체제의 이해","한민재","컴퓨터 과학"),("컴퓨터 구조 입문","한민재","컴퓨터 과학"),
    ("알고리즘 문제 해결","정수빈","알고리즘"),("코딩 테스트 준비","정수빈","알고리즘"),
    ("파이썬 코딩 테스트","김철수","알고리즘"),("개발자 면접 가이드","최지훈","커리어"),
    ("Java 프로그래밍 입문","송지민","프로그래밍"),("Java 객체지향 개발","송지민","프로그래밍"),
    ("Spring Boot 입문","송지민","백엔드"),("Spring Boot 실전","송지민","백엔드"),
    ("C언어 프로그래밍","한민재","프로그래밍"),("C++ 프로그래밍 기초","한민재","프로그래밍"),
    ("TypeScript 시작하기","오현우","프론트엔드"),("TypeScript 실전 개발","오현우","프론트엔드"),
    ("풀스택 웹 개발","윤서연","웹 개발"),("현대 웹 애플리케이션 개발","윤서연","웹 개발")
]

class Donation(BaseModel):
    title: str
    author: str
    year: int
    category: str = "기증 도서"
    description: str = ""

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL,
                category TEXT NOT NULL DEFAULT '기증 도서',
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        count = con.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        if count == 0:
            rows = list(SEED_BOOKS)
            years = [2023,2019,2022,2023,2025,2022,2021,2023,2020,2025,2018,2022,2017,2021,2024,2019,2022,2023,2024,2020,
                     2019,2021,2022,2020,2023,2021,2018,2020,2023,2025,2019,2020,2022,2024,2021,2023,2018,2022,2020,2025,
                     2023,2024,2025,2024,2021,2025,2020,2023,2024,2025,2019,2022,2018,2021,2020,2023,2021,2024,2019,2023,
                     2020,2022,2017,2018,2021,2024,2019,2023,2022,2025,2016,2020,2021,2018,2017,2016,2022,2024,2023,2025,
                     2018,2020,2022,2024,2015,2019,2022,2024,2023,2025]
            for i, (title, author, category) in enumerate(TOPICS):
                year = years[i]
                desc = f"{title}은(는) {category} 분야를 처음 접하는 독자부터 한 단계 더 깊이 이해하고 싶은 독자까지 편안하게 따라갈 수 있도록 구성한 책입니다. 핵심 개념을 단순히 나열하기보다 왜 필요한지, 실제 개발과 학습 과정에서 어떻게 연결되는지를 중심으로 설명합니다. 기본 원리와 대표적인 활용 사례를 함께 살펴볼 수 있어 개념을 정리하거나 실무 감각을 다지는 데 도움이 됩니다. 한 번 읽고 끝내기보다 필요한 순간 다시 펼쳐 참고할 수 있는 실용적인 안내서로, {category} 분야의 흐름을 차분하게 익히고 싶은 독자에게 어울립니다."
                rows.append((title, author, year, category, desc))
            con.executemany("INSERT INTO books(title,author,year,category,description) VALUES(?,?,?,?,?)", rows)

init_db()

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/collection")
def collection():
    return FileResponse(STATIC_DIR / "collection.html")

@app.get("/donate")
def donate():
    return FileResponse(STATIC_DIR / "donate.html")

@app.get("/book/{book_id}")
def detail_page(book_id: int):
    return FileResponse(STATIC_DIR / "book-detail.html")

@app.get("/books/search")
def search_books(title: str = "", author: str = "", year: str = ""):
    sql = "SELECT id,title,author,year,category,description FROM books WHERE 1=1"
    params = []
    if title.strip():
        sql += " AND title LIKE ?"
        params.append(f"%{title.strip()}%")
    if author.strip():
        sql += " AND author LIKE ?"
        params.append(f"%{author.strip()}%")
    if year.strip():
        if not year.isdigit():
            raise HTTPException(400, "출판연도는 정수로 입력해 주세요.")
        sql += " AND year = ?"
        params.append(int(year))
    sql += " ORDER BY id"
    with connect() as con:
        return [dict(r) for r in con.execute(sql, params).fetchall()]

@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    with connect() as con:
        row = con.execute("SELECT id,title,author,year,category,description FROM books WHERE id=?", (book_id,)).fetchone()
    if not row:
        raise HTTPException(404, "도서를 찾을 수 없습니다.")
    return dict(row)

@app.post("/books")
def create_book(book: Donation):
    current_year = datetime.now().year
    title = book.title.strip()
    author = book.author.strip()
    category = book.category.strip() or "기증 도서"
    description = book.description.strip()

    if not 1 <= len(title) <= 50:
        raise HTTPException(400, "책 제목은 1글자 이상 50글자 이하로 입력해 주세요.")
    if not 1 <= len(author) <= 30:
        raise HTTPException(400, "저자명은 1글자 이상 30글자 이하로 입력해 주세요.")
    if not 1950 <= book.year <= current_year:
        raise HTTPException(400, f"출판연도는 1950년 이상 {current_year}년 이하의 정수로 입력해 주세요.")
    if len(category) > 30:
        raise HTTPException(400, "분류는 30글자 이하로 입력해 주세요.")
    if len(description) > 1000:
        raise HTTPException(400, "책 설명은 1000글자 이하로 입력해 주세요.")

    with connect() as con:
        duplicate = con.execute(
            "SELECT id FROM books WHERE lower(trim(title))=lower(?) AND lower(trim(author))=lower(?)",
            (title, author)
        ).fetchone()
        if duplicate:
            raise HTTPException(409, "이미 같은 제목과 저자의 도서가 컬렉션에 있습니다. 중복 서적은 등록할 수 없습니다.")
        cur = con.execute(
            "INSERT INTO books(title,author,year,category,description) VALUES(?,?,?,?,?)",
            (title, author, book.year, category, description)
        )
        new_id = cur.lastrowid

    return {"message": "소중한 책이 MAISON LIVRE의 새로운 컬렉션에 등록되었습니다.", "id": new_id}
