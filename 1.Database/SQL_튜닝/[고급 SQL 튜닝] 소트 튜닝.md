
_______

# 소트 튜닝 방안 목차

- 데이터 모델 측면에서의 검토

- **소트가 발생하지 않도록 SQL 작성**

&ensp; &ensp; - 소트연산이 부하가 되지 않는 크기면 집착안해도 됌

- 인덱스를 이용한 소트 연산 대체

- **Sort Area를 적게 사용하도록 SQL 작성**

- Sort Area 크기 조정

  
# 소트 수행 과정

- 메모리 소트 : 전체 데이터의 정렬 작업을 메모리 내에서 완료

&ensp; &ensp; - Internal Sort, In-memory Sort

- 디스크 소트 : 할당받은 Sort Area + 디스크 공간까지 사용

&ensp; &ensp; - External Sort, To-Disk Sort

  
![8e218fd2-fc4d-47ed-8f29-d33346fad879](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/94e01878-505a-43c6-9ccc-1ebf14271bfa/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T194023Z&X-Amz-Expires=3600&X-Amz-Signature=e6cde74b2f5bbb8aeb8811efcafde7f6c51d502d797738bcfdf903773c560b47&X-Amz-SignedHeaders=host&x-id=GetObject)
1. 소트할 대상을 SGA 버퍼캐시를 통해 읽음

1. PGA영역 Sort Area 내에서 데이터 정렬을 수행함

1. (공간 부족 시) 중간 집합을 Temp TableSpace에 임시 세그먼트를 만들어 저장

&ensp; &ensp; 1. `Sort Run :` Sort Area가 찰 때마다 Temp 영역에 저장해 둔 중간집합 

1. (정렬이 완료 후) Merge 수행해서 결과집합 얻음

&ensp; &ensp; 1. Sort Run에서 하나씩 읽음

1. PGA로 읽고, 찰 때마다 클라이언트에게 전송하거나 쿼리 수행 다음단계로 전달

  
  
### 부하 지점

1. Temp 영역에 임시 저장했다가 다시 읽어들이는 디스크 소트가 발생하는 순간

&ensp; &ensp; 특히,  Sort Area가 각 Sort Run으로부터 하나의 청크씩 읽어 들일 정도의 크기가 안되면 읽어들이는 과정을 여러 번 반복하게 되어 극도로 나빠짐 (→ multipass sort)

&ensp; &ensp; - Optimal 소트 : Sort Area 내에서 정렬 완료** (메모리만 사용)**

&ensp; &ensp; - Onepass 소트 : 정렬 대상 집합이 **디스크에 한 번**만 쓰임

&ensp; &ensp; - Multipass 소트 : 정렬 대상 집합이 **디스크에 여러 번** 쓰임

1. 부분범위 처리 불가

# 소트 발생 오퍼레이션

## Sort Aggregate

- 전체 로우를 대상으로 집계 수행 시 나타남

- **실제 소트가 발생하지 않음**

- Sort Area를 사용한다는 의미

>sum, max, min, count


 ``` 
o sorts(memory)
0 sorts(disk)
 ``` 


<details><summary>실행예제</summary></details>

&ensp; &ensp; 
 ``` 
select max(일련번호)
from 입금;

---------------------------------------------------------------------------
| Id  | Operation	   | Name | Rows  | Bytes | Cost (%CPU)| Time	  |
---------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |	  |	1 |	4 |	6   (0)| 00:00:01 |
|   1 |  SORT AGGREGATE    |	  |	1 |	4 |	       |	  |
|   2 |   TABLE ACCESS FULL| 입금 |  5010 | 20040 |     6   (0)| 00:00:01 |
---------------------------------------------------------------------------

	  0  sorts (memory)
	  0  sorts (disk)
 ``` 


## Sort Order by

- 데이터 정렬을 위한 order by 사용 시 나타남

- 전체 데이터를 정렬할 때 나타남 ⇒ `Sort Area를 많이 사용`


 ``` 
1 sorts(memory)
0 sorts(disk)
 ``` 


<details><summary>실행예제</summary></details>

&ensp; &ensp; 
 ``` 
select *
from 입금
order by 일련번호;

---------------------------------------------------------------------------
| Id  | Operation	   | Name | Rows  | Bytes | Cost (%CPU)| Time	  |
---------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |	  |  5010 | 60120 |	7  (15)| 00:00:01 |
|   1 |  SORT ORDER BY	   |	  |  5010 | 60120 |	7  (15)| 00:00:01 |
|   2 |   TABLE ACCESS FULL| 입금 |  5010 | 60120 |     6   (0)| 00:00:01 |
---------------------------------------------------------------------------

	  1  sorts (memory)
	  0  sorts (disk)
 ``` 


## Sort Group By

- 소트 알고리즘을 사용해 그룹별 집계

- 집계할 대상 레코드가 아무리 많아도 group 갯수가 없으면 temp tablespace를 쓸 일이 없음

>group by
sort by


 ``` 
1 sorts(memory)
0 sorts(disk)
 ``` 


<details><summary>실행예제</summary></details>

&ensp; &ensp; 
 ``` 
select 고객ID, avg(입금액)
from 입금
group by 고객ID
order by 고객ID

---------------------------------------------------------------------------
| Id  | Operation	   | Name | Rows  | Bytes | Cost (%CPU)| Time	  |
---------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |	  |  1824 | 14592 |	7  (15)| 00:00:01 |
|   1 |  SORT GROUP BY	   |	  |  1824 | 14592 |	7  (15)| 00:00:01 |
|   2 |   TABLE ACCESS FULL| 입금 |  5010 | 40080 |     6   (0)| 00:00:01 |
---------------------------------------------------------------------------

	  1  sorts (memory)
	  0  sorts (disk)



select 고객ID, avg(입금액)
from 입금
group by 고객ID

---------------------------------------------------------------------------
| Id  | Operation	   | Name | Rows  | Bytes | Cost (%CPU)| Time	  |
---------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |	  |  1824 | 14592 |	7  (15)| 00:00:01 |
|   1 |  HASH GROUP BY	   |	  |  1824 | 14592 |	7  (15)| 00:00:01 |
|   2 |   TABLE ACCESS FULL| 입금 |  5010 | 40080 |     6   (0)| 00:00:01 |
---------------------------------------------------------------------------

	  0  sorts (memory)
	  0  sorts (disk)

 ``` 


### Sort Group By vs Hash Group By

**Sort Group By**

- `소팅` 알고리즘을 사용해 데이터를 그룹핑

- 읽는 로우마다 그룹을 찾아가 집계항목 갱신(↔ 모든 데이터를 정렬하고 나서 집계)

&ensp; &ensp; - 어떻게 찾아가는가? 소팅방식 group by 컬럼값이 정렬되어 있음

&ensp; &ensp; - 결과집합의 건수 만큼만 sort area 사용

  
**Hash Group By (10gR2 이후)**

- `해싱` 알고리즘을 사용해 데이터를 그룹핑

- 읽는 로우마다 group by 컬럼의 해시 값으로 해키 버킷을 찾아가 그룹별로 집계항목 갱신

- **order by 절을 명시하지 않으면 대부분 이 방식으로 처리**

  
**statistics 항목에 sort가 0으로 나옴**

&ensp; &ensp; ### 비활성화

&ensp; &ensp; 
 ``` 
alter system set "_gby_hash_aggregation_enabled" = false;
 ``` 


  
>둘의 차이점 : 그룹을 찾아가는 방식이 해싱이냐 소팅이냐
집계할 대상 로우가 아무리 많아도 그룹 갯수가 소수이면 모두 디스크 소트가 전혀 발생하지 않음

  
### 예시


 ``` 
select deptno, job, sum(sal), max(sal), min(sal)
from emp
group by deptno, job;
=> hash group by 

select deptno, job, sum(sal), max(sal), min(sal)
from emp
group by deptno, job
order by deptno, job;
=> sort group by
 ``` 


  
### Group by 정렬 순서

group by 결과의 정렬 순서는 보장되지 않음 (sort나 hash나 동일)

  
## Sort Unique

- Distinct 연산

&ensp; &ensp; - Exists로 변환해야 함

- **Union**, **Minus **집합 연산

&ensp; &ensp; - Union : Union All 후 SORT UNIQUE 수행

- Unnesting 된 서브쿼리가 M쪽 집합(또는 NonUnique 인덱스) + Non Semi Join (exists X)

&ensp; &ensp; - 만약, PK/Unique 제약이 있으면 생략됨

&ensp; &ensp; <details><summary>예시 쿼리</summary></details>

&ensp; &ensp; &ensp; &ensp; 
 ``` 
select /*+ ordered use_nl(dept) */ * from dept
where deptno in (select /*+ unnest */ deptno
									from emp where job = 'CLERK');
 ``` 



 ``` 
1 sorts(memory)
0 sorts(disk)
 ``` 


<details><summary>실행예제</summary></details>

&ensp; &ensp; 
 ``` 
select distinct 일련번호
from 입금
where 입금액 >50000
order by 일련번호
---------------------------------------------------------------------------
| Id  | Operation	   | Name | Rows  | Bytes | Cost (%CPU)| Time	  |
---------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |	  |  2530 | 20240 |	8  (25)| 00:00:01 |
|   1 |  SORT UNIQUE	   |	  |  2530 | 20240 |	7  (15)| 00:00:01 |
|*  2 |   TABLE ACCESS FULL| 입금 |  2530 | 20240 |     6   (0)| 00:00:01 |
---------------------------------------------------------------------------

	  1  sorts (memory)
	  0  sorts (disk)


select distinct 일련번호
from 입금
where 입금액 >50000
---------------------------------------------------------------------------
| Id  | Operation	   | Name | Rows  | Bytes | Cost (%CPU)| Time	  |
---------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |	  |  2530 | 20240 |	7  (15)| 00:00:01 |
|   1 |  HASH UNIQUE	   |	  |  2530 | 20240 |	7  (15)| 00:00:01 |
|*  2 |   TABLE ACCESS FULL| 입금 |  2530 | 20240 |     6   (0)| 00:00:01 |
---------------------------------------------------------------------------

	  0  sorts (memory)
	  0  sorts (disk)

 ``` 


### Sort Unique vs Hash Unique

- Sort Unique에는 1 memory sort 발생

- Hash Unique에는 없음

  
위와 비슷하게

**distinct 연산에서 group/order by 생략 ⇒ Hash Unique 방식으로 수행**

  
## Sort Join

- 소트 머지 조인 /*+ use_merge(e) */


 ``` 
2 sorts(memory)
0 sorts(disk)
 ``` 


  
##  Window Sort

- 윈도우 함수 사용

&ensp; &ensp; <details><summary>예시 쿼리</summary></details>

&ensp; &ensp; &ensp; &ensp; 
 ``` 
select empno, ename, job, mgr, sal
			 , avg(sal) over (partition by deptno) -- 해당 부서의 평균 연봉
from emp;
 ``` 


  
_______
# SQL튜닝으로 소트 생략

### Union ⇒ Union All 로 튜닝


 ``` 
select *
from 결제
where 결제일자 = '20200202'
union
select *
from 결제
where 결제일자 = '20200205'

=> 이렇게 하면 union all -> sort(unique) 연산 수행

select *
from 결제
where 결제일자 = '20200202'
union all
select *
from 결제
where 결제일자 = '20200205'
and 결제일자 <> '20200202'

=> 이렇게하면 sort연산 발생하지 않음
 ``` 


만약 결제일자가 NULL 허용일 경우


 ``` 
방법 1)
and (결제일자 <> '20200205' and 결제일자 is null)
방법 2) 컬럼이 null 이면 True. 내부조건이 false 이면 True
and LNNVL(결제일자 = '20200205')

 ``` 


### Distinct ⇒ Exists 로 튜닝

Distinct는 조건에 해당하는 데이터를 모두 읽고 중복 제거 (당연 부분범위처리도 불가)

  
<details><summary>예시 1</summary></details>

&ensp; &ensp; 
 ``` 
select distinct 과금연월
from 과금
where 과금연월 <= :yyyymm
and 지역 like :reg || '%';

=> Hash Unique 수행

select 연월
where 연월테이블 a
where 연월 <= :yyyymm
and exists (
		select 'x'
		from 과금
		where 과금연월 a.연월
		and 지역 like :reg || '%'
)

=> ns semi 조인 발생
 ``` 


<details><summary>예시 2</summary></details>

&ensp; &ensp; 
 ``` 
select DISTINCT p.상품번호, p.상품명, ...
from 상품 p, 계약 c
where p.상품유형코드 = :pclscd
and c.상품번호 = p.상품번호
and c.계약일자 between :dt1 and :dt2
and c.계약구분코드 = :ctpcd

-- 계약에는 여러 상품이 있지만, 상품은 중복이 없음
-- 상품 테이블을 기준으로 filter를 거는게 나음

select 상품번호 ..
from 상품
where p.상품유형코드 = :pclscd
and exists ( select 'x'
						from 계약 c
						where c.상품번호 = 상품번호
						and c.계약일자 between :dt1 and :dt2
						and c.계약구분코드 = :ctpcd)
 ``` 


  
### 조인

>NL 조인밖에 없음
**단, 조인 기준이 조인 키 컬럼이면 ⇒ 소트 머지도 생략 가능 (부분 범위 처리가 가능)**


 ``` 
-- 계약_X01 : 지점ID + 계약일시

select /*+ leading(c) use_nl(p) */ c.*
from 계약 c, 상품 p
where c.지점ID = :brch_id
and p.상품코드 = c.상품코드
**order by c.계약일시 desc  -- 명시되어 있어도 실행계획에서 sort는 생략됨**
 ``` 


  
# 인덱스를 사용해 소트 생략

## 소트 생략 가능한 인덱스 구성법

>1 ‘=‘ 연산자로 사용된 컬럼

&ensp; &ensp; 2 order by/group by 절 컬럼

&ensp; &ensp; 3 그 외에는 데이터 분포를 고려해 추가 여부 결정

>IN은 ’=‘ 이 아님

  
### Sort Group By 생략

인덱스를 사용해서 group by 문을 사용하면 생략

**sort group by nosort**

  
  
## 페이징 처리

부분범위 처리가 가능해야 한다.

>즉, Top N Stopkey 알고리즘이 작동

1. 인라인 뷰 안쪽에 Order by 명시

1. 바깥쪽에 ROWNUM ≤ 조건 명시

  
### Top N 쿼리 (ROWNUM)

전체 결과집합 중 상위 N개 레코드만 선택하는 쿼리

>mssql 에서는 TOP 10으로 간단하게 가능하지만, 오라클에서는 Rownum활용


 ``` 
select * from(
	select 거래일시, 거래금액 ..
	from 종목거래
	where 종목코드 = 'KR123456'
	and 거래일시 >= '20200202'
	**order by 거래일시**)
**where rownum <= 10**
 ``` 


쿼리만 보면, 중간집합을 만들어야 하므로 부분범위 처리가 불가능해 보이지만

`종목코드+거래일시` 순으로 인덱스를 구성하면,

1. 옵티마이저는 소트연산을 생략

1. 인덱스를 스캔하다가 열 개 레코드를 읽는 순간 바로 멈춤 ⇒ `COUNT (STOPKEY)`

&ensp; &ensp; 1. 내가 봤을 땐 **rownum** 이 가지는 강력함으로 보임

>sort 연산이 생략되었더라도 COUNT옆에 Stopkey가 없으면 전체범위를 처리한다는 뜻

  
**만약 인덱스활용을 못하면?**

Sort Area라도 줄이면 좋고, Top N Sort 알고리즘을 사용하는게 무의미하지 않음

order by 절에 있는 컬럼이 인덱스가 없는 경우


 ``` 
select *
from (
	select rownum no , a.*
	from (
		select ename, deptno, mgr, sal
		from emp1
		where deptno = 20
		and mgr = 7788
		order by sal desc) a
	where rownum <= 20
)
where no >=  10;

---------------------------------------------------------------------------------
| Id  | Operation                | Name | Rows  | Bytes | Cost (%CPU)| Time     |
---------------------------------------------------------------------------------
|   0 | SELECT STATEMENT         |      |    20 |  1580 |    26   (4)| 00:00:01 |
|*  1 |  VIEW                    |      |    20 |  1580 |    26   (4)| 00:00:01 |
|*  2 |   **COUNT STOPKEY    **      |      |       |       |            |          |
|   3 |    VIEW                  |      |   333 | 21978 |    26   (4)| 00:00:01 |
|*  4 |     **SORT ORDER BY STOPKEY**|      |   333 |  5661 |    26   (4)| 00:00:01 |
|*  5 |      **TABLE ACCESS FULL**   | EMP1 |   333 |  5661 |    25   (0)| 00:00:01 |
---------------------------------------------------------------------------------
 ``` 


- Sort Order By Stopkey

&ensp; &ensp; - sort 연산을 수행하지만 `TOP N 소트` 알고리즘이 작동

&ensp; &ensp; - 소트 연산(=값 비교) 횟수와 Sort Area 사용량을 최소화해줌

&ensp; &ensp; - 즉, Page로 반환할 10개의 원소를 담을 배열 공간만 있으면 됌

&ensp; &ensp; &ensp; &ensp; - 메모리 소트로 가능, 디스크 사용 X

>대상 집합이 아무리 커도 많은 메모리 공간이 필요 없음
전체 레코드를 다 정렬하지 않고도 오름차순으로 최솟값 10개를 구할 수 있음
이것이 Top N 소트 알고리즘이 소트 연산 횟수와 Sort Area 사용량을 줄여주는 원리

10개의 순서만 필요하고, 그 보다 작은것들의 순서는 중요하지 않기 때문

  
  
>! 여기서 rownum에 alias를 붙여서 비교하게되면 알고리즘 사용불가

## 최솟값 / 최대값 구하기 (FIRST ROW)

Sort Aggregate는 전체 데이터를 정렬하진 않지만, 전체 데이터를 읽으면서 값을 비교한다

→ 인덱스를 사용하면 전체를 안읽어도 쉽게 찾을 수 있다.

  
**인덱스를 이용하기 위한 조건**

>①조건절 컬럼, ②MIN/MAX 함수 인자 
       → 모두 인덱스 포함(순서중요) 즉, 테이블 엑세스 발생 X


 ``` 
------------------------------------------------------------------------------------------
| Id  | Operation                    | Name      | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT             |           |     1 |    11 |     1   (0)| 00:00:01 |
|   1 |  SORT AGGREGATE              |           |     1 |    11 |            |          |
|   2 |   **FIRST ROW                  **|           |     1 |    11 |     1   (0)| 00:00:01 |
|*  3 |    INDEX **RANGE SCAN (MIN/MAX)**| EMP_IDX02 |     1 |    11 |     1   (0)| 00:00:01 |
------------------------------------------------------------------------------------------
 ``` 


First Row 는 조건을 만족하는 레코드를 찾았을 때 바로 멈춘다는 것을 의미

`First Row Stopkey`

  

 ``` 
select max(sal) from emp where deptno=20 and mgr=7788;

[인덱스 없을 때]
-----------------------------------------------------------------------------------------------------
| Id  | Operation                            | Name         | Rows  | Bytes | Cost (%CPU)| Time     |
-----------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                     |              |     1 |    11 |     2   (0)| 00:00:01 |
|   1 |  SORT AGGREGATE                      |              |     1 |    11 |            |          |
|*  2 |   TABLE ACCESS BY INDEX ROWID BATCHED| EMP          |     1 |    11 |     2   (0)| 00:00:01 |
|*  3 |    INDEX RANGE SCAN                  | EMP_DEPT_IDX |     4 |       |     1   (0)| 00:00:01 |
-----------------------------------------------------------------------------------------------------
 ``` 


**[인덱스 있을 때]**
1. DEPT + MGR + SAL


 ``` 
------------------------------------------------------------------------------------------
| Id  | Operation                    | Name      | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT             |           |     1 |    11 |     1   (0)| 00:00:01 |
|   1 |  SORT AGGREGATE              |           |     1 |    11 |            |          |
|   2 |   **FIRST ROW   **               |           |     1 |    11 |     1   (0)| 00:00:01 |
|*  3 |    INDEX RANGE SCAN (MIN/MAX)| EMP_IDX02 |     1 |    11 |     1   (0)| 00:00:01 |
------------------------------------------------------------------------------------------
 ``` 


2. DEPTNO + SAL


 ``` 
--------------------------------------------------------------------------------------------------
| Id  | Operation                            | Name      | Rows  | Bytes | Cost (%CPU)| Time     |
--------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                     |           |     1 |    11 |     2   (0)| 00:00:01 |
|   1 |  SORT AGGREGATE                      |           |     1 |    11 |            |          |
|*  2 |   TABLE ACCESS BY INDEX ROWID BATCHED| EMP       |     1 |    11 |     2   (0)| 00:00:01 |
|*  3 |    INDEX RANGE SCAN                  | EMP_IDX02 |     4 |       |     1   (0)| 00:00:01 |
--------------------------------------------------------------------------------------------------
 ``` 


![2d387329-01df-4954-a8f5-49fd0f0d56c9](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/bb1c37ba-9792-460b-a4b5-f28da466356a/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T194032Z&X-Amz-Expires=3600&X-Amz-Signature=605528b890b21b4be8510e72ba7d44ccedc9833de6c1fc9e01771bef4e62c071&X-Amz-SignedHeaders=host&x-id=GetObject)
- MGR 조건은 테이블 필터링

- deptno 조건을 만족하는 '전체' 레코드를 읽고 테이블 필터링한 후 max값을 찾음

&ensp; &ensp; - First row stopkey X


`Top N 쿼리 활용`** → **인덱스를 추가하지 않고 튜닝


 ``` 
select /*+INDEX(emp emp_IDX02)*/*
from (
	select SAL
	from emp
	where deptno = 20
	and mgr = 7788
	order by sal desc)
where rownum <= 1;

--------------------------------------------------------------------------------------------
| Id  | Operation                      | Name      | Rows  | Bytes | Cost (%CPU)| Time     |
--------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT               |           |     1 |    13 |     2   (0)| 00:00:01 |
|*  1 | ** COUNT STOPKEY **                |           |       |       |            |          |
|   2 |   VIEW                         |           |     1 |    13 |     2   (0)| 00:00:01 |
|*  3 |    TABLE ACCESS BY INDEX ROWID | EMP       |     1 |    11 |     2   (0)| 00:00:01 |
|*  4 |     INDEX RANGE SCAN **DESCENDING**| EMP_IDX02 |     4 |       |     1   (0)| 00:00:01 |
--------------------------------------------------------------------------------------------
 ``` 


`DEPTNO + SAL`

![0e9b711f-8d20-46b9-ba21-1738a5a6a92b](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/c2a6a7c1-6dcb-41fd-b4e5-24f54049beaa/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T194032Z&X-Amz-Expires=3600&X-Amz-Signature=6aa6397ecdd4838001d2f988341afca16ddc3c55f643355cb2a9a594dfd3e81d&X-Amz-SignedHeaders=host&x-id=GetObject)
- sal 이 인덱스가 있어 sort 생략

1. DESC 탐색으로 역순으로 스캔시도

1. 한 건씩 테이블 엑세스하다가 MGR조건을 만족하면 멈춤

- DEPTNO = 30인 전체 레코드를 읽지 않음

>Top N Stopkey 알고리즘은 모든 컬럼이 인덱스에 포함돼 있지 않아도 동작

  
## Group By 연산 생략

그룹핑 연산에도 인덱스 활용 가능

  
## 분석함수에서의 Top N 소트

윈도우 함수 중 rank나 row_number함수는 max함수보다 소트 부하가 적다.

&ensp; &ensp; → Top N 소트 알고리즘이 작동하기 때문


 ``` 
select ...
from (select ...
						, max(변경순번) over (partition by 장비번호) 최종변경순번)
			from 상태변경이력
			where 변경일자 =:upd_dt)
where 변경순번 = 최종변경순번
 ``` 


- 전체를 읽고 max값을 찾아와 많은 I/O 발생


 ``` 
select ...
from (select ...
						, rank() over(partition by 장비번호 order by 변경순번 desc) rnum)
			from 상태변경이력
			where 변경일자 =:upd_dt)
where rnum = 1

 ``` 


- 장비번호, 변경순번 인덱스를 사용하기 때문에 Top N 소트 알고리즘 동작함

## Sort Area를 적게 사용하도록 SQL 작성

order by sql문에서 select되는 컬럼들이 모두 sort area에 저장되는 점 잊지말자

  
  

 ``` 
------------------------------------------------------------------------------------------------------
| Id  | Operation                                 | Name     | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                          |          |     1 |    66 |  9122K  (1)| 00:05:57 |
|*  1 |  COUNT STOPKEY                            |          |       |       |            |          |
|   2 |   VIEW                                    |          |   169 | 11154 |  9122K  (1)| 00:05:57 |
|*  3 |    SORT ORDER BY STOPKEY                  |          |   169 | 13858 |  9122K  (1)| 00:05:57 |
|   4 |     NESTED LOOPS                          |          |   169 | 13858 |  9122K  (1)| 00:05:57 |
|   5 |      NESTED LOOPS                         |          |    11M| 13858 |  9122K  (1)| 00:05:57 |
|   6 |       NESTED LOOPS                        |          |   174 |  5742 | 63272   (1)| 00:00:03 |
|   7 |        TABLE ACCESS BY INDEX ROWID BATCHED| T2       |   174 |  3480 |    17   (0)| 00:00:01 |
|*  8 |         INDEX RANGE SCAN                  | T2_IDX01 |   174 |       |     1   (0)| 00:00:01 |
|*  9 |        TABLE ACCESS FULL                  | T3       |     1 |    13 |   364   (1)| 00:00:01 |
|  10 |       INDEX FULL SCAN                     | T_IDX    | 68156 |       |   448   (1)| 00:00:01 |
|* 11 |      TABLE ACCESS BY INDEX ROWID          | T        |     1 |    49 | 52063   (1)| 00:00:03 |
------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------------------------------------
| Id  | Operation                                 | Name     | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                          |          |   169 | 13351 |  9122K  (1)| 00:05:57 |
|*  1 |  VIEW                                     |          |   169 | 13351 |  9122K  (1)| 00:05:57 |
|   2 |   SORT ORDER BY                           |          |   169 | 13858 |  9122K  (1)| 00:05:57 |
|   3 |    COUNT                                  |          |       |       |            |          |
|   4 |     NESTED LOOPS                          |          |   169 | 13858 |  9122K  (1)| 00:05:57 |
|   5 |      NESTED LOOPS                         |          |    11M| 13858 |  9122K  (1)| 00:05:57 |
|   6 |       NESTED LOOPS                        |          |   174 |  5742 | 63272   (1)| 00:00:03 |
|   7 |        TABLE ACCESS BY INDEX ROWID BATCHED| T2       |   174 |  3480 |    17   (0)| 00:00:01 |
|*  8 |         INDEX RANGE SCAN                  | T2_IDX01 |   174 |       |     1   (0)| 00:00:01 |
|*  9 |        TABLE ACCESS FULL                  | T3       |     1 |    13 |   364   (1)| 00:00:01 |
|  10 |       INDEX FULL SCAN                     | T_IDX    | 68156 |       |   448   (1)| 00:00:01 |
|* 11 |      TABLE ACCESS BY INDEX ROWID          | T        |     1 |    49 | 52063   (1)| 00:00:03 |
-----------------------------------------------------------------------------------------------------
 ``` 


  
![e15d2d54-da3b-4826-ae3e-b3821270c315](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/99b4c9f0-007a-41d9-b711-a70966bc5cba/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T194032Z&X-Amz-Expires=3600&X-Amz-Signature=d8ab8b8129c3805e24995998b97774bd846deec79e72f4019beb295e1d11e8a6&X-Amz-SignedHeaders=host&x-id=GetObject)
  