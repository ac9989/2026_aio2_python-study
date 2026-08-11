# 2026_aio2_python-study

```markdown
# Git 협업 실습 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant A as 작업자 A
    participant G as GitHub
    participant B as 작업자 B

    A->>A: README 수정
    A->>A: Commit
    A->>G: Push
    G-->>A: Push 성공

    B->>B: README 수정
    B->>B: Commit
    B->>G: Push
    G-->>B: Push 거절

    B->>G: Fetch
    G-->>B: A의 변경사항 전달

    B->>B: Merge
    B-->>B: Conflict 발생

    B->>B: 충돌 내용 수정
    B->>B: 충돌 해결
    B->>B: Merge Commit 생성

    B->>G: Push
    G-->>B: Push 성공

    A->>G: Fetch
    G-->>A: 최종 Merge 결과 전달
    A->>A: 최종 결과 확인
