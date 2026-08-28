--실습 0. user table 만들기
create extension if not exists "pgcrypto";

create table users (
    id uuid primary key default gen_random_uuid(),
    email text not null unique,
    username varchar(30) not null check (length(username) >= 2),
    created_at timestamptz not null default now()
);

-- 실습 1. users 테이블 라벨링
select column_name, data_type, is_nullable, column_default
from information_schema.columns
where table_name = 'users' and table_schema = 'public'
order by ordinal_position;


comment on table  users            is '서비스 사용자';
comment on column users.id         is '사용자 식별자. 자동 생성되는 UUID';
comment on column users.email      is '로그인 이메일. 중복 불가';
comment on column users.username   is '화면에 보이는 이름. 로그인 아이디가 아니다';
comment on column users.created_at is '가입 시각. 입력하지 않으면 현재 시각';


select
    c.column_name              as 컬럼,
    c.data_type                as 타입,
    c.character_maximum_length as 길이,
    c.is_nullable              as null허용,
    c.column_default           as 기본값,
    col_description(('public.' || c.table_name)::regclass, c.ordinal_position) as 설명
from information_schema.columns c
where c.table_schema = 'public' and c.table_name = 'users'
order by c.ordinal_position;


--실습 2. 제약 조건 검

-- (1) NOT NULL 위반 — email 없이 넣기
insert into users (username) values ('테스터');

-- (2) CHECK 위반 — 닉네임이 1글자
insert into users (email, username) values ('x@example.com', 'A');

-- (3) 길이 초과 — varchar(30)을 넘김
insert into users (email, username) values ('y@example.com', repeat('가', 31));


--실습 3. 데이터 넣고 조회하기

insert into users (email, username) values
    ('kim@example.com',  '김철수'),
    ('lee@example.com',  '이영희'),
    ('park@example.com', '박민수'),
    ('choi@example.com', '최지은'),
    ('jung@example.com', '정하늘');


-- 전체 조회
select id, email, username, created_at from users;

-- 조건 조회
select email, username, id from users
where email = 'kim@example.com';

-- 부분 일치 (이메일에 e가 들어간 사용자)
select email, username from users
where email like '%e%';

-- 정렬 (최신 가입 순)
select username, created_at from users
order by created_at desc;

-- 개수 제한 (먼저 가입한 3명)
select username, created_at from users
order by created_at asc
limit 3;

-- 개수 세기
select count(*) as 전체사용자수 from users;


-- 실습 4. UPDATE로 값 바꾸기

update users
set username = '김철수리'
where email = 'kim@example.com';

select email, username from users order by email;


-- 실습 5. WHERE 없는 UPDATE — 직접 사고를 내본다
-- (1) 사고 치기 전에 백업부터
create table users_backup as select * from users;

select count(*) as 백업건수 from users_backup;

-- (2) 사고 재현 — where 없이 update
update users
set username = '해킹당함';

-- (3) 피해 확인
select email, username from users order by email;

-- (4) 복구
update users u
set username = b.username
from users_backup b
where u.id = b.id;

select email, username from users order by email;

--예방법 — 트랜잭션으로 미리 확인하기
begin;

update users set username = '실수다';

-- 몇 행이 바뀌었는지 여기서 확인한다. 예상과 다르면 rollback.
select count(*) as 바뀐행수 from users where username = '실수다';
rollback;   -- 되돌리기 (의도한 결과였다면 commit;)
select email, username from users order by email;


--실습 6. DELETE로 삭제하기
-- (1) 지울 대상을 먼저 확인 (위 습관 1번)
select * from users where email = 'jung@example.com';

-- (2) 확인한 그 where 그대로 delete
delete from users
where email = 'jung@example.com';

select email, username from users order by email;

-- (3) 백업 테이블 정리
drop table users_backup;