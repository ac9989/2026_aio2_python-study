import hashlib
import json
import sys
import time
import urllib.request

from app.redis_client import r

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000"
TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjM0OTU5NGQ3LWY5MzYtNDM1Zi1iZDIyLTIxYjNjNmFkYjMyNCIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3R1YXp5dnhmY3l6ZWl3cnlrYmxsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIyOWRlMDc4MC00MDBkLTQ1YzItODY4Yi1jYmExYWU5NGMzNTYiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzg3ODE2MTE0LCJpYXQiOjE3ODc4MTI1MTQsImVtYWlsIjoiYUBleGFtcGxlLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJhQGV4YW1wbGUuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwic3ViIjoiMjlkZTA3ODAtNDAwZC00NWMyLTg2OGItY2JhMWFlOTRjMzU2In0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoicGFzc3dvcmQiLCJ0aW1lc3RhbXAiOjE3ODc4MTI1MTR9XSwic2Vzc2lvbl9pZCI6IjRlMTdkZmMwLTQ3MmYtNDg4Ni05ZGUyLTI1YmYxNThkZWViMiIsImlzX2Fub255bW91cyI6ZmFsc2V9.xEvm3HFX4mXPZ7wsMmqjM7uiCyLk12V9JAvREU45jdZJ3pYUuV5jx7xHH8p_Lzdw82DGWemDYdj25e1g_qBcuw"
CONVERSATION_ID = "ccdd9cb5-684f-4e3c-a6ee-bfe81093b025"


def call(path):
    req = urllib.request.Request(BASE + path)
    req.add_header("Authorization", "Bearer " + TOKEN)
    started = time.perf_counter()
    with urllib.request.urlopen(req) as res:
        body = json.loads(res.read())
    return body, (time.perf_counter() - started) * 1000


def measure(path, cache_key, times=3):
    """캐시를 비우고 같은 요청을 여러 번 보낸다."""
    r.delete(cache_key)          # 1회차가 확실히 MISS 가 되게 한다
    print(f"\n{path}")
    for i in range(1, times + 1):
        body, ms = call(path)
        count = len(body) if isinstance(body, list) else "-"
        print(f"  {i}회차  {ms:7.1f} ms  {count}건  남은 TTL {r.ttl(cache_key):>4}s")


measure("/me", "session:" + hashlib.sha256(TOKEN.encode()).hexdigest())