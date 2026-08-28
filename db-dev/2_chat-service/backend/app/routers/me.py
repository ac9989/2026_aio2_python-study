from fastapi import APIRouter, Depends, HTTPException

from app.db import get_anon_client
from app.deps import CurrentUser, get_current_user
from app.schemas import ConversationOut, ProfileOut

router = APIRouter(prefix="/me", tags=["me"])


@router.get("")
def read_me(current_user: CurrentUser = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}


@router.get("/conversations", response_model=list[ConversationOut])
def my_conversations(current_user: CurrentUser = Depends(get_current_user)):
    client = get_anon_client()
    client.postgrest.auth(current_user.token)
    result = (
        client.table("conversations")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data

# 문제 1. 내 프로필 조회
@router.get("/profile", response_model=ProfileOut)
def read_my_profile(current_user: CurrentUser = Depends(get_current_user)):
    client = get_anon_client()
    client.postgrest.auth(current_user.token)
    result = client.table("profiles").select("*").execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")
    return result.data[0]