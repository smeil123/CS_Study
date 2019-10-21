



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
### datetime

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
```sql
SELECT ANIMAL_ID, NAME, date_format(DATETIME,'%Y-%m-%d') AS 날짜
FROM ANIMAL_INS
```
```
날짜 출력 -> 
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

* 보호소에 들어올땐 중성화 되지 않았지만 나갈땐 중성화된 동물
```sql
-- 코드를 입력하세요
SELECT A.ANIMAL_ID, A.ANIMAL_TYPE, A.NAME
FROM ANIMAL_OUTS AS A
WHERE A.SEX_UPON_OUTCOME IN ("Spayed Female","Spayed Male","Neutered Male","Neutered Male")
AND EXISTS (SELECT B.ANIMAL_ID
              FROM ANIMAL_INS AS B
              WHERE B.ANIMAL_ID = A.ANIMAL_ID
              AND B.SEX_UPON_INTAKE IN ('Intact Male','Intact Female'))
ORDER BY A.ANIMAL_ID;
        
```

* 이름이 Null 이면 'No name'으로 출력하기
```sql
-- 코드를 입력하세요
SELECT ANIMAL_TYPE, IFNULL (NAME, 'No name') AS NAME, SEX_UPON_INTAKE
FROM ANIMAL_INS
ORDER BY ANIMAL_ID;
```

* 특정 TEXT가 포함하면 O,X로 표시하기
```sql
-- 코드를 입력하세요
SELECT ANIMAL_ID, NAME, IF(sex_upon_intake LIKE 'Neutered%' 
           OR sex_upon_intake LIKE 'Spayed%', 'O', 'X') AS '중성화' 
FROM ANIMAL_INS
ORDER BY ANIMAL_ID;
```
<!--stackedit_data:
eyJoaXN0b3J5IjpbODgxMTU5NjYzLC03MTY5MDY0MjYsLTIwNT
k2MzY1NzIsLTkxMzk3MTYxLDIxMzU2NzgwNTIsMjA3OTMyMTY1
NywtOTQ1MDExMDY5LDI3NTYxMzYxLC05Nzg0MjUwMzcsNTczNj
k1NDQ3LC0xNjUyNzI1MjY0LDIwMzAyODA3OV19
-->