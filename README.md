# 2026_aio2_python-study

```mermaid
sequenceDiagram
    participant A as 작업자 A
    participant G as GitHub
    participant B as 작업자 B

    A->>A: README 수정 및 Commit
    A->>G: Push
    G-->>A: Push 성공

    B->>B: README 수정 및 Commit
    B->>G: Push
    G-->>B: Push 거절

    B->>G: Fetch
    G-->>B: A의 변경사항 전달

    B->>B: Merge
    B-->>B: Conflict 발생

    B->>B: 충돌 내용 수정
    B->>B: Merge Commit

    B->>G: Push
    G-->>B: Push 성공

    A->>G: Fetch
    G-->>A: Merge 결과 전달
    A->>A: 최종 결과 확인


### 시각적으로 보면

```text
시간 ↓

작업자 A                 GitHub                 작업자 B
   │                       │                       │
   │── README 수정 ────────│                       │
   │── Commit ─────────────│                       │
   │── Push ──────────────>│                       │
   │                       │                       │
   │                       │<──── README 수정 ─────│
   │                       │<──── Commit ──────────│
   │                       │<──── Push ────────────│
   │                       │───── 거절 ───────────>│
   │                       │                       │
   │                       │<──── Fetch ───────────│
   │                       │──── A 변경사항 ──────>│
   │                       │                       │
   │                       │                  Merge
   │                       │                    ↓
   │                       │                Conflict
   │                       │                    ↓
   │                       │                충돌 해결
   │                       │                    ↓
   │                       │                Merge Commit
   │                       │                       │
   │                       │<──── Push ────────────│
   │                       │                       │
   │                       │<──── Fetch ───────────│
   │                       │──── 최종 결과 ───────>│
   │                       │                       │
