



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


```sql

`
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTMxMjcxMDM0OCwtMTY1MjcyNTI2NCwyMD
MwMjgwNzldfQ==
-->