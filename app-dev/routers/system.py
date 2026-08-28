from fastapi import APIRouter

router = APIRouter(tags=["시스템"])

@router.get("/", summary="루트")
def read_root():
    return {"message": "FastAPI 첫 서버"}


@router.get("/health", summary="서버 상태 확인")
def health():
    return {"status": "ok"}


@router.get("/info", summary="앱 정보")
def info():
    return {"name": "도서 관리 API", "version": "1.0.0"}