# FastAPI 입문 3일차 — 비동기와 외부 API 연동

> [!warning] 이용 조건
> 본 교육자료는 수강생 개인의 학습 목적에 한하여 이용할 수 있으며, 외부 AI 서비스에 업로드하거나 동영상을 포함한 2차 콘텐츠로 제작·재배포하는 행위를 금지합니다. 예외적 이용은 출처 표기, 비상업적 사용, 강사의 사전 동의를 모두 충족하는 경우에 한하여 허용됩니다.

> **교육생 배포용 실습 가이드**
> 이 문서 하나만 따라 하면 3일차 실습을 처음부터 끝까지 완성할 수 있습니다.
> 수업 중 놓친 부분이 있어도 이 문서로 혼자 복습할 수 있도록 모든 결과 코드를 포함했습니다.
>
> **코드 복사 방법 (Obsidian)** — `Ctrl + E`를 눌러 **읽기 모드**로 전환한 뒤, 코드 블록 위에 마우스를 올리면 우측 상단에 복사 버튼이 나타납니다. 편집 모드에서는 보이지 않습니다.

|항목|내용|
|---|---|
|과정|FastAPI 입문 (5일 과정) — 3일차|
|주제|비동기 처리(async/await), 외부 API 호출, 응답 매핑, 오류 처리, 파일 분리|
|예제 앱|도서 관리 API (2일차 `main.py`에 이어서 작업)|
|사용 외부 API|**Open-Meteo**(날씨, 키 불필요) / **Google Books**(도서 검색, 키 필요)|
|선수 조건|2일차 완료 + 선행 자료 「httpx 기초」 완료 + Google Books API 키 발급 완료|

**2일차와 오늘의 차이**

| 구분      | 1·2일차                   | 3일차 (오늘)                                         |
| ------- | ----------------------- | ------------------------------------------------ |
| 데이터 출처  | **내 서버 안**의 `books` 리스트 | **다른 서버**에서 가져옴                                  |
| 기다리는 시간 | 거의 없음 (밀리초)             | 길다 (수백 밀리초 ~ 수 초)                                |
| 함수 정의   | `def`                   | `async def` + `await`                            |
| 실패 가능성  | 내 코드 문제만                | **외부 서버가 죽거나 느릴 수 있음**                           |
| 파일 구성   | `main.py` 한 개           | `main.py` / `schemas.py` / `external_api.py` 세 개 |

> **주의:** Google Books API 키가 아직 없으면 실습 5부터 진행할 수 없습니다.
> 배포용 자료 「Google Books API 키 발급과 설정」을 먼저 완료하세요.
> 실습 1~4는 키 없이 진행할 수 있으므로, 키를 기다리는 동안 먼저 해도 됩니다.

---

## 0. 시작 전 체크리스트

- [ ] 가상환경이 활성화되어 프롬프트 앞에 `(.venv)`가 보인다
- [ ] `01-fastapi-basic` 폴더에 2일차까지 완성한 `main.py`가 있다
- [ ] `fastapi dev main.py` 실행 후 `POST /books`로 도서 등록이 된다
- [ ] `.env` 파일에 `GOOGLE_BOOKS_API_KEY`가 들어 있다 (실습 5부터 필요)
- [ ] `pip show httpx` 실행 시 정보가 출력된다
- [ ] 선행 자료 「httpx 기초」의 실습 5개를 완료했다

> **선행 자료를 먼저 하세요**
> 오늘은 `async`/`await`와 httpx 사용법을 **이미 아는 상태**를 전제로 진행합니다.
> 배포용 자료 「httpx 기초 — 외부 서버에 요청 보내기」를 먼저 완료하세요.
> 그 문서에서 FastAPI 없이 httpx만 따로 익히므로, 오늘 오류가 났을 때 httpx 문제인지 FastAPI 문제인지 구분할 수 있습니다.

> **참고:** `httpx`는 1일차에 설치한 `fastapi[standard]`에 **이미 포함** 되어 있습니다. 따로 설치하지 않아도 됩니다. 확인만 합니다.

```bash
pip show httpx
```

`Name: httpx`와 버전이 출력되면 정상입니다. 아무것도 안 나오면 가상환경이 활성화되지 않은 것입니다.

### 완료 후 폴더 구조

오늘은 `main.py` 하나였던 것을 **세 파일로 나눕니다.** (실습 4)

```
01-fastapi-basic/
├── main.py              엔드포인트 (요청을 받고 응답을 만든다)
├── schemas.py           Pydantic 모델 전부              ← 오늘 새로 만듦
├── external_api.py      외부 API 호출 함수              ← 오늘 새로 만듦
├── sample_books.json    폴백(대체) 데이터               ← 오늘 새로 만듦
├── .env                 API 키·타임아웃 (커밋 금지)
├── .gitignore
└── static/
    ├── index.html               링크 6개 추가
    ├── 01-status.html ~ 12-final.html    1·2일차 완성분
    ├── 13-weather.html          오늘 추가
    ├── 14-weather-input.html    오늘 추가
    ├── 15-loading.html          오늘 추가
    ├── 16-import.html           오늘 추가
    ├── 17-error.html            오늘 추가
    └── 18-multi.html            오늘 추가
```

---

## 1. 왜 비동기인가

### 1-1. 기다리는 시간의 문제

외부 API 호출은 **오래 걸립니다.** 내 서버가 계산하는 시간은 밀리초 단위지만, 다른 서버에 요청을 보내고 응답을 받기까지는 수백 밀리초에서 수 초가 걸립니다.

이 시간 동안 서버는 **아무것도 하지 않고 기다립니다.** 계산 중이 아니라 응답을 기다리는 상태입니다. 이런 대기를 **I/O 대기** 라고 합니다.

|용어|의미|
|---|---|
|**I/O**|Input/Output. 파일 읽기·쓰기, 네트워크 통신처럼 **바깥과 주고받는 작업**|
|**I/O 대기**|그 작업의 응답을 기다리며 아무 일도 못 하는 시간|
|**동기 (Synchronous)**|앞 작업이 끝나야 다음 작업을 시작하는 방식|
|**비동기 (Asynchronous)**|기다리는 동안 다른 작업을 처리하는 방식|

문제는 이 대기 중에 다른 요청이 오면 어떻게 되느냐입니다.
한 사람의 요청을 기다리느라 나머지 사용자를 전부 기다리게 하면 서버가 쓸모없어집니다.

### 1-2. 비동기의 아이디어

비동기 처리는 **"기다리는 동안 다른 일을 하자"** 는 방식입니다. 식당에 비유하면 이렇습니다.

|방식|식당 비유|서버에서는|
|---|---|---|
|**동기**|주문을 받고 그 요리가 완성될 때까지 **서서 기다린 뒤** 다음 손님을 받는다|한 요청의 외부 응답을 기다리는 동안 다른 요청이 전부 대기|
|**비동기**|주문을 주방에 넘기고 **바로 다음 손님을 받는다.** 요리가 나오면 그때 가져다준다|외부 응답을 기다리는 동안 다른 요청을 처리|

주방(외부 API)이 일하는 동안 종업원(서버)은 놀지 않습니다.

**오늘 실습 1에서 이 차이를 초 단위 숫자로 직접 측정합니다.**

---

## 2. async/await 문법

### 2-1. `async def`와 `await`

함수 앞에 `async`를 붙이면 **비동기 함수** 가 됩니다. 그 안에서 기다려야 하는 작업 앞에 `await`를 붙입니다.

```python
import asyncio

@app.get("/wait")
async def wait_example():
    await asyncio.sleep(2)      # 2초 기다림. 그동안 서버는 다른 요청 처리
    return {"message": "2초 후 응답"}
```

|키워드|의미|
|---|---|
|**`async def`**|이 함수는 중간에 **멈췄다가 다시 이어질 수 있다**는 선언|
|**`await`**|**여기서 기다린다.** 기다리는 동안 제어권을 넘겨 다른 요청을 처리하게 한다|
|**`asyncio`**|파이썬 표준 비동기 라이브러리. `asyncio.sleep`은 비동기로 기다리는 함수|

> **주의:** `await`는 **`async def` 안에서만** 쓸 수 있습니다. 일반 `def` 안에서 쓰면 `SyntaxError`가 납니다.

### 2-2. 어디에 `await`를 붙이는가

`await`는 **비동기를 지원하는 작업** 에만 붙입니다. 아무 함수에나 붙이는 것이 아닙니다.

```python
await asyncio.sleep(2)              # 가능. 비동기 대기
await client.get(url)               # 가능. httpx의 비동기 요청
await some_normal_function()        # 불가. 일반 함수에는 붙이지 않음
```

판단 기준은 단순합니다. **라이브러리 문서에 비동기용이라고 되어 있고 `async` 환경에서 쓰라고 안내된 함수** 에 붙입니다.

### 2-3. 가장 위험한 실수

`async def` 안에서 **동기 방식으로 기다리는 코드** 를 쓰면, 비동기의 장점이 사라지는 정도가 아니라 **서버 전체가 멈춥니다.**

```python
import time

@app.get("/bad")
async def bad_example():
    time.sleep(2)        # 위험. 서버 전체가 2초간 정지
    return {"message": "완료"}
```

`time.sleep`은 제어권을 넘기지 않고 그냥 붙잡고 있습니다. 이 2초 동안 **다른 모든 요청이 대기** 합니다.

|비슷해 보이지만 완전히 다른 두 가지|동작|
|---|---|
|`await asyncio.sleep(2)`|제어권을 넘김. 다른 요청 처리 가능|
|`time.sleep(2)`|제어권을 붙잡음. **서버 전체 정지**|

같은 이유로 `async def` 안에서는 `requests` 라이브러리 대신 **`httpx`의 비동기 방식** 을 씁니다.
실습 1에서 이 차이를 직접 측정합니다.

### 2-4. `def`는 어떻게 되는가

지금까지 만든 엔드포인트는 전부 일반 `def`였습니다. FastAPI는 `def` 함수를 **별도 스레드에서 실행** 하므로, 그 안에서 오래 걸리는 작업을 해도 서버 전체가 멈추지는 않습니다.
다만 스레드 수에 한계가 있어 동시 처리량이 비동기보다 적습니다.

|방식|동작|권장 용도|
|---|---|---|
|`async def` + `await`|대기 중 다른 요청 처리|**외부 호출, DB 조회**|
|`def`|별도 스레드에서 실행|계산 위주, 동기 라이브러리 사용 시|
|`async def` + 동기 대기 코드|**서버 전체 정지**|**절대 금지**|

---

## 3. httpx로 외부 호출

### 3-1. 기본 형태

```python
import httpx

async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://example.com/api")
        return response.json()
```

|코드|역할|
|---|---|
|**`httpx`**|파이썬 HTTP 클라이언트 라이브러리. 비동기를 지원함|
|`httpx.AsyncClient()`|요청을 보내는 객체|
|**`async with`**|사용이 끝나면 **연결을 자동으로 정리**합니다|
|`await client.get(...)`|실제 요청. **응답을 기다리는 지점**|
|`response.json()`|응답 본문을 파이썬 딕셔너리로 변환|

### 3-2. 파라미터 전달

주소에 값을 직접 이어 붙이지 않고 **`params`로 넘깁니다.** 특수문자와 한글이 자동으로 처리됩니다.

```python
response = await client.get(
    "https://api.open-meteo.com/v1/forecast",
    params={"latitude": 36.8, "longitude": 127.1, "current": "temperature_2m"}
)
```

> **참고:** 1일차에 브라우저 주소창으로 호출했던 것과 **같은 주소, 같은 파라미터** 입니다.
> 그때는 사람이 주소창에 쳤고, 지금은 서버가 코드로 보냅니다.
> `params`로 넘기면 라이브러리가 `?latitude=36.8&longitude=127.1&...` 형태로 알아서 조립합니다.

---

## 4. 외부 응답 매핑

외부 API의 응답을 **그대로 돌려주면 안 됩니다.** 이유는 세 가지입니다.

1. 응답이 불필요하게 **큽니다.** 클라이언트가 쓰지 않는 필드가 대부분입니다.
2. 외부 서비스가 응답 구조를 바꾸면 **내 API 사용자까지** 영향을 받습니다.
3. 어떤 외부 서비스를 쓰는지 **그대로 드러납니다.**

그래서 필요한 필드만 뽑아 **내 모델** 로 변환합니다. 2일차에 만든 `BookResponse`와 같은 역할입니다.

```python
class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: float
```

외부 응답이 `{"current": {"temperature_2m": 27.8}}` 형태라면, 다음처럼 꺼내 담습니다.

```python
data = response.json()
return WeatherResponse(
    latitude=data["latitude"],
    longitude=data["longitude"],
    temperature=data["current"]["temperature_2m"],
)
```

### 없을 수 있는 필드 처리

외부 데이터는 **항목마다 필드가 다를 수 있습니다.** 예를 들어 Google Books의 도서 정보에는 저자가 없는 경우가 있습니다.
이때 `data["authors"]`로 접근하면 `KeyError`가 나 **500** 이 발생합니다.

`.get()`을 쓰면 없을 때 기본값을 지정할 수 있습니다.

|코드|없을 때 결과|
|---|---|
|`info["authors"]`|**`KeyError` 발생 → 500**|
|`info.get("authors", [])`|빈 리스트 `[]`|
|`info.get("publishedDate", "")`|빈 문자열 `""`|

> **주의:** 이것은 이론이 아니라 **실제로 발생하는 문제** 입니다.
> `keyword=fastapi`로 검색하면 두 번째 항목인 `파이썬 FastAPI 개발 입문`에는 `publishedDate` 키가 **아예 없습니다.**
> 첫 번째·세 번째 항목에는 있기 때문에, 몇 건만 테스트하면 놓치기 쉬운 유형의 오류입니다.

---

## 5. 오류 처리

외부 API는 **반드시 실패한다고 가정** 하고 코드를 씁니다. 서버가 죽거나, 응답이 늦거나, 네트워크가 끊깁니다.

### 5-1. 타임아웃 설정

**타임아웃(timeout)** 은 "이 시간 안에 응답이 없으면 포기한다"는 제한 시간입니다.
타임아웃이 없으면 외부 서버가 응답하지 않을 때 **내 서버도 무한정 기다립니다.**

```python
async with httpx.AsyncClient(timeout=5.0) as client:
    ...
```

5초 안에 응답이 없으면 예외가 발생합니다.

### 5-2. 예외 종류와 대응 상태 코드

|상황|httpx 예외|돌려줄 상태 코드|의미|
|---|---|---|---|
|응답이 너무 늦음|`httpx.TimeoutException`|**`504`**|Gateway Timeout|
|외부 서버가 오류 응답|`httpx.HTTPStatusError`|**`502`**|Bad Gateway|
|연결 실패, DNS 오류|`httpx.RequestError`|**`502`**|Bad Gateway|

**내 서버 잘못이 아니므로 `500`이 아닙니다.**
`502`와 `504`는 "중간에서 전달하는데 **뒤쪽이 문제**"라는 뜻입니다.

|상태 코드|누구 잘못인가|
|---|---|
|`400`·`422`|**요청을 보낸 쪽** (클라이언트)|
|`500`|**내 서버** 코드의 버그|
|`502`·`504`|**외부 서버** 또는 그 사이 네트워크|

### 5-3. 기본 형태

```python
try:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()      # 4xx, 5xx면 예외 발생
        data = response.json()
except httpx.TimeoutException:
    raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
except httpx.HTTPStatusError:
    raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
except httpx.RequestError:
    raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")
```

> **주의:** `raise_for_status()`를 부르지 않으면 외부가 `404`를 줘도 **그냥 넘어갑니다.** 반드시 넣습니다.

---

## 6. 실습 — API 만들기

2일차 `main.py`에 이어서 작성합니다. 실습 1~3은 **준비물이 없고**, 실습 5부터 Google Books 키가 필요합니다.

> **주의:** 새로 만드는 `/books/external` 경로는 반드시 `/books/{book_id}`보다 **위에** 선언합니다.
> 1일차의 리터럴 경로 규칙과 같습니다. 최종 순서는 [7. 전체 완성 코드](#7-전체-완성-코드)에서 확인하세요.

---

### 실습 1. 동기와 비동기 차이 체감

**목표:** `async def` 안에서 동기 대기가 왜 위험한지 **초 단위 숫자로** 확인한다.

**요구사항**
- `GET /slow-async` : `asyncio.sleep(3)` 후 응답 (올바른 비동기 대기)
- `GET /slow-block` : `time.sleep(3)` 후 응답 (잘못된 동기 대기)

**결과 코드**

```python
import asyncio
import time


@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(3)
    return {"type": "async", "message": "3초 대기 완료"}


@app.get("/slow-block")
async def slow_block():
    time.sleep(3)
    return {"type": "block", "message": "3초 대기 완료"}
```

#### 확인 — 왜 브라우저 탭만으로는 안 되는가

브라우저 탭을 여러 개 열어 **같은 주소** 를 실행하는 방식은 동작하지 않습니다.
Chrome이 동일한 주소의 중복 요청을 첫 응답이 올 때까지 대기시키기 때문에, 서버에는 요청이 하나씩 순차로 도착합니다.
그러면 `async` 쪽도 3초, 6초, 9초로 보여 **차이가 드러나지 않습니다.**

#### 방법 1. 주소를 다르게 만들기

탭마다 쿼리 파라미터를 다르게 붙입니다. Chrome이 별개 요청으로 취급합니다.

```
http://127.0.0.1:8000/slow-async?n=1
http://127.0.0.1:8000/slow-async?n=2
http://127.0.0.1:8000/slow-async?n=3
```

세 탭을 **빠르게 연속 실행** 합니다. 엔드포인트 코드를 고칠 필요는 없습니다. 정의하지 않은 쿼리 파라미터는 FastAPI가 무시합니다.

|주소|결과|
|---|---|
|`/slow-async?n=1,2,3`|세 탭이 **거의 동시에** 3초 후 응답|
|`/slow-block?n=1,2,3`|3초, 6초, 9초로 **순차 응답**|

#### 방법 2. 콘솔에서 시간 측정 (권장)

시간이 숫자로 나와 더 명확합니다.

1. `http://127.0.0.1:8000/docs`를 엽니다.
2. `F12`를 눌러 `Console` 탭으로 갑니다.
3. 프롬프트에 `allow pasting`을 **손으로 직접 입력** 하고 Enter를 누릅니다.
4. 아래 코드를 붙여 넣고 Enter를 누릅니다.

```javascript
async function test(path, count = 3) {
  const start = performance.now();
  await Promise.all(
    Array.from({ length: count }, (_, i) =>
      fetch(path + "?n=" + i, { cache: "no-store" })
    )
  );
  console.log(path, "동시", count, "건:", ((performance.now() - start) / 1000).toFixed(2), "초");
}

await test("/slow-async");
await test("/slow-block");
```

**확인:** 콘솔에 아래와 같이 출력된다. (실제 측정 결과)

```
/slow-async 동시 3 건: 3.05 초
/slow-block 동시 3 건: 9.03 초
```

`/slow-async`는 3건을 **동시에 처리해 총 3초**, `/slow-block`은 **하나씩 처리해 9초** 가 걸립니다.
이것이 비동기 함수 안에서 동기 대기를 쓴 결과입니다.

확인 후 `/slow-block`은 남겨 두되, **실제 코드에서는 이런 패턴을 쓰지 않습니다.**

---

### 실습 2. 외부 API 첫 호출 (Open-Meteo)

**목표:** httpx로 외부 데이터를 가져와 그대로 반환한다.

**요구사항**
- `GET /weather/raw` : 천안 좌표(36.8, 127.1)의 현재 날씨를 조회해 **원본 JSON 그대로** 반환

**결과 코드**

```python
import httpx


@app.get("/weather/raw")
async def weather_raw():
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 36.8,
                "longitude": 127.1,
                "current": "temperature_2m",
            },
        )
        return response.json()
```

#### `async def`, `async with`, `await` — 세 가지의 역할 구분

위 코드 한 곳에 `async`가 세 번 나옵니다. **같은 말이 아니라 층위가 다른 세 가지** 입니다.

|문법|무엇에 붙나|뜻|위 코드에서|
|---|---|---|---|
|**`async def`**|**함수 전체**|이 함수는 중간에 멈췄다 이어질 수 **있다** (자격 선언)|`async def weather_raw():`|
|**`async with`**|함수 안의 **한 블록**|이 블록의 **정리 작업 자체가** 기다림이 필요하다|`async with httpx.AsyncClient(...) as client:`|
|**`await`**|**한 줄(식)**|**여기서 실제로 기다린다**|`await client.get(...)`|

`async def`는 "기다릴 수 있는 함수"라고 **선언만** 합니다. 어디서 기다릴지는 지정하지 않으므로, 실제로 기다리는 지점마다 `await`나 `async with`를 따로 써야 합니다.

`async with`가 필요한 이유는 **블록을 빠져나갈 때 하는 일이 연결 정리(소켓 닫기)** 이고, 그것도 네트워크 작업이라 기다려야 하기 때문입니다.

> **주의:** `async with`를 그냥 `with`로 쓰면 아래 오류가 납니다.
>
> `TypeError: 'AsyncClient' object does not support the context manager protocol`
>
> `with`와 `async with`는 서로 다른 규약을 찾습니다. `AsyncClient`는 비동기 쪽만 제공합니다.

> **참고:** `async def` 안이라고 모든 `with`가 `async with`인 것은 아닙니다.
> 실습 7의 `load_fallback_books`에서는 파일을 열 때 그냥 `with open(...)`을 씁니다. 파일 닫기는 기다릴 일이 없기 때문입니다.
> 판단 기준은 "`async def` 안인가"가 아니라 **"그 라이브러리가 `async with`로 쓰라고 안내하는가"** 입니다.
>
> 더 자세한 원리는 강의용 원본 문서 「FastAPI 입문 3일차」의 `async with`가 필요한 이유 절을 참고하세요.

**확인:** `/docs`를 새로고침하고 `GET /weather/raw`를 펼쳐 `Try it out` → `Execute`. `Code`가 `200`이고 `Response body`에 아래와 비슷한 JSON이 나온다.

```json
{
  "latitude": 36.8,
  "longitude": 127.125,
  "generationtime_ms": 0.03,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "timezone_abbreviation": "GMT",
  "elevation": 42.0,
  "current_units": {"time": "iso8601", "interval": "seconds", "temperature_2m": "°C"},
  "current": {"time": "2026-08-04T00:00", "interval": 900, "temperature_2m": 28.9}
}
```

`current` 안의 `temperature_2m` 값이 실제 기온입니다.
**우리가 쓸 값은 3~4개인데 응답에는 10개가 넘는 필드가 들어 있다**는 점을 확인하세요. 다음 실습에서 이걸 줄입니다.

---

### 실습 3. 응답 매핑

**목표:** 필요한 필드만 뽑아 내 모델로 변환하고, 좌표를 파라미터로 받는다.

**요구사항**
- `WeatherResponse` 모델 정의 (`latitude`, `longitude`, `temperature`, `time`)
- `GET /weather?latitude=...&longitude=...` : 기본값은 천안 좌표

**힌트:** 중첩된 값은 `data["current"]["temperature_2m"]`처럼 두 단계로 꺼낸다.

**결과 코드**

```python
class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    time: str


@app.get("/weather", response_model=WeatherResponse)
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
            },
        )
        data = response.json()

    return WeatherResponse(
        latitude=data["latitude"],
        longitude=data["longitude"],
        temperature=data["current"]["temperature_2m"],
        time=data["current"]["time"],
    )
```

**확인:** `/docs`에서 `GET /weather`를 펼쳐 `Try it out` → 기본값 그대로 `Execute`.

|입력|`Code`|`Response body`|
|---|---|---|
|기본값 (36.8 / 127.1)|`200`|**네 필드만** 나옴 (`latitude`, `longitude`, `temperature`, `time`)|
|서울 (37.57 / 126.98)|`200`|좌표와 기온이 달라짐|
|부산 (35.18 / 129.08)|`200`|좌표와 기온이 달라짐|

실습 2의 `/weather/raw`와 나란히 실행해 **응답 크기 차이** 를 비교해 보세요.

---

### 실습 4. 파일 분리

**목표:** 한 파일에 몰려 있던 코드를 역할별로 나눈다.

`main.py`가 250줄을 넘겼습니다. 여기서 외부 API를 하나 더 붙이면 원하는 코드를 찾기 어려워집니다. 세 파일로 나눕니다.

```
01-fastapi-basic/
  main.py            엔드포인트. 요청을 받고 응답을 만든다
  schemas.py         Pydantic 모델 전부
  external_api.py    외부 API 호출 함수
  static/
  .env
```

기준은 **"무엇을 담당하는가"** 입니다.
`external_api.py`는 **데이터를 가져오는 방법** 을, `main.py`는 **그 결과를 사용자에게 어떻게 전달할지** 를 담당합니다.

#### 4-1. `schemas.py` 만들기

`main.py`에 있던 모델 정의를 **전부 옮깁니다.** 옮긴 뒤 `main.py`에서는 지웁니다.

```python
from pydantic import BaseModel, Field, field_validator


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


class BookResponse(BookCreate):
    id: int


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    time: str
```

#### 4-2. `external_api.py` 만들기

실습 3에서 만든 날씨 호출 부분을 함수로 옮깁니다.

```python
import httpx

from schemas import WeatherResponse


async def fetch_weather(latitude: float, longitude: float) -> WeatherResponse:
    async with httpx.AsyncClient(timeout=5.0) as client:
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
```

> **여기서 `HTTPException`을 쓰지 않는 것이 핵심입니다**
> 이 파일은 **FastAPI를 모르는 상태로** 둡니다. "데이터를 가져온다"는 일만 하고,
> 실패를 사용자에게 어떻게 알릴지는 `main.py`가 정합니다.
> 이렇게 두면 나중에 이 함수를 다른 곳에서 재사용하거나 단독으로 테스트하기 쉽습니다.

#### 4-3. `main.py` 수정

파일 맨 위 import를 정리하고, 날씨 엔드포인트를 **함수 호출로** 바꿉니다.

```python
import asyncio
import time

import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles

from external_api import fetch_weather
from schemas import BookCreate, BookResponse, Publisher, WeatherResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/weather", response_model=WeatherResponse)
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    try:
        return await fetch_weather(latitude, longitude)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")
```

엔드포인트가 **5줄로 줄었습니다.** 외부 호출의 세부 사항은 `external_api.py`에 숨었고, 여기에는 "실패하면 어떤 상태 코드를 줄지"만 남았습니다.

**확인:** 터미널에서 `Ctrl + C`로 서버를 끄고 다시 `fastapi dev main.py`를 실행한다. `/docs`에서 `GET /weather`를 `Execute`했을 때 실습 3과 **똑같이** 네 필드가 나오면 성공이다. `/weather/raw`는 실습 2의 학습용이므로 남겨 두거나 지운다.

#### 4-4. 실행 위치 주의

`from schemas import ...`는 **`main.py`와 같은 폴더에서 실행할 때만** 동작합니다.

```bash
cd 01-fastapi-basic
fastapi dev main.py
```

> **주의:** 상위 폴더에서 `fastapi dev 01-fastapi-basic/main.py`로 실행하면
> `ModuleNotFoundError: No module named 'schemas'`가 납니다.
> **파일을 나눈 뒤 가장 자주 겪는 오류입니다.**

#### 4-5. import 누락 점검

파일을 나눈 뒤로는 **새 모델이나 함수를 만들 때마다 import 줄을 함께 고쳐야 합니다.**
한 파일일 때는 없던 단계라 계속 빠뜨리게 됩니다.

아래는 실습 5~8에서 추가되는 항목입니다. **해당 실습에 도달했을 때 추가합니다.**
미리 전부 넣으면 아직 존재하지 않는 함수를 가져오려 해 `ImportError: cannot import name ...`이 납니다.

|실습|추가하는 것|정의 위치|import 해야 하는 곳|
|---|---|---|---|
|5|`ExternalBook`|`schemas.py`|`main.py`, `external_api.py`|
|5|`fetch_books`|`external_api.py`|`main.py`|
|7|`load_fallback_books`|`external_api.py`|`main.py`|
|8|`fetch_books_multi`|`external_api.py`|`main.py`|

각 실습은 **`schemas.py` 또는 `external_api.py`에 먼저 추가하고, 그다음 `main.py`에서 import** 하는 순서로 진행합니다. 반대로 하면 매번 `ImportError`를 보게 됩니다.

오류는 세 종류로 나뉩니다.

|오류|의미|
|---|---|
|`ModuleNotFoundError: No module named 'external_api'`|**파일이 없거나** 실행 폴더가 다름|
|`ImportError: cannot import name 'fetch_books'`|파일은 있는데 **그 이름이 아직 없음**|
|`NameError: name 'fetch_books' is not defined`|함수는 있는데 **import 줄에 안 넣음**|

`NameError`는 다시 두 갈래입니다.

|쓰인 위치|증상|
|---|---|
|모듈 최상단 (데코레이터 등)|**서버가 뜨지 않음**|
|함수 안|서버는 뜨고, 그 엔드포인트를 호출할 때 **500**|

후자가 더 늦게 발견되므로 주의합니다.

> **참고:** VS Code를 쓰면 이름 위에 커서를 두고 `Ctrl + .`을 눌러 `Add import from "schemas"` 제안을 받을 수 있습니다.
> 실행 전에 `문제` 패널(`Ctrl + Shift + M`)을 확인하는 습관을 들이세요. `"..." is not defined` 경고가 있으면 그 줄이 실행되는 순간 오류가 납니다.

---

### 실습 5. Google Books 도서 검색

**목표:** 키를 환경변수로 관리하고 외부 도서 검색을 붙인다.

> **주의:** **선행 조건** — 배포용 자료 「Google Books API 키 발급과 설정」을 완료해 `.env` 파일에 키가 있어야 합니다.

**요구사항**
- `ExternalBook` 모델 정의 (`title`, `authors`, `published_date`)
- `GET /books/external?keyword=...&limit=5` : Google Books에서 검색해 세 필드만 반환

**1) `schemas.py`에 모델을 추가합니다.**

```python
class ExternalBook(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    published_date: str = ""
```

**2) `external_api.py`에 호출 함수를 추가합니다.** 키를 읽는 코드도 여기에 둡니다.

```python
import os

import httpx
from dotenv import load_dotenv

from schemas import ExternalBook, WeatherResponse

load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

if not GOOGLE_BOOKS_API_KEY:
    print("경고: GOOGLE_BOOKS_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")


async def fetch_books(keyword: str, limit: int = 5) -> list[ExternalBook]:
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
            ExternalBook(
                title=info.get("title", "제목 없음"),
                authors=info.get("authors", []),
                published_date=info.get("publishedDate", ""),
            )
        )
    return result
```

**3) `main.py`에 엔드포인트를 추가합니다.**

```python
from external_api import fetch_books, fetch_weather
from schemas import BookCreate, BookResponse, ExternalBook, Publisher, WeatherResponse


# 리터럴 경로이므로 /books/{book_id}보다 먼저 선언한다
@app.get("/books/external", response_model=list[ExternalBook])
async def search_external_books(keyword: str, limit: int = 5):
    return await fetch_books(keyword, limit)
```

> **`.get()`을 세 번이나 쓴 이유**
> - 검색 결과가 없으면 응답에 **`items` 자체가 없습니다.** → `data.get("items", [])`
> - 도서에 따라 `volumeInfo`가 비어 있을 수 있습니다. → `item.get("volumeInfo", {})`
> - 도서에 따라 `authors`나 `publishedDate`가 **없습니다.** → `info.get("authors", [])`
>
> 하나라도 대괄호 접근(`data["items"]`)으로 바꾸면 특정 검색어에서 `KeyError` → **500** 이 납니다.

> **참고:** 도서 한 권의 원본 응답에는 판매 가격, 미리보기 링크, 표지 이미지, 접근 권한, 본문 발췌까지 **40개 이상의 필드** 가 들어 있습니다.
> 여기서 **세 개만 뽑아 쓰는 것** 이 매핑입니다.

**확인:** `/docs`에서 `GET /books/external`을 펼쳐 `Try it out` → `keyword` 칸에 값을 넣어 `Execute`.

|`keyword` 입력값|`Code`|`Response body`|
|---|---|---|
|`fastapi`|`200`|도서 5건. 각 항목에 `title`·`authors`·`published_date` 세 필드만|
|`asdkjfhaskdjfh` (없는 말)|`200`|**빈 배열 `[]`** (오류가 아님)|
|`파이썬` (한글)|`200`|한국어 검색도 정상 동작|

`fastapi`로 검색했을 때 **`published_date`가 빈 문자열인 항목** 이 섞여 있는지 확인하세요. `.get()`이 막아준 자리입니다.

---

### 실습 6. 검색 결과 내 목록에 담기

**목표:** 외부 검색 결과를 내 도서 목록에 등록하고, 서로 다른 데이터 형식을 변환한다.

지금까지 도서 관리 API는 외부와 단절돼 있었습니다. 제목·저자·연도를 손으로 입력해야만 데이터가 늘었습니다.
실습 5에서 검색은 되지만 조회하고 끝입니다. 여기서 **"찾은 책을 내 목록에 담는다"** 까지 이어 붙입니다.

**요구사항**
- `POST /books/from-external` : 외부 검색 결과 하나를 받아 `books`에 등록
- 이미 있는 제목이면 `409`
- 저자는 첫 번째만, 연도는 발행일 앞 4자리를 잘라 사용

**결과 코드** — `main.py`에 추가합니다.

```python
@app.post("/books/from-external", response_model=BookResponse, status_code=201)
def create_from_external(book: ExternalBook):
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
    return new_book
```

#### 형식 변환이 필요한 이유

외부 형식과 내부 형식이 **다릅니다.**

|항목|외부 (`ExternalBook`)|내부 (`BookResponse`)|변환 방법|
|---|---|---|---|
|저자|`authors: ["김철수", "이영희"]` **배열**|`author: "김철수"` **단일값**|첫 번째만 사용, 없으면 `"미상"`|
|연도|`published_date: "2024-07-01"` **문자열**|`year: 2024` **정수**|앞 4자리를 잘라 정수 변환|
|식별자|**없음**|`id` **필수**|서버가 발급|

> **주의:** `isdigit()` 검사를 넣은 이유가 중요합니다.
> 실습 5에서 확인했듯 `파이썬 FastAPI 개발 입문`은 `publishedDate`가 아예 없어 **빈 문자열** 이 됩니다.
> 검사 없이 `int(book.published_date[:4])`를 실행하면 `ValueError`가 발생해 **500** 이 납니다.

> **참고:** `create_from_external`이 `async def`가 **아닌** 이유는 **외부 호출이 없기 때문** 입니다.
> 전달받은 데이터를 리스트에 넣기만 하므로 `def`로 충분합니다.
> `async`는 "기다릴 일이 있을 때" 쓰는 것이지, 무조건 붙이는 것이 아닙니다.

**확인:**

1. `/docs`에서 `GET /books/external`을 `keyword=fastapi`로 `Execute`한다.
2. `Response body`에서 **항목 하나를 통째로 복사** 한다. 예: `{"title": "처음 시작하는 FastAPI", "authors": ["빌 루바노빅"], "published_date": "2024-07-01"}`
3. `POST /books/from-external`을 펼쳐 `Try it out` → `Request body`에 붙여 넣고 `Execute`. `Code`가 `201`이고 `id`·`year`·`author`가 채워져 돌아온다.
4. `GET /books`를 `Execute`해 목록이 한 건 늘었는지 본다. `tags`에 `["외부검색"]`이 붙어 있다.
5. **같은 내용을 한 번 더** `Execute`한다. `Code`가 `409`, `detail`이 `"이미 등록된 제목입니다"`로 나온다.

---

### 실습 7. 오류 처리와 폴백

**목표:** 외부 API 실패를 상태 코드로 구분하고, 장애 시 대체 데이터를 쓴다.

지금까지 만든 외부 호출은 **상대 서버가 정상이라고 가정** 합니다. 실제로는 응답이 늦거나, 오류를 주거나, 연결 자체가 안 될 수 있습니다.

|용어|의미|
|---|---|
|**폴백 (Fallback)**|주된 방법이 실패했을 때 쓰는 **대체 수단**. 여기서는 미리 저장해 둔 파일|

**1) 폴백 파일을 만듭니다.** `main.py`와 같은 폴더에 `sample_books.json`을 만듭니다.

```json
[
  {"title": "처음 시작하는 FastAPI", "authors": ["빌 루바노빅"], "published_date": "2024-07-01"},
  {"title": "파이썬 FastAPI 개발 입문", "authors": ["나카무라 쇼"], "published_date": ""},
  {"title": "기획에서 출시까지 FastAPI 개발 백서", "authors": ["차경묵"], "published_date": "2025-11-21"}
]
```

**2) `external_api.py`에 폴백 로더를 추가합니다.**

```python
import json
from pathlib import Path

from schemas import ExternalBook


def load_fallback_books() -> list[ExternalBook]:
    path = Path(__file__).parent / "sample_books.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [ExternalBook(**item) for item in raw]
```

> **참고:** `Path(__file__).parent`를 쓴 이유는 **실행 위치와 무관하게** 파일을 찾기 위해서입니다.
> 그냥 `"sample_books.json"`으로 열면 **터미널의 현재 폴더 기준** 이라 실행 위치에 따라 실패합니다.
> `__file__`은 "이 파이썬 파일 자신의 경로"를 뜻합니다.

**3) `main.py`의 검색 엔드포인트에 예외 처리를 붙입니다.** 오류를 어떤 상태 코드로 바꿀지는 `main.py`의 책임입니다.

```python
from external_api import fetch_books, fetch_weather, load_fallback_books


@app.get("/books/external", response_model=list[ExternalBook])
async def search_external_books(keyword: str, limit: int = 5, fallback: bool = False):
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
```

파일을 나눈 효과가 여기서 드러납니다. **오류 처리가 붙어 코드가 길어져도 외부 호출 로직은 전혀 건드리지 않았습니다.**

#### 7-1. 타임아웃을 설정으로 빼기

이제 `504`가 실제로 나오는지 확인해야 하는데, 그러려면 타임아웃을 아주 짧게 만들어야 합니다.
이때 **`external_api.py`를 직접 고치면 안 됩니다.** 테스트할 때마다 소스를 편집하는 것은 좋지 않고, 되돌리는 것을 잊으면 수업 내내 오류가 납니다.

**타임아웃은 코드가 아니라 설정입니다.** `.env`로 옮깁니다.

`.env`에 한 줄 추가합니다.

```
GOOGLE_BOOKS_API_KEY=발급받은키
EXTERNAL_TIMEOUT=5.0
```

`external_api.py`에서 읽습니다.

```python
EXTERNAL_TIMEOUT = float(os.getenv("EXTERNAL_TIMEOUT", "5.0"))
```

|코드 조각|의미|
|---|---|
|`os.getenv("이름", "5.0")`|두 번째 인자는 **값이 없을 때 쓸 기본값**. `.env`에 없어도 5초로 동작|
|`float(...)`|**환경변수는 항상 문자열** 로 들어오므로 숫자로 변환해야 함|

`fetch_weather`와 `fetch_books`의 `timeout=5.0`을 **모두** 바꿉니다.

```python
async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT) as client:
```

> **참고:** API 키만 `.env`에 두면 "비밀 값 보관소"로 오해하기 쉽습니다.
> 타임아웃처럼 **비밀이 아닌 설정** 도 여기 두는 것이 원래 용도입니다.
> 실무에서는 개발과 운영 환경에 서로 다른 타임아웃을 주는 식으로 활용합니다.

#### 7-2. 확인 절차

**확인:** 아래 순서대로 진행한다.

1. `.env`의 값을 아래로 바꾸고 **서버를 재시작** 한다.

```
EXTERNAL_TIMEOUT=0.001
```

> **주의:** `fastapi dev`는 `.env` 변경을 **감지하지 못합니다.** 반드시 `Ctrl + C` 후 다시 실행하세요.

2. `/docs`에서 `GET /books/external`을 펼치고 `Try it out`을 누른다.
3. `keyword`에 `fastapi`, `fallback`은 `false`인 상태로 `Execute`.
   → `Code`가 **`504`**, `detail`이 `"외부 API 응답이 지연됩니다"`
4. `fallback`을 `true`로 바꿔 다시 `Execute`.
   → `Code`가 **`200`**, `sample_books.json`의 **3권** 이 나옴
5. `.env`를 `EXTERNAL_TIMEOUT=5.0`으로 되돌리고 **서버를 재시작** 한다.
6. 다시 `Execute`해 실제 검색 결과가 나오는지 확인한다.

주소로 직접 호출해도 됩니다. `fallback`은 쿼리 파라미터이므로 주소 끝에 붙입니다.

```
http://127.0.0.1:8000/books/external?keyword=fastapi
http://127.0.0.1:8000/books/external?keyword=fastapi&fallback=true
```

첫 파라미터 앞에는 `?`, 두 번째부터는 `&`를 씁니다.

> **참고:** 불리언 값은 **대소문자를 가리지 않습니다.**
> `true`, `True`, `1`, `yes`, `on`이 모두 참으로, `false`, `False`, `0`, `no`, `off`가 거짓으로 처리됩니다.
> URL에서는 소문자 `true`가 관례입니다.

> **`fallback`의 기본값이 `False`인 이유**
> 기본값이 `True`면 외부 API가 죽어도 `200`과 함께 예비 데이터가 나가 **장애가 조용히 숨겨집니다.**
> 폴백은 호출하는 쪽이 **명시적으로 요청할 때만** 동작해야 합니다.

---

### 실습 8. 동시 호출

**목표:** 여러 외부 호출을 동시에 처리해 시간 차이를 확인한다.

실습 1에서 비동기의 원리를 봤다면, 여기서는 **실제 외부 호출에 적용** 합니다.

**요구사항**
- `GET /books/external/multi?keywords=python,fastapi,django` : 여러 키워드를 동시에 검색
- 응답에 서버 처리 시간(`elapsed_seconds`) 포함

**1) `external_api.py`에 동시 검색 함수를 추가합니다.**

```python
import asyncio


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
```

|코드|의미|
|---|---|
|**`asyncio.gather`**|여러 비동기 작업을 **동시에 실행** 하고 전부 끝날 때까지 기다림|
|`*[...]`|리스트를 **개별 인자로 펼쳐서** 전달하는 문법|
|`_fetch_titles` (밑줄)|**이 파일 안에서만 쓰는 보조 함수** 라는 관례상 표시|
|`EXTERNAL_TIMEOUT * 2`|동시 호출은 요청을 한꺼번에 보내므로 **단건보다 여유** 를 둠|

**2) `main.py`에 엔드포인트를 추가합니다.**

```python
import time

from external_api import fetch_books, fetch_books_multi, fetch_weather, load_fallback_books


@app.get("/books/external/multi")
async def search_multi(keywords: str = "python,fastapi,django"):
    words = [w.strip() for w in keywords.split(",") if w.strip()]

    start = time.perf_counter()
    results = await fetch_books_multi(words)
    elapsed = round(time.perf_counter() - start, 2)

    return {"elapsed_seconds": elapsed, "results": results}
```

키워드 3개를 **순차로** 호출하면 각 호출 시간의 **합** 이 걸리지만, `gather`를 쓰면 **가장 오래 걸린 하나의 시간** 만 듭니다.

**확인:** `/docs`에서 `GET /books/external/multi`를 펼쳐 `Try it out` → `keywords` 값을 바꿔 가며 `Execute`하고 `elapsed_seconds`를 비교한다.

|`keywords` 입력값|키워드 수|`elapsed_seconds` 경향|
|---|---|---|
|`python,fastapi`|2개|기준값|
|`python,fastapi,django`|3개|거의 그대로|
|`python,fastapi,django,flask,react,vue`|6개|**개수에 비례해 늘지 않음**|

개수를 3배로 늘려도 시간이 3배가 되지 않으면 **동시 처리가 되고 있는 것** 입니다.
순차 처리라면 6개일 때 2개의 3배가 나와야 합니다.

---

### 심화 (시간이 남을 때)

- 실습 8의 동시 호출을 **순차 버전** 으로도 만들어 시간을 직접 비교한다.
- `ExternalBook`에 `thumbnail` 필드를 추가한다. 값은 `volumeInfo.imageLinks.thumbnail`에 있고, 이 역시 없는 도서가 있으므로 `info.get("imageLinks", {}).get("thumbnail", "")`처럼 **두 단계로** 꺼낸다. 웹 실습에서 `<img>`로 표지를 표시하면 화면이 크게 달라진다.
- `publisher`, `pageCount`, `categories`도 같은 방식으로 추가해 본다.
- 실습 6의 저자 변환을 개선한다. 저자가 여러 명이면 쉼표로 이어 붙이거나, `author` 필드 대신 목록을 유지하도록 내부 모델을 바꾼다.
- `books` 리스트를 `database.py`로 분리한다. 나중에 실제 데이터베이스로 바꿀 지점이 어디인지 드러난다.
- `httpx.AsyncClient`를 요청마다 만들지 않고 앱 전체가 공유하도록 바꾼다. (연결 재사용)
- 검색 결과를 캐시해 같은 키워드 재검색 시 외부 호출을 생략한다.

---

## 7. 전체 완성 코드

3일차까지의 최종 상태입니다. 세 파일로 나뉩니다.

### 7-1. `schemas.py`

```python
from pydantic import BaseModel, Field, field_validator


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


class BookResponse(BookCreate):
    id: int


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    time: str


class ExternalBook(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    published_date: str = ""
```

### 7-2. `external_api.py`

```python
import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from schemas import ExternalBook, WeatherResponse

load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
EXTERNAL_TIMEOUT = float(os.getenv("EXTERNAL_TIMEOUT", "5.0"))

if not GOOGLE_BOOKS_API_KEY:
    print("경고: GOOGLE_BOOKS_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")


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


async def fetch_books(keyword: str, limit: int = 5) -> list[ExternalBook]:
    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT) as client:
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
            ExternalBook(
                title=info.get("title", "제목 없음"),
                authors=info.get("authors", []),
                published_date=info.get("publishedDate", ""),
            )
        )
    return result


def load_fallback_books() -> list[ExternalBook]:
    path = Path(__file__).parent / "sample_books.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [ExternalBook(**item) for item in raw]


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
```

### 7-3. `main.py`

리터럴 경로(`/books/search`, `/books/filter`, `/books/page`, `/books/external`, `/books/external/multi`, `/books/from-external`)가 `/books/{book_id}`보다 **위** 에 있는 순서에 주의합니다.

```python
import asyncio
import time

import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles

from external_api import (
    fetch_books,
    fetch_books_multi,
    fetch_weather,
    load_fallback_books,
)
from schemas import (
    BookCreate,
    BookResponse,
    ExternalBook,
    Publisher,
    WeatherResponse,
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

books = [
    {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021, "tags": [], "publisher": None},
    {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023, "tags": [], "publisher": None},
    {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022, "tags": [], "publisher": None},
    {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020, "tags": [], "publisher": None},
    {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year": 2024, "tags": [], "publisher": None},
]


@app.get("/")
def read_root():
    return {"message": "FastAPI 첫 서버"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/info")
def info():
    return {"name": "도서 관리 API", "version": "0.3.0"}


# --- 실습 1: 동기와 비동기 비교용 (학습 목적) ---
@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(3)
    return {"type": "async", "message": "3초 대기 완료"}


@app.get("/slow-block")
async def slow_block():
    time.sleep(3)
    return {"type": "block", "message": "3초 대기 완료"}


# --- 날씨 (Open-Meteo) ---
@app.get("/weather/raw")
async def weather_raw():
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 36.8,
                "longitude": 127.1,
                "current": "temperature_2m",
            },
        )
        return response.json()


@app.get("/weather", response_model=WeatherResponse)
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    try:
        return await fetch_weather(latitude, longitude)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")


# --- 도서 ---
@app.get("/books", response_model=list[BookResponse])
def list_books():
    return books


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")
    new_id = max([b["id"] for b in books], default=0) + 1
    new_book = {"id": new_id, **book.model_dump()}
    books.append(new_book)
    return new_book


# 리터럴 경로는 /books/{book_id}보다 먼저 선언한다
@app.get("/books/search")
def search_books(keyword: str = ""):
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]


@app.get("/books/filter")
def filter_books(author: str = "", sort: str = ""):
    result = books
    if author:
        result = [b for b in result if b["author"] == author]
    if sort == "year":
        result = sorted(result, key=lambda b: b["year"])
    return result


@app.get("/books/page")
def page_books(skip: int = 0, limit: int = 2):
    return books[skip: skip + limit]


@app.get("/books/external", response_model=list[ExternalBook])
async def search_external_books(keyword: str, limit: int = 5, fallback: bool = False):
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


@app.get("/books/external/multi")
async def search_multi(keywords: str = "python,fastapi,django"):
    words = [w.strip() for w in keywords.split(",") if w.strip()]

    start = time.perf_counter()
    results = await fetch_books_multi(words)
    elapsed = round(time.perf_counter() - start, 2)

    return {"elapsed_seconds": elapsed, "results": results}


@app.post("/books/from-external", response_model=BookResponse, status_code=201)
def create_from_external(book: ExternalBook):
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
    return new_book


@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
```

### 7-4. `.env`와 `.gitignore`

`.env`

```
GOOGLE_BOOKS_API_KEY=발급받은키
EXTERNAL_TIMEOUT=5.0
```

`.gitignore`

```
.venv/
__pycache__/
.env
```

> **주의:** `.env`에 API 키가 들어 있으므로 `.gitignore`에 **반드시** 포함합니다.
> 5일차 GitHub 협업에서 이 설정이 없으면 키가 그대로 공개됩니다.

### 7-5. 파일별 역할과 의존 방향

|파일|담당|포함 내용|
|---|---|---|
|`main.py`|**요청을 받고 응답을 만든다**|엔드포인트, 오류를 상태 코드로 변환, `books` 리스트|
|`schemas.py`|**데이터 형태를 정의한다**|`BookCreate`, `BookResponse`, `Publisher`, `WeatherResponse`, `ExternalBook`|
|`external_api.py`|**외부에서 데이터를 가져온다**|`fetch_weather`, `fetch_books`, `fetch_books_multi`, `load_fallback_books`|

의존 방향은 **한 방향** 입니다.

```
main.py  →  external_api.py  →  schemas.py
main.py  →  schemas.py
```

`schemas.py`는 아무것도 import하지 않고, `external_api.py`는 FastAPI를 import하지 않습니다.
**이 방향이 지켜지면 순환 import가 생기지 않습니다.**

### 7-6. 경로 선언 순서

```
/
/health  /info
/weather  /weather/raw
/slow-async  /slow-block
/books                     (GET, POST)
/books/search  /books/filter  /books/page
/books/external  /books/external/multi
/books/from-external       (POST)
/books/{book_id}           맨 마지막
```

### 7-7. 실행

```bash
cd 01-fastapi-basic
fastapi dev main.py
```

**반드시 `main.py`가 있는 폴더에서 실행합니다.** 상위 폴더에서 실행하면 `ModuleNotFoundError`가 납니다.

---

## 8. 실습 확장 — 외부 데이터 화면

`static` 폴더에 이어서 작성합니다. 오늘은 **응답이 느리므로 로딩 표시가 중요합니다.**

> **주의:** 1·2일차와 마찬가지로 반드시 `http://127.0.0.1:8000/static/파일명.html` 주소로 여세요.
> 탐색기에서 더블클릭(`file://`)하면 CORS에 막혀 호출이 실패합니다.

---

### 웹 실습 1. 현재 날씨 표시 (실습 3 API 사용)

파일: `static/13-weather.html`

```html
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>현재 날씨</title></head>
<body>
  <h1>현재 날씨</h1>
  <p id="result">불러오는 중...</p>

  <script>
    async function load() {
      const data = await (await fetch("/weather")).json();
      document.getElementById("result").textContent =
        data.temperature + "도 (" + data.time + ")";
    }
    load();
  </script>
</body>
</html>
```

**확인:** 페이지를 열면 잠시 "불러오는 중..."이 보였다가 기온과 시각으로 바뀐다.

---

### 웹 실습 2. 좌표 입력 조회 (실습 3 API 사용)

파일: `static/14-weather-input.html`

```html
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>좌표별 날씨</title></head>
<body>
  <h1>좌표로 날씨 조회</h1>
  <input id="lat" type="number" step="0.01" value="36.8">
  <input id="lon" type="number" step="0.01" value="127.1">
  <button id="btn">조회</button>
  <p id="result"></p>

  <script>
    document.getElementById("btn").addEventListener("click", async () => {
      const lat = document.getElementById("lat").value;
      const lon = document.getElementById("lon").value;
      const res = await fetch("/weather?latitude=" + lat + "&longitude=" + lon);
      const data = await res.json();
      document.getElementById("result").textContent =
        data.latitude + ", " + data.longitude + " : " + data.temperature + "도";
    });
  </script>
</body>
</html>
```

**확인:** 서울(37.57 / 126.98), 부산(35.18 / 129.08)으로 바꿔 조회하면 기온이 달라진다.

---

### 웹 실습 3. 로딩 표시와 버튼 잠금 (실습 5 API 사용)

파일: `static/15-loading.html` — 응답을 기다리는 동안 상태를 보여주고 중복 클릭을 막습니다.

```html
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>외부 도서 검색</title></head>
<body>
  <h1>외부 도서 검색</h1>
  <input id="keyword" placeholder="검색어">
  <button id="btn">검색</button>
  <p id="status"></p>
  <ul id="list"></ul>

  <script>
    const btn = document.getElementById("btn");

    btn.addEventListener("click", async () => {
      const kw = document.getElementById("keyword").value;
      const status = document.getElementById("status");
      const list = document.getElementById("list");

      btn.disabled = true;
      status.textContent = "검색 중...";
      list.innerHTML = "";

      try {
        const res = await fetch("/books/external?keyword=" + encodeURIComponent(kw));
        const data = await res.json();
        status.textContent = "결과 " + data.length + "건";
        for (const b of data) {
          const li = document.createElement("li");
          li.textContent = b.title + " / " + (b.authors.join(", ") || "저자 미상")
            + " / " + (b.published_date || "발행일 미상");
          list.appendChild(li);
        }
      } finally {
        btn.disabled = false;
      }
    });
  </script>
</body>
</html>
```

> **참고:** `finally`를 쓴 이유는 **오류가 나도 버튼이 잠긴 채로 남지 않게** 하기 위해서입니다.

**확인:** 검색어 `fastapi`를 넣고 버튼을 누르면, 응답이 오기 전까지 버튼이 회색으로 비활성화되고 "검색 중..."이 표시된다. 결과가 오면 버튼이 다시 활성화된다. 발행일이 없는 도서는 "발행일 미상"으로 나온다.

---

### 웹 실습 4. 검색 결과 담기 (실습 6 API 사용)

파일: `static/16-import.html` — 외부 검색 결과 옆 버튼으로 내 목록에 등록합니다.

```html
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>검색 결과 담기</title></head>
<body>
  <h1>외부 검색 후 내 목록에 담기</h1>
  <input id="keyword" placeholder="검색어">
  <button id="searchBtn">검색</button>
  <p id="msg"></p>
  <ul id="external"></ul>

  <h2>내 도서 목록</h2>
  <ul id="mine"></ul>

  <script>
    async function loadMine() {
      const books = await (await fetch("/books")).json();
      const ul = document.getElementById("mine");
      ul.innerHTML = "";
      for (const b of books) {
        const li = document.createElement("li");
        li.textContent = b.id + ". " + b.title + " - " + b.author;
        ul.appendChild(li);
      }
    }

    async function importBook(book) {
      const res = await fetch("/books/from-external", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(book)
      });
      const msg = document.getElementById("msg");
      if (res.status === 201) {
        msg.textContent = "담기 완료";
        loadMine();
      } else if (res.status === 409) {
        msg.textContent = "이미 등록된 도서입니다";
      } else {
        msg.textContent = "실패 (상태 " + res.status + ")";
      }
    }

    document.getElementById("searchBtn").addEventListener("click", async () => {
      const kw = document.getElementById("keyword").value;
      const data = await (await fetch("/books/external?keyword=" + encodeURIComponent(kw))).json();
      const ul = document.getElementById("external");
      ul.innerHTML = "";
      for (const b of data) {
        const li = document.createElement("li");
        li.textContent = b.title + " ";
        const btn = document.createElement("button");
        btn.textContent = "담기";
        btn.addEventListener("click", () => importBook(b));
        li.appendChild(btn);
        ul.appendChild(li);
      }
    });

    loadMine();
  </script>
</body>
</html>
```

**확인:** 검색 후 항목 옆 "담기"를 누르면 "담기 완료"가 뜨고 아래 내 목록이 늘어난다. **같은 항목을 한 번 더** 누르면 "이미 등록된 도서입니다"가 뜬다.

---

### 웹 실습 5. 오류 상태 안내 (실습 7 API 사용)

파일: `static/17-error.html` — `502`, `504`를 사람이 이해할 문구로 바꿉니다.

```html
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>검색 (오류 처리)</title></head>
<body>
  <h1>외부 검색 (오류 처리)</h1>
  <input id="keyword" placeholder="검색어">
  <label><input id="fallback" type="checkbox"> 실패 시 예비 데이터 사용</label>
  <button id="btn">검색</button>
  <p id="msg"></p>
  <ul id="list"></ul>

  <script>
    document.getElementById("btn").addEventListener("click", async () => {
      const kw = document.getElementById("keyword").value;
      const useFallback = document.getElementById("fallback").checked;
      const msg = document.getElementById("msg");
      const list = document.getElementById("list");
      list.innerHTML = "";
      msg.textContent = "검색 중...";
      msg.style.color = "black";

      const url = "/books/external?keyword=" + encodeURIComponent(kw)
        + "&fallback=" + useFallback;
      const res = await fetch(url);
      const data = await res.json();

      if (res.status === 504) {
        msg.style.color = "red";
        msg.textContent = "외부 서비스 응답이 늦습니다. 잠시 후 다시 시도하세요.";
      } else if (res.status === 502) {
        msg.style.color = "red";
        msg.textContent = "외부 서비스에 연결할 수 없습니다.";
      } else if (res.ok) {
        msg.style.color = "green";
        msg.textContent = "결과 " + data.length + "건";
        for (const b of data) {
          const li = document.createElement("li");
          li.textContent = b.title;
          list.appendChild(li);
        }
      } else {
        msg.style.color = "red";
        msg.textContent = "오류 (상태 " + res.status + ")";
      }
    });
  </script>
</body>
</html>
```

**확인:** `.env`를 `EXTERNAL_TIMEOUT=0.001`로 바꾸고 서버를 재시작한 뒤 검색한다.

|체크박스|화면|
|---|---|
|해제|빨간 글씨로 "외부 서비스 응답이 늦습니다..."|
|체크|초록 글씨로 "결과 3건" + 예비 도서 3권|

확인이 끝나면 `.env`를 `5.0`으로 되돌리고 서버를 재시작한다.

---

### 웹 실습 6. 동시 검색 시간 비교 (실습 8 API 사용)

파일: `static/18-multi.html`

```html
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>동시 검색</title></head>
<body>
  <h1>여러 키워드 동시 검색</h1>
  <input id="keywords" value="python,fastapi,django,flask" size="40">
  <button id="btn">동시 검색</button>
  <p id="elapsed"></p>
  <div id="result"></div>

  <script>
    document.getElementById("btn").addEventListener("click", async () => {
      const kw = document.getElementById("keywords").value;
      const elapsed = document.getElementById("elapsed");
      const box = document.getElementById("result");
      elapsed.textContent = "검색 중...";
      box.innerHTML = "";

      const data = await (await fetch("/books/external/multi?keywords="
        + encodeURIComponent(kw))).json();

      elapsed.textContent = "서버 처리 시간: " + data.elapsed_seconds + "초";
      for (const r of data.results) {
        const h = document.createElement("h3");
        h.textContent = r.keyword;
        const ul = document.createElement("ul");
        for (const t of r.titles) {
          const li = document.createElement("li");
          li.textContent = t;
          ul.appendChild(li);
        }
        box.appendChild(h);
        box.appendChild(ul);
      }
    });
  </script>
</body>
</html>
```

**확인:** 입력칸의 키워드를 2개 → 4개 → 6개로 늘려가며 실행하고 "서버 처리 시간"을 비교한다. 개수가 3배가 되어도 시간이 3배가 되지 않는다. **이것이 비동기의 효과다.**

---

### 시작 페이지 갱신 (선택)

`static/index.html`에 3일차 페이지 6개를 추가합니다.

```html
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>도서 관리 API 실습</title></head>
<body>
  <h1>도서 관리 API 실습</h1>

  <h2>1일차 — 조회</h2>
  <ul>
    <li><a href="01-status.html">1. 서버 상태</a></li>
    <li><a href="02-list.html">2. 도서 목록</a></li>
    <li><a href="03-detail.html">3. 단건 조회</a></li>
    <li><a href="04-search.html">4. 제목 검색</a></li>
    <li><a href="05-filter.html">5. 저자 필터·정렬</a></li>
    <li><a href="06-page.html">6. 페이지네이션</a></li>
  </ul>

  <h2>2일차 — 등록과 검증</h2>
  <ul>
    <li><a href="07-create.html">7. 도서 등록 폼</a></li>
    <li><a href="08-validate.html">8. 검증 오류 표시</a></li>
    <li><a href="09-create-list.html">9. 등록 후 목록 갱신</a></li>
    <li><a href="10-detail-404.html">10. 404 구분 처리</a></li>
    <li><a href="11-nested.html">11. 태그·출판사 입력</a></li>
    <li><a href="12-final.html">12. 상태 코드 통합 처리</a></li>
  </ul>

  <h2>3일차 — 외부 API 연동</h2>
  <ul>
    <li><a href="13-weather.html">13. 현재 날씨</a></li>
    <li><a href="14-weather-input.html">14. 좌표별 날씨</a></li>
    <li><a href="15-loading.html">15. 외부 도서 검색 (로딩 표시)</a></li>
    <li><a href="16-import.html">16. 검색 결과 담기</a></li>
    <li><a href="17-error.html">17. 오류 상태 안내</a></li>
    <li><a href="18-multi.html">18. 동시 검색 시간 비교</a></li>
  </ul>

  <p><a href="/docs">API 자동 문서(Swagger UI) 열기</a></p>
</body>
</html>
```

### 웹 실습 심화 (시간이 남을 때)

- 웹 실습 3의 로딩 표시를 회전 애니메이션으로 바꾼다.
- 웹 실습 4에서 담기 성공한 항목을 목록에서 흐리게 표시한다.
- 검색 입력을 0.5초 멈췄을 때 자동 검색되게 만든다. (디바운스)

---

## 9. 최종 확인 체크리스트

**API (Swagger UI `/docs`에서 확인)**

- [ ] 콘솔 측정에서 `/slow-async` 3건이 약 3초, `/slow-block` 3건이 약 9초로 나온다
- [ ] `GET /weather/raw`가 필드 10개 이상의 원본 JSON을 반환한다
- [ ] `GET /weather`가 **네 필드만** 반환한다
- [ ] `GET /weather?latitude=37.57&longitude=126.98`이 서울 기온을 반환한다
- [ ] 서버를 재시작해도 `ModuleNotFoundError` 없이 뜬다 (파일 분리 성공)
- [ ] `GET /books/external?keyword=fastapi`가 도서 5건을 반환한다
- [ ] `GET /books/external?keyword=asdkjfhaskdjfh`가 **빈 배열** 을 반환한다
- [ ] `POST /books/from-external`로 담으면 `201`, 같은 것을 또 담으면 `409`
- [ ] 담은 도서의 `tags`가 `["외부검색"]`이고 `year`가 정수다
- [ ] `EXTERNAL_TIMEOUT=0.001` + 재시작 후 `fallback=false`면 `504`
- [ ] 같은 조건에서 `fallback=true`면 `200` + 예비 도서 3권
- [ ] `.env`를 `5.0`으로 되돌리고 재시작하면 정상 검색된다
- [ ] `GET /books/external/multi`에서 키워드를 늘려도 시간이 비례해 늘지 않는다
- [ ] 1·2일차 엔드포인트(`/books`, `/books/search`, `/books/{book_id}` 등)가 그대로 동작한다

**파일 구성**

- [ ] `schemas.py`에 모델 5개가 있고 `main.py`에는 모델 정의가 남아 있지 않다
- [ ] `external_api.py`에 `HTTPException`이나 `fastapi` import가 **없다**
- [ ] `sample_books.json`이 `main.py`와 같은 폴더에 있다
- [ ] `.gitignore`에 `.env`가 들어 있다

**웹페이지 (`http://127.0.0.1:8000/static/...`)**

- [ ] `13-weather.html` — 열자마자 기온이 표시된다
- [ ] `14-weather-input.html` — 좌표를 바꾸면 기온이 달라진다
- [ ] `15-loading.html` — 검색 중 버튼이 잠기고 "검색 중..."이 표시된다
- [ ] `16-import.html` — 담기 성공/중복이 구분되고 목록이 갱신된다
- [ ] `17-error.html` — 타임아웃 시 빨간 안내, 체크박스 켜면 예비 데이터
- [ ] `18-multi.html` — 키워드 수를 늘려도 처리 시간이 비례해 늘지 않는다

---

## 10. 오늘의 정리

- 외부 호출은 기다리는 시간이 길다. `async def`와 `await`로 기다리는 동안 다른 요청을 처리한다.
- `async def` 안에서 **동기 대기 코드** 를 쓰면 서버 전체가 멈춘다. `httpx`의 비동기 방식을 쓴다.
- 외부 응답은 그대로 넘기지 말고 **필요한 필드만 뽑아 내 모델로 변환** 한다.
- 없을 수 있는 필드는 `.get()`으로 기본값을 준다. 실제로 자주 발생한다.
- 외부 API는 **반드시 실패한다고 가정** 한다. 타임아웃을 설정하고, 실패를 `502`·`504`로 구분해 알린다.
- 여러 외부 호출은 `asyncio.gather`로 동시에 처리한다.
- API 키는 `.env`에 두고 `.gitignore`에 등록한다. 코드에 직접 쓰지 않는다.
- 파일이 길어지면 역할별로 나눈다. **데이터를 가져오는 일**(`external_api.py`)과 **사용자에게 응답하는 일**(`main.py`)을 분리하면, 한쪽이 복잡해져도 다른 쪽을 건드리지 않는다.

4일차에는 지금까지 만든 API의 **문서를 정리** 하고 **Postman으로 전체를 테스트** 합니다.

---

## 11. 자주 나는 오류와 해결

### 파일 분리 관련

|증상 / 오류 메시지|원인|해결|
|---|---|---|
|`ModuleNotFoundError: No module named 'schemas'`|**상위 폴더에서 실행함**|`cd 01-fastapi-basic` 후 `fastapi dev main.py`|
|`ModuleNotFoundError: No module named 'external_api'`|파일을 아직 안 만들었거나 이름 오타|`main.py`와 같은 폴더에 파일이 있는지 확인|
|`ImportError: cannot import name 'fetch_books'`|파일은 있는데 **그 함수를 아직 안 씀**|`external_api.py`에 함수를 먼저 추가한 뒤 import|
|`NameError: name 'ExternalBook' is not defined`|함수는 있는데 **import 줄에 안 넣음**|`from schemas import ... , ExternalBook` 추가|
|서버가 아예 안 뜸|모듈 최상단(데코레이터)에서 미정의 이름 사용|터미널 traceback의 파일·줄 번호 확인|
|서버는 뜨는데 특정 엔드포인트만 `500`|함수 **안** 에서 미정의 이름 사용|해당 함수의 import 확인|
|순환 import 오류|`schemas.py`가 다른 파일을 import함|`schemas.py`는 **아무것도 import하지 않는다**|

### 비동기 관련

|증상 / 오류 메시지|원인|해결|
|---|---|---|
|`SyntaxError: 'await' outside async function`|일반 `def` 안에서 `await` 사용|함수를 `async def`로 변경|
|브라우저 탭 여러 개로 테스트해도 차이가 없음|Chrome이 **같은 주소** 중복 요청을 대기시킴|`?n=1`, `?n=2`처럼 주소를 다르게 하거나 콘솔 측정 사용|
|`/slow-async`도 9초가 걸림|`await`를 빠뜨리고 `time.sleep` 사용|`await asyncio.sleep(3)`인지 확인|
|동시 호출인데 시간이 비례해 늘어남|`gather` 없이 반복문으로 순차 호출|`asyncio.gather(*[...])` 사용 확인|

### 외부 API 관련

|증상 / 오류 메시지|원인|해결|
|---|---|---|
|`500` + `KeyError: 'publishedDate'`|없을 수 있는 필드를 대괄호로 접근|`info.get("publishedDate", "")`로 변경|
|`500` + `ValueError: invalid literal for int()`|빈 문자열을 `int()`로 변환|`isdigit()` 검사 추가 (실습 6)|
|검색 결과가 항상 빈 배열|API 키가 없거나 잘못됨|서버 시작 시 "경고: ..." 메시지가 떴는지 확인|
|`502` + `API key not valid`|`.env`의 키 오타|키를 다시 복사해 붙여넣기|
|`.env`를 고쳤는데 반영 안 됨|`fastapi dev`는 `.env` 변경을 **감지 못 함**|`Ctrl + C` 후 서버 재시작|
|`504`가 안 나옴|`EXTERNAL_TIMEOUT`을 코드가 안 읽고 있음|`timeout=EXTERNAL_TIMEOUT`으로 바꿨는지 확인|
|`fallback=true`인데 빈 배열|`sample_books.json` 위치가 다름|`main.py`와 같은 폴더에 두기|
|`/books/external` 호출 시 `422`|`/books/{book_id}`가 **위** 에 선언됨|리터럴 경로를 위로 이동|

### 문제가 안 풀릴 때

1. **`500`이면 브라우저가 아니라 서버 터미널** 을 봅니다. traceback 마지막 줄에 원인이 있습니다.
2. 오류가 `KeyError`면 **없을 수 있는 필드** 를 대괄호로 접근한 것입니다.
3. import 오류는 `ModuleNotFoundError`(파일 없음) / `ImportError`(이름 없음) / `NameError`(import 누락)를 구분해 원인을 좁힙니다.
4. 그래도 안 되면 [7. 전체 완성 코드](#7-전체-완성-코드)와 본인 코드를 파일별로 비교합니다.

---

## 부록. 용어 사전 (3일차 추가분)

| 용어                          | 한 줄 정의                                             |
| --------------------------- | -------------------------------------------------- |
| **I/O**                     | Input/Output. 네트워크·파일처럼 **바깥과 주고받는 작업**            |
| **I/O 대기**                  | 외부 응답을 기다리며 아무 일도 못 하는 시간                          |
| **동기 / 비동기**                | 앞 작업이 끝나야 다음을 시작 / 기다리는 동안 다른 일을 처리                |
| **`async def`**             | 중간에 멈췄다가 다시 이어질 수 있는 **비동기 함수** 선언                 |
| **`await`**                 | 여기서 기다린다는 표시. 기다리는 동안 **제어권을 넘김**                  |
| **`asyncio`**               | 파이썬 표준 비동기 라이브러리                                   |
| **`asyncio.sleep`**         | 비동기로 기다리는 함수. `time.sleep`과 달리 제어권을 넘김             |
| **`asyncio.gather`**        | 여러 비동기 작업을 **동시에 실행** 하고 전부 끝날 때까지 기다림             |
| **`httpx`**                 | 비동기를 지원하는 파이썬 HTTP 클라이언트                           |
| **`AsyncClient`**           | httpx에서 요청을 보내는 객체                                 |
| **`async with`**            | 사용이 끝나면 연결을 **자동으로 정리** 하는 구문                      |
| **`raise_for_status()`**    | 응답이 `4xx`·`5xx`면 **예외를 발생** 시키는 메서드                |
| **타임아웃 (timeout)**          | "이 시간 안에 응답이 없으면 포기한다"는 제한 시간                      |
| **`502` Bad Gateway**       | **외부 서버** 가 오류를 냈거나 연결할 수 없음                       |
| **`504` Gateway Timeout**   | **외부 서버** 응답이 너무 늦음                                |
| **매핑 (mapping)**            | 외부 응답에서 필요한 필드만 뽑아 내 모델로 변환하는 일                    |
| **폴백 (fallback)**           | 주된 방법이 실패했을 때 쓰는 **대체 수단**                         |
| **`Path(__file__).parent`** | **이 파이썬 파일이 있는 폴더.** 실행 위치와 무관하게 경로를 잡을 때 사용       |
| **순환 import**               | A가 B를, B가 A를 import해 서로 물리는 상태. 의존 방향을 한쪽으로 유지해 예방 |

### 1·2일차 용어 복습

|용어|한 줄 정의|
|---|---|
|**FastAPI / Uvicorn**|웹 프레임워크 / 실제로 포트를 열고 요청을 받는 ASGI 서버|
|**`dev` / `run`**|`fastapi dev`는 개발용(자동 재시작), `fastapi run`은 운영용|
|**Pydantic / `BaseModel`**|타입 힌트로 데이터 구조를 정의하고 자동 검증하는 라이브러리|
|**`response_model`**|응답 형태를 고정·검사하는 옵션. 값을 **생성하지는 않음**|
|**`HTTPException`**|상태 코드와 함께 오류 응답을 내보내는 예외. `return`이 아니라 `raise`|
|**`.env` / python-dotenv**|환경변수를 적어 두는 파일 / 그것을 읽어 오는 패키지|
|**리터럴 경로 우선 규칙**|`/books/search`는 `/books/{book_id}`보다 **위** 에 선언|

## 부록. 명령어 요약

|목적|명령|
|---|---|
|가상환경 활성화 (Windows PowerShell)|`.venv\Scripts\Activate.ps1`|
|httpx 설치 확인|`pip show httpx`|
|python-dotenv 설치|`pip install python-dotenv`|
|**개발** 서버 실행 (반드시 `main.py` 폴더에서)|`cd 01-fastapi-basic` → `fastapi dev main.py`|
|서버 종료|`Ctrl + C`|
|`.env` 변경 반영|**서버 재시작** (자동 감지 안 됨)|

## 부록. 주요 주소 요약

|주소|용도|
|---|---|
|`http://127.0.0.1:8000/docs`|Swagger UI 자동 문서 (실습 확인용)|
|`http://127.0.0.1:8000/static/index.html`|웹 실습 시작 페이지|
|`http://127.0.0.1:8000/weather`|날씨 조회 (Open-Meteo 매핑 결과)|
|`http://127.0.0.1:8000/books/external?keyword=fastapi`|외부 도서 검색 (Google Books)|
|`https://api.open-meteo.com/v1/forecast`|Open-Meteo 원본 주소 (키 불필요)|
|`https://www.googleapis.com/books/v1/volumes`|Google Books 원본 주소 (키 필요)|

---

**다음 시간:** FastAPI 입문 4일차 — 문서화와 테스트

#FastAPI #Python #백엔드 #API #입문 #3일차 #배포용 #async #await #asyncio #httpx #외부API #OpenMeteo #GoogleBooks #타임아웃 #502 #504 #gather #dotenv #모듈분리