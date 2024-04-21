  
# 서브쿼리 분류

1. Inline View : from 절에 있는 서브쿼리

1. Nested Subquery (중첩된) : where절에 사용된 서브쿼리

&ensp; &ensp; 1. 메인쿼리에 있는 컬럼을 참조하면 ‘상관관계 있는 서브쿼리’라고 부름

1. 스칼라 서브쿼리 : 한 레코드당 `하나의 컬럼 값`만을 리턴

&ensp; &ensp; 1. 주로  select-list에서 사용되지만, 컬럼이 올 수 있는 대부분 위치에서 사용 가능

  
>옵티마이저는 쿼리 블록 단위로 최적화 수행

  
# Unnesting ⇒ 중첩된 상태를 풀어냄

  
중첩된 상태에서 IN, Exists를 불문하고 다 `필터 방식`

**즉, 메인 쿼리에서 읽히는 **`레코드마다 서브쿼리를 반복 수행`**하면서 조건에 맞지 않는 데이터를 골라내는 것**

  
**필터 방식은 NL조인으로 이해하면 된다 ⇒ 즉 대용량 데이터를 필터할 때는 Unnest를 해서 해시 조인으로 변경하는 등의 튜닝필요**

  
서브쿼리를 처리하는데 필터 방식이 항상 최적의 수행속도 보장 X

**옵티마이저는 아래 둘 중 하나 선택(Unnest해서 더 좋은 방식이 있는지 확인)**

1. 동일한 결과를 보장하는 `조인문으로 변환` 후 최적화 ⇒ `서브쿼리 Unnesting`

1. 원래대로 둔 상태에서 최적화. 쿼리를 별도의 서브플랜으로 구분해 최적화

&ensp; &ensp; 1. 이때 서브쿼리에 Filter 오퍼레이션이 나타남

  
## 이점

- 같은 레벨로 풀어내면, 다양한 엑세스 경로와 조인 메소드 평가 가능

- 더 나은 실행계획을 찾을 가능성이 높아짐

**⇒ 옵티마이저는 서브쿼리 Unnesting을 선호**

&ensp; &ensp; 10g부터는 서브쿼리 Unnesting이 비용기반 쿼리 방식으로 전환(예상 비용이 낮을 때만 Unnesting 함)

  
### 힌트

- unnest : Unnesting하여 `조인방식`으로 최적화 유도

- no_unnest : 그대로 둔 상태에서 `필터방식`으로 최적화 유도

  
  
## 실행계획

### no_unnest ⇒ filter


 ``` 
select * from emp
where deptno in (select /*+ no_unnest */ deptno from dept);

------------------------------------------------------------------------------------------------
| Id  | Operation          | Name            | Starts | E-Rows | A-Rows |   A-Time   | Buffers |
------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |                 |      1 |        |     13 |00:00:00.01 |       7 |
|*  1 |  FILTER            |                 |      1 |        |     13 |00:00:00.01 |       7 |
|   2 |   TABLE ACCESS FULL| EMP             |      1 |     13 |     13 |00:00:00.01 |       4 |
|*  3 |   INDEX RANGE SCAN | DEPT_DEPTNO_IDX |      3 |      1 |      3 |00:00:00.01 |       3 |
------------------------------------------------------------------------------------------------

Predicate Information (identified by operation id):
---------------------------------------------------

1 - filter( IS NOT NULL)
3 - access("DEPTNO"=:B1)
 ``` 


  
- 조건절이 바인드 변수로 처리됨 (DEPTNO =: B1)

&ensp; &ensp; - 서브쿼리를 별도의 서브플랜으로 최적화함을 알 수 있음

- 메인 쿼리에서 읽히는 레코드마다 값을 넘기면서 서브쿼리를 반복 실행한다.

>무조건 EMP 테이블이 먼저 드라이빙된다
항상 메인 쿼리의 EMP를 기준으로 서브쿼리의 DEPT 테이블과 NL방식으로 조인,필터링 된다.

  
### unnest ⇒ Join


 ``` 
select * from 거래_A
where 고객번호 in (select /*+ unnest */ 고객번호 from 거래_B);

-----------------------------------------------------------------------------
| Id  | Operation            | Name | Rows  | Bytes | Cost (%CPU)| Time     |
-----------------------------------------------------------------------------
|   0 | SELECT STATEMENT     |      | 10000 |   244K|    28   (0)| 00:00:01 |
|*  1 |  HASH JOIN RIGHT SEMI|      | 10000 |   244K|    28   (0)| 00:00:01 |
|   2 |   TABLE ACCESS FULL  | 거래_| 10000 | 40000 |    16   (0)| 00:00:01 |
|   3 |   TABLE ACCESS FULL  | 거래_| 10000 |   205K|    12   (0)| 00:00:01 |
-----------------------------------------------------------------------------

Predicate Information (identified by operation id):
---------------------------------------------------

   1 - access("고객번호"="고객번호")
 ``` 


  
>unnest를 하기 위해선 서브쿼리에 rownum조건이 없어야 함!!!

### Join 순서

어느 쪽이든 드라이빙 집합으로 선택 가능

- 선택 : 옵티마이저 몫

- 판단근거 : 데이터 분포 통계정보

- 힌트로도 가능

&ensp; &ensp; 
 ``` 
/*+ leading(emp) */

/*+ ordered */ => 서브쿼리 테이블이 Driving 됌(상위 기준)

-- 10g부터는 쿼리블록에 이름 지정 가능
select /*+ leading(**dept@gb1**) * */ from emp
where deptno in (select /*+ unnest **gb_name(gb1)***/ deptno from dept)

 ``` 


  
## 서브쿼리가 M쪽 집합이거나 Nonunique 인덱스일 때

옵티마이저는 컬럼의 PK제약조건을 통해서 어디가 1쪽 집합인지 알 수 잇음

  

 ``` 
select * from dept
where deptno in (select deptno from emp)
 ``` 


- 1쪽 집합을 기준으로 M쪽 집합을 필터링하는 형태 

- 당연히 서브쿼리 쪽 EMP테이블 deptno 컬럼 : Unique 인덱스 X

- Dept 테이블이 기준 집합 ⇒ 결과 집합은 DEPT 테이블의 총 건수를 넘지 않음

  
`여기서 조인문으로 변환 시`⇒ 결과 집합에 오류 발생

  
이럴 땐 두가지 방법 중 하나 선택

- 1쪽 집합임을 확신할 수 없는 **서브쿼리 쪽  테이블** 드라이빙

&ensp; &ensp; - 먼저 `Sort Unique 오퍼레이션` 수행하여 1쪽 집합으로 만든 후 조인

- **메인 쿼리 쪽 테이블** 드라이빙

&ensp; &ensp; - `세미 조인 방식`

  
### **서브쿼리 쪽  테이블** 


 ``` 
-- 고객번호에 PK제약조건이 없는 상태로 조인
-- 책에서는 힌트를 안줬는데 그냥 수행하니 hash_semi join을 사용해서 힌트를 조정 함

select /*+ ordered */* from 거래_A
where 고객번호 in (select 고객번호 from 거래_B);

--------------------------------------------------------------------------------------
| Id  | Operation              | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
--------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT       |             | 10000 |   244K|    20   (5)| 00:00:01 |
|*  1 |  HASH JOIN             |             | 10000 |   244K|    20   (5)| 00:00:01 |
|   2 |   SORT UNIQUE          |             | 10000 | 40000 |     7   (0)| 00:00:01 |
|   3 |    INDEX FAST FULL SCAN| 거래_고객번 | 10000 | 40000 |     7   (0)| 00:00:01 |
|   4 |   TABLE ACCESS FULL    | 거래_A      | 10000 |   205K|    12   (0)| 00:00:01 |
--------------------------------------------------------------------------------------

Predicate Information (identified by operation id):
---------------------------------------------------

   1 - access("고객번호"="고객번호")
 ``` 


  
- 실제로 고객번호가 Unique 한 집합이더라도 제약조건이 없으면 옵티마이저는 SORT UNIQUE오퍼레이션을 수행함

아래와 같은 쿼리 변환 형태이 일어난 것


 ``` 
select b.*
from ( select /*+ no_merge */ distinct 고객번호 from 거래_B order by 고객번호) a,
		거래_A b
where b.고객번호 = a.고객번호
 ``` 


  
### **메인 쿼리 쪽 테이블**


 ``` 
select * from 거래_A
where 고객번호 in (select 고객번호 from 거래_B);
----------------------------------------------------------------------------------
| Id  | Operation          | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
----------------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |             | 10000 |   244K| 10015   (1)| 00:00:01 |
|   1 |  NESTED LOOPS SEMI |             | 10000 |   244K| 10015   (1)| 00:00:01 |
|   2 |   TABLE ACCESS FULL| 거래_A      | 10000 |   205K|    12   (0)| 00:00:01 |
|*  3 |   INDEX RANGE SCAN | 거래_고객번 | 10000 | 40000 |     1   (0)| 00:00:01 |
----------------------------------------------------------------------------------

Predicate Information (identified by operation id):
---------------------------------------------------

   3 - access("고객번호"="고객번호")
 ``` 


- Outer(=Driving) 테이블의 한 로우가 Inner테이블의 한 로우와 조인에 성공하는 순간 진행을 멈춤

- 만약  이렇게 안나오면 `/*+ unnest nl_sj */` 으로 유도가능 (hash_sj, merge_sj)

  
# 캐싱효과

- 서브쿼리를 Unnesting 하지 않으면 쿼리를 최적화 하는데 있어 선택의 폭이 넓지 않아 불리

- 메인 쿼리를 수행하면서 건건이 서브쿼리를 반복 수행하는 단순한 필터 오퍼레이션을 사용해야 되기 때문

- 서브쿼리 수행 결과를 버리지 않고 `내부 캐싱`을 사용함 (스칼라 서브쿼리 캐싱효과와 비슷)

  

 ``` 
select count(*) from t_emp t
where exists (select /*+ no_unnest */ 'x' from dept
where deptno = t.deptno and loc is not null)

call     count       cpu    elapsed       disk      query    current        rows
------- ------  -------- ---------- ---------- ---------- ----------  ----------
Parse        1      0.01       0.00          0          6          2           0
Execute      1      0.00       0.00          0          0          0           0
Fetch        2      0.00       0.00          0         24          3           1
------- ------  -------- ---------- ---------- ---------- ----------  ----------
total        4      0.01       0.00          0         30          5           1

Misses in library cache during parse: 1
Optimizer mode: ALL_ROWS
Parsing user id: 9  
Number of plan statistics captured: 1

Rows (1st) Rows (avg) Rows (max)  Row Source Operation
---------- ---------- ----------  ---------------------------------------------------
         1          1          1  SORT AGGREGATE (cr=24 pr=0 pw=0 time=205 us starts=1)
      1300       1300       1300   **FILTER  **(cr=24 pr=0 pw=0 time=977 us starts=1)
      1300       1300       1300    TABLE ACCESS FULL T_EMP (cr=18 pr=0 pw=0 time=251 us starts=1 cost=4 size=16900 card=1300)
         3          3          3    TABLE ACCESS BY INDEX ROWID BATCHED DEPT (cr=6 pr=0 pw=0 time=15 us starts=3 cost=1 size=11 card=1)
         3          3          3     INDEX RANGE SCAN DEPT_DEPTNO_IDX (cr=3 pr=0 pw=0 time=8 us starts=3 cost=0 size=0 card=1)(object id 73674)
 ``` 


- FILTER : 서브쿼리라 unnesting 되지 않음 확인

- dept 테이블에 대한 필터링을 1300번 수행했음에도 읽을 블록 수는 인덱스에서 3개, 테이블에서 3개, 총 6개(cr=6)

&ensp; &ensp; - 거기서 리턴된 결과 건수도 3개에 그침

&ensp; &ensp; - deptno 에는 10,20,30 세 개의 값만 있기 때문에

⇒ 결과를 캐시에 저장한 상태에서 반복적으로 재사용했음을 알 수 있음

  
**NL 세미 조인은 **10G부터 캐싱효과를 가짐

  
# Anti 조인

not exists, not in 서브쿼리도 unnesting 하지 않으면 필터 방식으로 처리

- 기본 루틴은 exists 필터와 동일

- 레코드가 하나도 없을 때만 결과집합에 포함시킨다는 점만 다름

- 조인에 성공하는 레코드를 만나는 순간 버림

  
### Unnesting

- unnest nl_aj

- unnset merge_aj

- unnest hash_aj

&ensp; &ensp; - 메인 쿼리쪽 테이블을 해시 테이블로 빌드

&ensp; &ensp; - 서브쿼리쪽을 스캔하면서 해시 테이블 탐색

&ensp; &ensp; - 조인에 성공한 엔트리에만 표시

&ensp; &ensp; - 마지막으로, 해시 테이블을 스캔하면서 표시가 없는 엔트리만 결과집합에 담음

  
# Pushing 서브쿼리

  
실행계획 상 가능한 앞 단계에서 서브쿼리 필터링이 처리되도록 강제

&ensp; &ensp; 원래 서브쿼리는 대게 실행계획 상 맨 마지막 단계에 처리됨

&ensp; &ensp; 성능에 부하를 주는 조인 다하고서 대거 필터되는 경우에 사용하면 좋음

### 이점

서브쿼리 필터링을 먼저 처리했을 때 다음 수행 단계로 넘어가는 로우 수를 크게 줄일 수 있는 경우

  
### 힌트


 ``` 
서브쿼리에서
/*+ NO_UNNEST PUSH_SUBQ */
 ``` 


- 인라인 뷰 안에 조건절을 밀어 넣는 ‘조건절 Pushing’ 과 다름 

  
### 특징

- Unnesting 되지 않은 서브 쿼리에만 작동 ( **no_unnest 와 세트**)

- 실행계획상 FILTER가 나타나지 않음

  
### 실습


 ``` 
select /*+ leading(e1) use_nl(e2) */ sum(e1.sal), sum(e2.sal)
from emp1 e1, emp2 e2
where e1.no = e2.no
and e1.empno = e2.empno
and exists (select /*+ NO_UNNEST NO_PUSH_SUBQ */ 'x'
from dept where deptno = e1.deptno
and loc='NEW YORK')

call     count       cpu    elapsed       disk      query    current        rows
------- ------  -------- ---------- ---------- ---------- ----------  ----------
Parse        1      0.00       0.00          0         16          4           0
Execute      1      0.00       0.00          0          0          0           0
Fetch        2      0.01       0.01          0      13552          4           1
------- ------  -------- ---------- ---------- ---------- ----------  ----------
total        4      0.01       0.02          0      13568          8           1

Misses in library cache during parse: 1
Optimizer mode: ALL_ROWS
Parsing user id: 9  
Number of plan statistics captured: 1

Rows (1st) Rows (avg) Rows (max)  Row Source Operation
---------- ---------- ----------  ---------------------------------------------------
         1          1          1  SORT AGGREGATE (cr=13552 pr=0 pw=0 time=16214 us starts=1)
      2997       2997       2997   **FILTER  (cr=13552 **pr=0 pw=0 time=17299 us starts=1)
     12987      12987      12987    NESTED LOOPS  (cr=13546 pr=0 pw=0 time=16985 us starts=1 cost=13360 size=1217671 card=13381)
     12987      12987      12987     NESTED LOOPS  (cr=559 pr=0 pw=0 time=9595 us starts=1 cost=13360 size=1217671 card=13381)
     12987      12987      12987      TABLE ACCESS FULL EMP1 (cr=96 pr=0 pw=0 time=1948 us starts=1 cost=25 size=695812 card=13381)
     12987      12987      12987      INDEX UNIQUE SCAN EMP2_PK (cr=463 pr=0 pw=0 time=4745 us starts=12987 cost=0 size=0 card=1)(object id 73888)
     12987      12987      12987     TABLE ACCESS BY INDEX ROWID EMP2 (cr=12987 pr=0 pw=0 time=5124 us starts=12987 cost=1 size=39 card=1)
         1          1          1    TABLE ACCESS BY INDEX ROWID BATCHED DEPT (cr=6 pr=0 pw=0 time=15 us starts=3 cost=1 size=11 card=1)
         3          3          3     INDEX RANGE SCAN DEPT_DEPTNO_IDX (cr=3 pr=0 pw=0 time=9 us starts=3 cost=0 size=0 card=1)(object id 73674)
 ``` 


- emp2와 조인 횟수가 12987회

  

 ``` 
select /*+ leading(e1) use_nl(e2) */ sum(e1.sal), sum(e2.sal)
from emp1 e1, emp2 e2
where e1.no = e2.no
and e1.empno = e2.empno
and exists (select /*+ NO_UNNEST PUSH_SUBQ */ 'x'
from dept where deptno = e1.deptno
and loc='NEW YORK')

call     count       cpu    elapsed       disk      query    current        rows
------- ------  -------- ---------- ---------- ---------- ----------  ----------
Parse        1      0.00       0.00          0         16          4           0
Execute      1      0.00       0.00          0          0          0           0
Fetch        2      0.00       0.00          0       3338          4           1
------- ------  -------- ---------- ---------- ---------- ----------  ----------
total        4      0.00       0.00          0       3354          8           1

Misses in library cache during parse: 1
Optimizer mode: ALL_ROWS
Parsing user id: 9  
Number of plan statistics captured: 1

Rows (1st) Rows (avg) Rows (max)  Row Source Operation
---------- ---------- ----------  ---------------------------------------------------
         1          1          1  SORT AGGREGATE (cr=3338 pr=0 pw=0 time=4890 us starts=1)
      2997       2997       2997   NESTED LOOPS  (cr=3338 pr=0 pw=0 time=5704 us starts=1 cost=692 size=60879 card=669)
      2997       2997       2997    NESTED LOOPS  (cr=341 pr=0 pw=0 time=4576 us starts=1 cost=692 size=60879 card=669)
      2997       2997       2997     TABLE ACCESS FULL EMP1 (cr=102 pr=0 pw=0 time=2073 us starts=1 cost=25 size=34788 card=669)
         1          1          1      TABLE ACCESS BY INDEX ROWID BATCHED DEPT (cr=6 pr=0 pw=0 time=19 us starts=3 cost=1 size=11 card=1)
         3          3          3       INDEX RANGE SCAN DEPT_DEPTNO_IDX (cr=3 pr=0 pw=0 time=13 us starts=3 cost=0 size=0 card=1)(object id 73674)
      2997       2997       2997     INDEX UNIQUE SCAN EMP2_PK (cr=239 pr=0 pw=0 time=1140 us starts=2997 cost=0 size=0 card=1)(object id 73888)
      2997       2997       2997    TABLE ACCESS BY INDEX ROWID EMP2 (cr=2997 pr=0 pw=0 time=1310 us starts=2997 cost=1 size=39 card=1)
 ``` 


- emp2와 조인 횟수가 2997회
