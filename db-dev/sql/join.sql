--실습 10. INNER JOIN과 LEFT JOIN 비교
-- INNER JOIN — 최지은이 사라진다
select u.username, c.title
from users u
join conversations c on c.user_id = u.id
order by u.username;

-- LEFT JOIN — 최지은도 남고, title 자리에 NULL이 찍힌다
select u.username, c.title
from users u
left join conversations c on c.user_id = u.id
order by u.username;

--대화와 메세지 left join
select c.title, m.content
from messages m
left join conversations c on c.id = m.conversation_id;

--실습 11. 대화가 없는 사용자 찾기
select u.username, u.email
from users u
left join conversations c on c.user_id = u.id
where c.id is null;

--실습 12. 사용자별 대화 수 세기
select
    u.username,
    count(*)     as 잘못된_대화수,
    count(c.id)  as 올바른_대화수
from users u
left join conversations c on c.user_id = u.id
group by u.username
order by u.username;

--실습 13. 세 테이블을 잇기
-- 특정 대화의 메시지 전체 (대화 흐름 그대로)
select
    m.role,
    m.content,
    m.created_at
from messages m
join conversations c on c.id = m.conversation_id
where c.title = '파이썬 기초 질문'
order by m.created_at;

-- 대화별 메시지 수 (메시지가 0건인 대화도 보이게)
select
    u.username,
    c.title,
    count(m.id) as 메시지수
from users u
join conversations c on c.user_id = u.id
left join messages m  on m.conversation_id = c.id
group by u.username, c.title
order by 메시지수 desc;

--실습 14. 서브쿼리
-- 대화를 가진 사용자만 (실습 11과 반대 결과)
select username, email
from users
where id in (select user_id from conversations);

-- 사용자별 대화 수를 한 열로 (실습 12의 다른 방법)
select
    username,
    (select count(*) from conversations c where c.user_id = u.id) as 대화수
from users u
order by 대화수 desc;

-- 가장 최근 대화가 있는 사용자 목록
select
    u.username,
    max(c.created_at) as 최근대화시각
from users u
join conversations c on c.user_id = u.id
group by u.username
order by 최근대화시각 desc;