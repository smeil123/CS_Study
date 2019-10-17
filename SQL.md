



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
SELECT CAST(DATE_FORMAT(DATETIME,'%H') AS unsigned), COUNT(*)
FROM ANIMAL_OUTS
WHERE CAST(DATE_FORMAT(DATETIME,'%H') AS unsigned) BETWEEN 9 AND 19
GROUP BY CAST(DATE_FORMAT(DATETIME,'%H') AS unsigned)
```

* 
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTEyNjgyNDQwNDEsMjc1NjEzNjEsLTk3OD
QyNTAzNyw1NzM2OTU0NDcsLTE2NTI3MjUyNjQsMjAzMDI4MDc5
XX0=
-->