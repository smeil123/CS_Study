
_______
  
# 계층 질의

부서 트리나 게시글-댓글 트리를 생성할 때 사용해야되는 구문으로

상위 하위가 나뉘어진 데이터를 계층 트리로 만드는 방법이다.

  
작성 방법에는 크게 2가지가 있다.

1. Connect by

1. Recursive With (11gR2 부터)


 ``` 
select LPAD(' ',LEVEL*2-2)||ename as NAME, LEVEL, empno, mgr
from emp -- 1번
-- where,..  -- 4번
start with empno = 7839-- 2번
connect by prior empno = mgr -- 3번
 ``` 


![ad437f22-7357-4084-9fc2-e04678985805](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/8c284ad2-56ef-4813-9489-6130387faa14/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193951Z&X-Amz-Expires=3600&X-Amz-Signature=d60b893b0a4b5efba901b11be5d345e3472a668d261070e3fcac88a3bcc26ca5&X-Amz-SignedHeaders=host&x-id=GetObject)
- START WITH 절 : 시작점 (루트행)을 찾는 문장

&ensp; &ensp; - where절보다 먼저 수행

&ensp; &ensp; - 생략도 가능함

&ensp; &ensp; &ensp; &ensp; - 생략 시, 모든 행이 한 번씩 시작 점으로 계층 질의 수행됨(모든 경우의 수 표현)

&ensp; &ensp; &ensp; &ensp; - 꼭 유니크한 값으로 하지 않아도 된

- Connect By 절 : 계층 질의 조건

&ensp; &ensp; - prior 키워드가 붙은 컬럼을 먼저 접근하게 됨

&ensp; &ensp; &ensp; &ensp; - prior empno 가 먼저 드라이빙 되어 mgr=7839를 찾음

&ensp; &ensp; &ensp; &ensp; - 이 과정이 레코드 단위로 반복 수행됨, 더 이상 매칭되는 값이 없을 때까지

- LEVEL : 계층 질의의 계층 Depth

&ensp; &ensp; - Connect By절이 있을 때만 가능

&ensp; &ensp; - Start With 절이 Level 1

- Where 절 : 계층 트리를 다 만든 후 조건이 수행된다

&ensp; &ensp; - SCOTT 행을 제외하는 조건이 있으면 scott만 제외되고 그 하위 레코드는 정상적으로 보인다

### 실행계획


 ``` 
------------------------------------------------------------------------------------------------------
| Id  | Operation                             | Name         | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                      |              |     3 |    99 |     5  (40)| 00:00:01 |
|*  1 |  CONNECT BY WITH FILTERING            |              |       |       |            |          |
|   2 |   TABLE ACCESS BY INDEX ROWID         | EMP          |     1 |    14 |     1   (0)| 00:00:01 |
|*  3 |    INDEX UNIQUE SCAN                  | EMP_EMPNO_IX |     1 |       |     0   (0)| 00:00:01 |
|   4 |   NESTED LOOPS                        |              |     2 |    54 |     2   (0)| 00:00:01 |
|   5 |    CONNECT BY PUMP                    |              |       |       |            |          |
|   6 |    TABLE ACCESS BY INDEX ROWID BATCHED| EMP          |     2 |    28 |     1   (0)| 00:00:01 |
|*  7 |     INDEX RANGE SCAN                  | EMP_MGR_IX   |     2 |       |     0   (0)| 00:00:01 |
------------------------------------------------------------------------------------------------------
 
Predicate Information (identified by operation id):
---------------------------------------------------
 
   1 - access("MGR"=PRIOR "EMPNO")
   3 - access("EMPNO"=7839)
 ``` 


## Connect_by_root 연산자

최상위 루트 노드의 컬럼값을 참조할 수 있다.


 ``` 
select connect_by_root sal as root_sal
...
 ``` 


  
## SIBLINGS 키워드

계층질의에서 order by 절을 사용하면 정렬이 되긴 하지만 트리 구조가 깨져서 나온다.

정렬하려는 컬럼의 트리 형태를 훼손하지 않고 같은 레벨에서의 정렬을 수행하는 방법은 아래와 같다


 ``` 
ORDER SIBLINGS BY ename;
 ``` 


  
## SYS_CONNECT_BY_PATH 함수

계층질의에서만 사용 가능한 함수이며 루트 노드부터 현재 노드까지 지정된 문자를 구분자로 연결


 ``` 
select lpad(' ',LEVEL*2-2) || ename AS NAME,
			sys_connect_by_path(ename,'/') as path
from emp
start with empno=7839
connect by prior empno = mgr;
 ``` 


![638c7744-0e4f-41e3-90f5-c6b002f3a89e](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/9352c2f0-c0f4-4935-9336-f68fd7e01cac/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193951Z&X-Amz-Expires=3600&X-Amz-Signature=6087cb57329f5ea215a41b93ec19628fff80eace99aa2760d6f0aff468d5a5a4&X-Amz-SignedHeaders=host&x-id=GetObject)
  
## Connect_by_isleaf

현재 노드가 계층의 마지막 leaf 값인지 확인하는 방법이다.

- Leaf 노드면 1

- 아니면 0


 ``` 
select lpad(' ',LEVEL*2-2) || ename AS NAME,
      level, empno, mgr,
      connect_by_isleaf
from emp
start with empno=7839
connect by prior empno = mgr;
 ``` 


![b75d3455-cd63-4283-99e5-92a9a099f16d](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/d44fe0e3-8dff-49df-ae0a-765963fcf235/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193951Z&X-Amz-Expires=3600&X-Amz-Signature=2609713630deb8aaa57b0d4e56755fc2f1c81588c55904c813fa7a53eac510ac&X-Amz-SignedHeaders=host&x-id=GetObject)
  
## Connect_by_iscycle

계층 질의에서 무한 루프가 발생하면 에러가 발생하는데

무한 루프 유무를 확인할 수 있다.

- 1이면 무한 루프가 있음

- connect by nocycle : 사이클이 있을 때 더 이상 계층 질의를 하지 말라는 키워드, 만약에 루프가 있는데 이 키워드를 빼면 오류가 발생함


 ``` 
select lpad(' ',LEVEL*2-2) || ename AS NAME,
      level, empno, mgr,
      connect_by_iscycle
from emp
start with empno=7839
connect by nocycle prior empno = mgr;
 ``` 


  
# Recursive With 절 (ANSI 표준)

Oracle은 11gR2부터 지원한다.

반복 실행되는 문장을 WITH절에 정의해주는 형태로,

이때 어떤 문장을 반복 수행할지는 규칙에 따르는데 규칙은 아래와 같다.

  

 ``` 
WITH **htree **(hlevel, ename, empno, mgr) 
  AS ( SELECT 1, ename, empno, mgr 
         FROM emp 
        WHERE empno = 7839
        UNION ALL
       SELECT hlevel + 1, e.ename, e.empno, e.mgr 
         FROM emp e, **htree **h
        WHERE e.mgr = h.empno ) 
SEARCH BREADTH FIRST BY empno ASC SET idx
 SELECT LPAD(' ',hlevel * 2 - 2)||ename AS name, hlevel, empno, mgr, idx
  FROM htree

 ``` 


![eaaf8123-e235-4f01-babd-1572477e18fd](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/f918919d-5510-431c-a7ac-bbf94051a172/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193951Z&X-Amz-Expires=3600&X-Amz-Signature=6d715b32dab6e549bd7571ceb4db0080a917eb931c981d0a025841f536e5b307&X-Amz-SignedHeaders=host&x-id=GetObject)
WITH절이 보이는데 일반적인 With절과 실행 순서가 다르다.

>With절을 먼저 임시 테이블을 생성하는데, 위 쿼리를 보면 본인 쿼리블록을 안에서 다시 사용하는 형태이다.

**실행순서**

1. with절 내 **Union All** 앞의 쿼리 블록이 먼저 수행(Anchor member)

&ensp; &ensp; 1. Start With를 검색하는 부분

&ensp; &ensp; 1. `UNION ALL`은 쿼리 블록을 구분해주는 키워드로 사용

&ensp; &ensp; 1. 해당 문장이 htree

1. 1번의 검색 내용은 Recursive Member로 들어가서 수행

&ensp; &ensp; 1. KING밑에 근무하는 사원 3명이 검색

&ensp; &ensp; 1. 이 결과가 다시 htree에 저장되서 출력 → With절이 반복되서 실행되면서 저장

&ensp; &ensp; 1. 그 결과가 다시 2번으로 수행

&ensp; &ensp;   
### 실행계획


 ``` 
----------------------------------------------------------------------------------------------------------
| Id  | Operation                                 | Name         | Rows  | Bytes | Cost (%CPU)| Time     |
----------------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                          |              |   203 | 11977 |    16   (7)| 00:00:01 |
|   1 |  VIEW                                     |              |   203 | 11977 |    16   (7)| 00:00:01 |
|   2 |   UNION ALL (RECURSIVE WITH) BREADTH FIRST|              |       |       |            |          |
|   3 |    TABLE ACCESS BY INDEX ROWID            | EMP          |     1 |    14 |     1   (0)| 00:00:01 |
|*  4 |     INDEX UNIQUE SCAN                     | EMP_EMPNO_IX |     1 |       |     0   (0)| 00:00:01 |
|*  5 |    HASH JOIN                              |              |   202 |  8080 |    14   (0)| 00:00:01 |
|   6 |     BUFFER SORT (REUSE)                   |              |       |       |            |          |
|   7 |      TABLE ACCESS BY INDEX ROWID BATCHED  | EMP          |    13 |   182 |     2   (0)| 00:00:01 |
|*  8 |       INDEX FULL SCAN                     | EMP_MGR_IX   |    13 |       |     1   (0)| 00:00:01 |
|   9 |     RECURSIVE WITH PUMP                   |              |       |       |            |          |
----------------------------------------------------------------------------------------------------------
 
Predicate Information (identified by operation id):
---------------------------------------------------
 
   4 - access("EMPNO"=7839)
   5 - access("E"."MGR"="H"."EMPNO")
   8 - filter("E"."MGR" IS NOT NULL)
 ``` 


  
### **특징**

- LEVEL, SYS_CONNECT_BY_PATH 등을 사용할 수 없다

&ensp; &ensp; - 동일한 값을 만드려면 직접 표현식을 만들어서 사용해야 된다.

# 계층질의 vs Recursive With

계층질의가 트리 형태로 결과를 출력하기에는 문장을 작성하기 더 쉽다.

하지만 그 결과를 다시 사용해서 출력 값을 뽑아내기에는 어렵다

  
**계층질의 특징**

- 루트 노드, 상위 노드 값만 참조 가능

- 그 중간 레벨 값은 참조가 쉽지 않다

&ensp; &ensp; - sys_connect_by_path로 중간값 나열은 가능하지만 문자라서 계산은 쉽지 않다

- 계층 트리를 보여주기위한 목적으로 적절

  
**Q. 루트 노드부터 현재 노드까지의 급여를 누적**

recursive with


 ``` 
WITH htree(hlevel, ename, empno, mgr, sal, formula, sum_sal) 
AS ( SELECT 1, ename, empno, mgr, sal, TO_CHAR(sal), sal
       FROM emp 
      WHERE mgr IS NULL 
      UNION ALL
     SELECT hlevel + 1, e.ename, e.empno, e.mgr, e.sal
           ,h.formula||'+'||TO_CHAR(e.sal)
           ,h.sum_sal + e.sal
       FROM emp e, htree h
      WHERE e.mgr = h.empno ) 
SEARCH DEPTH FIRST BY empno ASC SET idx      
SELECT LPAD(' ',hlevel * 2 - 2)||ename AS name, hlevel, empno, mgr, sal, formula, sum_sal
  FROM htree ;
 ``` 


  
계층 질의


 ``` 
SELECT LPAD(' ',LEVEL*2-2)||ename AS NAME, level, empno, mgr, sal
      ,LTRIM(SYS_CONNECT_BY_PATH(sal,'+'),'+') AS FORMULA
      ,(SELECT SUM(sal) 
          FROM emp 
         START WITH empno = e.empno 
         CONNECT BY empno = PRIOR mgr) AS SUM_SAL
  FROM emp e 
 START WITH empno = 7839
CONNECT BY prior empno = mgr ;

 ``` 


![1aabf4a0-b4e3-4299-9b4e-0ed7b82bea50](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/b45f00a9-8748-42ff-8974-437b0c93fb21/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193951Z&X-Amz-Expires=3600&X-Amz-Signature=26444cb390023cd1a649ea6786a8d81bf57a8d80a979932f76d39ec85d19a2dc&X-Amz-SignedHeaders=host&x-id=GetObject)
Recursive with절에서는 기존 문법에서 select절에 추가하여 구현하였고

계층질의에서는 스칼라 서브쿼리를 이용해서 역방향 트리를 만들어 구현했다.

  
계층 질의로도 계산은 가능하다 emp절을 다시 호출해야되고 + 분석함수로 Sum을 해야되는 등의 제약이 있어 더 복잡한 계산식을 구현이 어려울 수 있다.

  