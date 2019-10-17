



* 이름이 null이 아니며 중복되지 않은 이름의 개수
```sql
SELECT COUNT(DISTINCT NAME)
FROM ANIMAL_INS
WHERE NAME IS NOT NULL
```
<!--stackedit_data:
eyJoaXN0b3J5IjpbMjAzMDI4MDc5XX0=
-->