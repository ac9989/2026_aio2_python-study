--실습 7. conversations와 messages 만들기
create table conversations (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    title varchar(100) not null,
    created_at timestamptz not null default now()
);
create index idx_conversations_user_id on conversations(user_id);
insert into conversations (user_id, title)
values ('3317d88e-3618-4dad-93b0-c693e3df6a22', '유령 사용자의 대화')
--select * from conversations



create table messages (
    id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references conversations(id) on delete cascade,
    role varchar(20) not null check (role in ('user', 'assistant')),
    content text not null,
    created_at timestamptz not null default now()
);
create index idx_messages_conversation_id on messages(conversation_id);

comment on table  conversations            is '사용자별 대화';
comment on column conversations.id         is '대화 식별자';
comment on column conversations.user_id    is '대화 주인. users.id 참조. 사용자가 지워지면 함께 삭제';
comment on column conversations.title      is '대화 제목';
comment on column conversations.created_at is '대화 시작 시각';

comment on table  messages                 is '대화에 속한 메시지';
comment on column messages.id              is '메시지 식별자';
comment on column messages.conversation_id is '소속 대화. conversations.id 참조';
comment on column messages.role            is '작성 주체. user 또는 assistant';
comment on column messages.content         is '메시지 본문';
comment on column messages.created_at      is '작성 시각. 대화 순서를 이 값으로 정렬';

select
    c.table_name               as 테이블,
    c.column_name              as 컬럼,
    c.data_type                as 타입,
    c.is_nullable              as null허용,
    col_description(('public.' || c.table_name)::regclass, c.ordinal_position) as 설명
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name in ('users', 'conversations', 'messages')
order by c.table_name, c.ordinal_position;

--실습 8은 생략
--실습 9. 조회용 샘플 데이터 넣기
insert into conversations (user_id, title) values
    ((select id from users where email = 'kim@example.com'),  '파이썬 기초 질문'),
    ((select id from users where email = 'kim@example.com'),  '이직 고민 상담'),
    ((select id from users where email = 'lee@example.com'),  'SQL 공부 방법'),
    ((select id from users where email = 'park@example.com'), '여행 계획 짜기');

insert into messages (conversation_id, role, content, created_at) values
    ((select id from conversations where title = '파이썬 기초 질문'), 'user',
     '리스트와 튜플의 차이가 뭔가요?',                    now() - interval '50 minutes'),
    ((select id from conversations where title = '파이썬 기초 질문'), 'assistant',
     '리스트는 수정할 수 있고 튜플은 수정할 수 없습니다.',  now() - interval '49 minutes'),
    ((select id from conversations where title = '파이썬 기초 질문'), 'user',
     '그럼 언제 튜플을 쓰나요?',                          now() - interval '48 minutes'),
    ((select id from conversations where title = '파이썬 기초 질문'), 'assistant',
     '값이 바뀌면 안 되는 좌표나 설정값에 씁니다.',         now() - interval '47 minutes'),

    ((select id from conversations where title = '이직 고민 상담'), 'user',
     '3년차인데 이직하는 게 좋을까요?',                    now() - interval '30 minutes'),
    ((select id from conversations where title = '이직 고민 상담'), 'assistant',
     '현재 직무에서 더 배울 것이 남았는지 먼저 점검해보세요.', now() - interval '29 minutes'),

    ((select id from conversations where title = 'SQL 공부 방법'), 'user',
     'JOIN이 너무 어려워요.',                             now() - interval '20 minutes'),
    ((select id from conversations where title = 'SQL 공부 방법'), 'assistant',
     '두 표를 나란히 놓고 어떤 열이 같은지부터 찾아보세요.',  now() - interval '19 minutes'),
    ((select id from conversations where title = 'SQL 공부 방법'), 'user',
     'LEFT JOIN은 언제 쓰나요?',                          now() - interval '18 minutes');

select
    (select count(*) from users)         as 사용자수,
    (select count(*) from conversations) as 대화수,
    (select count(*) from messages)      as 메시지수;