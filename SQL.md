



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


* 입양되지 않은 동물중 가장 보호소에 오래 있었던 동물 3마리 출력
```sql
SELECT NAME, DATETIME
FROM ANIMAL_INS AS A
WHERE NOT EXISTS (SELECT *
    FROM ANIMAL_OUTS AS B
    WHERE A.ANIMAL_ID = B.ANIMAL_ID)
ORDER BY DATETIME
LIMIT 3;
```
<!--stackedit_data:
eyJoaXN0b3J5IjpbMjEzNTY3ODA1MiwyMDc5MzIxNjU3LC05ND
UwMTEwNjksMjc1NjEzNjEsLTk3ODQyNTAzNyw1NzM2OTU0NDcs
LTE2NTI3MjUyNjQsMjAzMDI4MDc5XX0=
-->