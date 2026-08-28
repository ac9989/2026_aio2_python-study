"""요청·응답 모델 (실습 3).

생성용 / 수정용 / 응답용을 나누는 이유:
    생성할 때 클라이언트는 id 와 created_at 을 보내지 않는다 (DB가 만든다).
    반대로 응답에는 그 값이 들어간다. 한 모델로 쓰면 둘 중 하나가 어긋난다.

11일차에 DB에 걸어둔 제약을 여기서 한 번 더 막는다.
    username 2~30자  ·  role 은 두 값만  ·  email 형식
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# ── 사용자 ────────────────────────────────────────────────────────
#회원 가입용
class SignupRequest(BaseModel):
    email: str
    password: str

#회원 로그인용
class LoginRequest(BaseModel):
    email: str
    password: str

#회원 응답
class TokenResponse(BaseModel):
    access_token: str | None
    user_id: str
    email: str

# ── 대화 ──────────────────────────────────────────────────────────
# TODO 4. ConversationCreate — user_id(UUID), title(1~100자)
class ConversationCreate(BaseModel):
    user_id: UUID
    title: str = Field(min_length=1, max_length=100)

# TODO 5. ConversationOut    — id, user_id, title, created_at
class ConversationOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime

# ── 메시지 ────────────────────────────────────────────────────────
# 주의: role 은 Literal 로 값을 고정한다. str 로 두면 'robot' 같은 값이 그대로 통과한다.
# TODO 6. MessageCreate — role(Literal), content(1자 이상)
class MessageCreate(BaseModel):
    role: Literal["user", "assistant","system"]
    content: str = Field(min_length=1)

# TODO 7. MessageOut    — id, conversation_id, role, content, created_at
class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime

#문제 1. 대화 제목 수정
class ConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)

#문제 1. 내 프로필 조회
class ProfileOut(BaseModel):
    id: UUID
    username: str
    created_at: datetime