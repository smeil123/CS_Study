



* 이름이 null이 아니며 중복되지 않은 이름의 개수
```sql
SELECT COUNT(DISTINCT NAME)
FROM ANIMAL_INS
WHERE NAME IS NOT NULL
```

* 개와 고양이 수를 출력하되 CAT,DOG 순으로 출력하라
```sql
SELECT COUNT(DISTINCT NAME)
FROM ANIMAL_INS
WHERE NAME IS NOT NULL
```
* 이름이 2번이상 쓰인 것만 출력
```sql
-- 코드를 입력하세요
SELECT NAME, COUNT(*)
FROM ANIMAL_INS
GROUP BY NAME
HAVING COUNT(NAME) >= 2
```

* 9시에서 19시 사이의 데이터 갯수를 출력
```sql
-- 코드를 입력하세요
select hour(`datetime`),count(*)
from animal_outs
where hour(`datetime`) between 9 and 19
group by hour(`datetime`)
```

* 0시부터 23시까지 각 시간대별로 입양건수를 조회
```sql
-- 코드를 입력하세요
set @hour = -1;
select
    (@hour := @hour +1) as HOUR,
    (select count(*) from animal_outs where hour(`datetime`) = @hour) as `COUNT`
from animal_outs 
where @hour < 23
```

```sq
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTIwMTA1MjY3NTEsMjA3OTMyMTY1NywtOT
Q1MDExMDY5LDI3NTYxMzYxLC05Nzg0MjUwMzcsNTczNjk1NDQ3
LC0xNjUyNzI1MjY0LDIwMzAyODA3OV19
-->