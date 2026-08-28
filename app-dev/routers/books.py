from fastapi import APIRouter, HTTPException

from database import books, save_books
from routers.schemas import BookCreate, BookResponse, BookUpdate, ErrorDetail

router = APIRouter(prefix="/books", tags=["도서"])


def get_book_or_404(book_id: int) -> dict:
    """번호로 도서를 찾고, 없으면 404를 발생시킨다."""
    for b in books:
        if b["id"] == book_id:
            return b
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


@router.get("", response_model=list[BookResponse], summary="도서 목록 조회")
def list_books():
    """내 목록에 등록된 도서를 전부 반환합니다."""
    return books


@router.post(
    "",
    response_model=BookResponse,
    status_code=201,
    summary="도서 등록",
    responses={409: {"description": "이미 등록된 제목입니다", "model": ErrorDetail}},
)
def create_book(book: BookCreate):
    """새 도서를 등록합니다. 같은 제목이 이미 있으면 409를 반환합니다."""
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")
    new_id = max([b["id"] for b in books], default=0) + 1
    new_book = {"id": new_id, **book.model_dump()}
    books.append(new_book)
    save_books()
    return new_book


# 리터럴 경로는 /{book_id}보다 먼저 선언한다
@router.get("/search", summary="제목 검색")
def search_books(keyword: str = ""):
    """제목에 키워드가 포함된 도서를 반환합니다. 비우면 전체를 반환합니다."""
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]


@router.get("/filter", summary="저자 필터·연도 정렬")
def filter_books(author: str = "", sort: str = ""):
    """저자로 거르고 sort가 year이면 연도 오름차순으로 정렬합니다."""
    result = books
    if author:
        result = [b for b in result if b["author"] == author]
    if sort == "year":
        result = sorted(result, key=lambda b: b["year"])
    return result


@router.get("/page", summary="페이지네이션")
def page_books(skip: int = 0, limit: int = 2):
    """skip개를 건너뛰고 limit개만 반환합니다."""
    return books[skip: skip + limit]


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="도서 단건 조회",
    responses={404: {"description": "해당 번호의 도서가 없습니다", "model": ErrorDetail}},
)
def read_book(book_id: int):
    """도서 번호로 한 건을 조회합니다."""
    return get_book_or_404(book_id)


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="도서 전체 수정",
    responses={404: {"description": "해당 번호의 도서가 없습니다", "model": ErrorDetail}},
)
def update_book(book_id: int, book: BookCreate):
    """
    도서 정보를 전체 교체합니다. 보내지 않은 필드는 기본값으로 바뀝니다.
    일부만 고치려면 PATCH를 사용하세요.
    """
    old = get_book_or_404(book_id)
    new_book = {"id": book_id, **book.model_dump()}
    books[books.index(old)] = new_book
    save_books()
    return new_book


@router.patch(
    "/{book_id}",
    response_model=BookResponse,
    summary="도서 부분 수정",
    responses={404: {"description": "해당 번호의 도서가 없습니다", "model": ErrorDetail}},
)
def patch_book(book_id: int, patch: BookUpdate):
    """보낸 필드만 수정합니다. 보내지 않은 필드는 그대로 유지됩니다."""
    book = get_book_or_404(book_id)
    book.update(patch.model_dump(exclude_unset=True))
    save_books()
    return book


@router.delete(
    "/{book_id}",
    status_code=204,
    summary="도서 삭제",
    responses={404: {"description": "해당 번호의 도서가 없습니다", "model": ErrorDetail}},
)
def delete_book(book_id: int):
    """도서를 삭제합니다. 성공 시 본문 없이 204를 반환합니다."""
    book = get_book_or_404(book_id)
    books.remove(book)
    save_books()
    return None