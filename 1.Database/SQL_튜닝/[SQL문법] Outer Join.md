  

_______
  
튜닝의 영역이 아닌 기능의 조인에는 Outer, Inner, Cross 조인이 있다.

Inner조인은 워낙 기본적으로 사용되는 것이고, Cross조인은 잘 사용하지 않는다.

  
Outer 조인은 가끔 쓸일이 생기는데 쓸때마다 헷갈리고 특히 Oracle 문법이 한번에 와닿지 않는다

이번에 이 개념을 제대로 정리하려고 한다.

# 기본 문법

1. **ANSI 구문**


 ``` 
--- 추가되어야하는 테이블이 왼쪽에 있으면 left로
from dept d left outer join emp e
on e.deptno = d.deptno;

--- 반대로 오른쪽에 있어야하면
from emp e right outer join dept d
 ``` 


ANSI구문은 키워드를 통해서 어디를 기준으로 Outer조인할 지 정하게 된다.

위 구문 처럼 left, right 키워드로 방향을 정하고

- Left → 왼쪽이 기준

- Right → 오른쪽이 기준

매우 직관적으로 표현되는데, 그림으로 이해하면 아래와 같다. 


1. **Oracle 구문**


 ``` 
where emp.dept(+) = dept.dept -- emp에 없는 dept 를 넣어주겠다 (+되는건 dept쪽)
 ``` 


ANSI구문과 다르게 `(+)` 기호를 사용해서 방향을 정한다.

>이 부분이 헷갈리는 포인트 였다.

**정리하면**

- (+) 가** 없는 쪽**이 먼저 access(driving)된다

  
1. DEPT 테이블을 먼저 읽는 기준이 되고

1. DEPT 테이블 기준으로 emp를 찾아간다.

  
결과는 EMP에 없는 DEPT 로우가 모두 출력된다

## **ANSI 구문 주의 ( 선택적 OUTER JOIN )**

ANSI 구문의 경우 조건

1.  ON에서도 사용할 수 있고

1. Where절에도 추가할 수 있는데

**주의할 점**

“어디에 조건을 사용하느냐에 따라 결과집합이 다르게 나옴 “

  
**예시를 살펴보면**


 ``` 
-- 1번) ON 절
select *
from dept d left outer join emp e
	on e.deptno = d.deptno
	and d.dname IN ('ACCOUNTING','OPERATION');
	
-- 2번) WHERE 절
select *
from dept d left outer join emp e
	on e.deptno = d.deptno
where d.dname IN ('ACCOUNTING','OPERATION');
 ``` 


  
**1번 결과**

![4359fb1f-b6fb-49ce-bc67-d38f34f587ab](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/0e4e2aef-71a8-46c3-92b6-1abd299b8b3a/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193955Z&X-Amz-Expires=3600&X-Amz-Signature=22cd04eae962f21f3b9eec7db4252b0103de9e2d693e30b51894cf1a8f232d43&X-Amz-SignedHeaders=host&x-id=GetObject)
dname이 accounting, operation 이 아닌 결과도 포함해서 나온다. 

단 emp테이블 값은 Null로 채워진다. (실제 값에는 emp 값이 있는 것도 있음)

  
**2번 결과**

![7b456499-9170-4384-b4ee-9a1bcbdb9691](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/66f2705e-3b4e-44e3-a96d-402767f59416/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193955Z&X-Amz-Expires=3600&X-Amz-Signature=8847202e5755fb89889da6791c22c1f91f3cf18d9534f75cb832a416cebad77f&X-Amz-SignedHeaders=host&x-id=GetObject)
dname이 accounting, operation 인 것은 제외하고 나온다.

  
결과를 보면 조건절을 On 또는 Where 어디에 넣느냐에 따라 결과집합이 달라짐을 확인할 수 있다.

  
**실행계획을 천천히 살펴보면**

(1번 2번 조인 방식을 동일하게 놓고 비교하기 위해 힌트를 주고 실행했다.)

**1번 실행계획**


 ``` 
------------------------------------------------------------------------------------------------------
| Id  | Operation                            | Name          | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                     |               |    10 |   580 |     6   (0)| 00:00:01 |
|   1 |  NESTED LOOPS OUTER                  |               |    10 |   580 |     6   (0)| 00:00:01 |
|   2 |   TABLE ACCESS FULL                  | DEPT          |     4 |    80 |     3   (0)| 00:00:01 |
|   3 |   TABLE ACCESS BY INDEX ROWID BATCHED| EMP           |     2 |    76 |     1   (0)| 00:00:01 |
|*  4 |    INDEX RANGE SCAN                  | EMP_DEPTNO_IX |     2 |       |     0   (0)| 00:00:01 |
------------------------------------------------------------------------------------------------------
 
Predicate Information (identified by operation id):
---------------------------------------------------
 
   4 - access("E"."DEPTNO"(+)="D"."DEPTNO")
       filter("D"."DNAME"=CASE  WHEN ("E"."DEPTNO"(+) IS NOT NULL) THEN 'ACCOUNTING' ELSE 
              'ACCOUNTING' END  OR "D"."DNAME"=CASE  WHEN ("E"."DEPTNO"(+) IS NOT NULL) THEN 'OPERATION' 
              ELSE 'OPERATION' END )
 ``` 



 ``` 
"D"."DNAME"=CASE  WHEN ("E"."DEPTNO"(+) IS NOT NULL) THEN 'ACCOUNTING' 
									ELSE 'ACCOUNTING' END  
OR 
"D"."DNAME"=CASE  WHEN ("E"."DEPTNO"(+) IS NOT NULL) THEN 'OPERATION' 
				          ELSE 'OPERATION' END
 ``` 


이 문장의 결과는 DEPTNO가 null 이 아니면 accounting, operation로 표현되는 것으로 필터링의 의미가 없는 구문이다.

  
**2번 실행계획**


 ``` 
-------------------------------------------------------------------------------------------------------
| Id  | Operation                             | Name          | Rows  | Bytes | Cost (%CPU)| Time     |
-------------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                      |               |     9 |   522 |     4   (0)| 00:00:01 |
|   1 |  NESTED LOOPS OUTER                   |               |     9 |   522 |     4   (0)| 00:00:01 |
|   2 |   INLIST ITERATOR                     |               |       |       |            |          |
|   3 |    TABLE ACCESS BY INDEX ROWID BATCHED| DEPT          |     2 |    40 |     2   (0)| 00:00:01 |
|*  4 |     INDEX RANGE SCAN                  | DEPT_DNAME_IX |     2 |       |     1   (0)| 00:00:01 |
|   5 |   TABLE ACCESS BY INDEX ROWID BATCHED | EMP           |     5 |   190 |     1   (0)| 00:00:01 |
|*  6 |    INDEX RANGE SCAN                   | EMP_DEPTNO_IX |     5 |       |     0   (0)| 00:00:01 |
-------------------------------------------------------------------------------------------------------
 
Predicate Information (identified by operation id):
---------------------------------------------------
 
   4 - access("D"."DNAME"='ACCOUNTING' OR "D"."DNAME"='OPERATION')
   6 - access("E"."DEPTNO"(+)="D"."DEPTNO")
 ``` 


테이블 엑세스 시 Accounting과 Operation만 가져오고 있다.

  
  
**둘의 가장 큰 차이점**

1. 1번(ON)은 검색 조건이 필터링 단계에서 수행되었고

&ensp; &ensp; - 데이터는 가져왔고 조건에 해당되지 않아도 남겨둔 상태로 조인을 수행한 것으로 유추할 수 있음

1. 2번(Where)은 인덱스 엑세스 단계(DEPT_DNAME_IX)에서 수행되었다.

&ensp; &ensp; - 즉, DEPT 테이블을 읽을 때, 조건에 해당하는 값만 가져옴

  
### 결론 정리

- ON 절에 조건을 넣으면 : (left의 경우) Right쪽 테이블이 NULL로 채워진 결과 집합 반환

&ensp; &ensp; - ON절 : 오른쪽 테이블 조건 필터

&ensp; &ensp; - WHERE절 : 왼쪽 테이블 조건 필터

&ensp; &ensp; - 경우에 따라서는 일부러 선택적 조인을 해야되는 경우가 있어 NULL로 채워진 값을 활용하기도 한다.

- where절에 조건을 넣으면 : 결과가 필터링되어 나타나지 않음

  
## Oracle 구문 주의

위에 봤던 내용은 ANSI기준이고 Oracle에서의 사용법이 다르다.

  
(+)기호를 Join이 아닌 조회조건에서도 사용해야되는 경우가 있다.

  
### **문제) 연봉 3000이 넘는 사원이 있는 부서 찾기
(단, 사원이 없어도 부서명은 출력)**

outer조인으로 사원이 없는 부서도 출력할 수 있다.


 ``` 
select d.deptno as dept_deptno, d.dname, e.deptno as emp_deptno, e.empno, e.sal
from dept d, emp e
where e.deptno(+) = d.deptno
and e.sal >= 3000;
 ``` 


![c387b67e-10a9-4576-94dc-ee1f4fa1a377](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/bfd77d93-6b64-40ea-9919-a1689ddac514/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193955Z&X-Amz-Expires=3600&X-Amz-Signature=2da6c0a4ee9f54d1a05463253e52d74a8371ed306f7065b1936d5d0a11f5688f&X-Amz-SignedHeaders=host&x-id=GetObject)
dept와 emp테이블을 조인할 때 dept기준으로 outer조인을 수행했다.

그런데 원하는 집합이 나오지 않는다. 부서번호 30,40인 데이터는 출력되지 않았다.

  
**이유**

1. outer 조인 수행

1. sal ≥3000 조건 필터 ⇒ sal에 NULL이 들어간 로우는 모두 필터링됨

  
**해결방법**

조회 조건에도 (+) 연산자를 추가해주기


 ``` 
-- 사원이 없거나, 연봉이 3000이 넘는 사원이 없는 부서 출력
select d.deptno as dept_deptno, d.dname, e.deptno as emp_deptno, e.empno, e.sal
from dept d, emp e
where e.deptno(+) = d.deptno
and e.sal(+) >= 3000;
 ``` 


이렇게 추가해주면 아래로 순서가 반대로 된다고 이해해도 된다.

1. SAL 조건 필터 수행

1. Outer 조인 수행

  
>두 가지를 실행계획을 비교해보면 실제로 순서가 달라지진 않고,
위 쿼리에는 실행계획에 OUTER가 나타나지 않는다. 그냥 이해를 이렇게 하라는 의미

  
### 정리

- outer 조인에 참여 시킨 테이블이 있고, 그 테이블에 조회 조건을 또 걸어야 된다면, 해당 조건(e.sal(+))에도** ‘+’ 를 추가해줘야 한다.**

- 위 내용이 헷갈리면 인라인 뷰를 사용해서 직관적이게 표현해주는게 좋다.

  
# 응용 적용

## 1. 조건에 맞을 때만 조인하도록

아래에는 CASE문을 썼지만, Decode 등 다른 함수도 가능하다.


 ``` 
-- 일할계산여부가 Y가 아닐 때만 조인
and B.할부계획ID(+) = ( case when A.일할계산여부='Y'
														then NULL
														else A.할부계획ID end)
 ``` 


1. 일할계산여부가 Y가 아니면 NULL로 계산된 테이블이 드라이빙 됨

1. outer조인을 걸어둬서 NULL로 변환된 것에는 B테이블 값이 NULL로 들어간 결과가 나옴

  
## 2. 3개 테이블을 조인하기

[로직 설명]

- TACCOUNT  ID_TYP = 1 이면 TPID와 조인

- TACCOUNT  ID_TYP = 2 이면 TCID와 조인


 ``` 
-- Oracle 
select ta.lnid,ta.ID_TYP, p.score, c.grade 
from taccount ta, tpid p, tcid c
where p.lnid(+) = (case when ta.ID_TYP=1 then ta.lnid end)
and c.lnid(+) = (case when ta.ID_TYP=2 then ta.lnid end)
                        
-- ANSI
select ta.lnid,ta.ID_TYP, tp.score, tc.grade
from taccount ta
left outer join tpid tp
	on ta.lnid = tp.lnid
	and ta.id_typ='1'
left outer join tcid tc
	on ta.lnid = tc.lnid
	and ta.id_typ='2';
 ``` 


  
  
_______
논외로 cross join - 두 집합의 가능한 모든 경우의 수 출력


 ``` 
--oracle
select * from emp, dept;

--ansi
select * from emp cross join dept;
 ``` 


_______
## Partition Outer Join

Q. 지점, 날짜에 대한 값이 없어도 행으로 표현하도록


 ``` 
 SELECT b.branch, a.yymm, NVL(b.cnt,0) AS cnt 
  FROM (SELECT TO_CHAR(ADD_MONTHS(TO_DATE('2021/01/01','YYYY/MM/DD')
                                 ,LEVEL-1)
                       ,'YYYY/MM') AS YYMM
          FROM dual 
         CONNECT BY LEVEL <= 12) a 
LEFT OUTER JOIN    
      (SELECT branch, TO_CHAR(ln_dt,'YYYY/MM') AS yymm, COUNT(*) AS cnt 
          FROM tacct 
         WHERE ln_dt BETWEEN TO_DATE('2021/01/01','YYYY/MM/DD')
                         AND TO_DATE('2022/01/01','YYYY/MM/DD') - 1/86400
           AND lmt_typ IS NULL 
        GROUP BY branch, TO_CHAR(ln_dt,'YYYY/MM')) b  
**PARTITION BY (b.branch)**
   ON a.yymm = b.yymm 
ORDER BY b.branch, a.yymm ;

 ``` 


연/월 - 갯수

2개 컬럼으로 묶여있는 결과를 Partition by 로 다시 그룹핑해준다.

&ensp; &ensp; - 이 구문을 안쓰면 dual로 연월일 만들듯이 다시 dummy데이터를 만들어서 조인해줘야 함

![1e3542bd-5c0b-4e90-bccf-d20bf20ef505](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/10abb3ef-7a86-4b1b-8563-eae23299658d/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193957Z&X-Amz-Expires=3600&X-Amz-Signature=174de557c10595890bb826cef0a7c997ff5fa53f4e60daab68548826015fc5d1&X-Amz-SignedHeaders=host&x-id=GetObject)