import hashlib
import json
from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db import get_anon_client
from app.cache import cache_get, cache_set

bearer_scheme = HTTPBearer()

SESSION_CACHE_TTL_SECONDS = 300

@dataclass
class CurrentUser:
    id: str
    email: str
    token: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    # "Bearer " 접두어는 HTTPBearer 가 이미 떼어냈다.
    # 헤더가 없거나 형식이 틀리면 여기 오기 전에 401 로 막힌다.
    token = credentials.credentials
    cache_key = f"session:{hashlib.sha256(token.encode()).hexdigest()}"

    cached = cache_get(cache_key)
    if cached:
        data = json.loads(cached)
        return CurrentUser(id=data["id"], email=data["email"], token=token)

    client = get_anon_client()
    try:
        result = client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")

    current_user = CurrentUser(id=str(result.user.id), email=result.user.email, token=token)
    cache_set(
        cache_key,
        json.dumps({"id": current_user.id, "email": current_user.email}),
        ex=SESSION_CACHE_TTL_SECONDS,
    )

    return CurrentUser(id=str(result.user.id), email=result.user.email, token=token)