
_______
  
# ROLLUP

소계 및 합계를 계산하며 우측 끝 컬럼부터 연산에서 제외되므로 컬럼 순서가 중요하다.


 ``` 
select deptno, job, sum(sal) as sum_sal
from emp
group by rollup(deptno,job)
order by 1,2;
 ``` 


![9fc49d14-a795-4901-87f4-d44417c2cb7c](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/460aea32-d59d-4a37-a045-01d2c69bd1a1/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193954Z&X-Amz-Expires=3600&X-Amz-Signature=2f7b7fd2365d9df8d902e8667017f5bd5c5d7aa0676637fd325a03f1e4cb0660&X-Amz-SignedHeaders=host&x-id=GetObject)
결과는 3종류가 나온다

1. (Deptno, Job)

1. (Deptno)

1. ()

  
# Cube

모든 경우의 수 그룹을 만들어 낸다.(ROLLUP과 차이)


 ``` 
select deptno, job, sum(sal) as sum_sal
from emp
group by cube(deptno,job)
order by 1,2;
 ``` 


![33580f67-ed79-4247-bbec-a35a55093ff5](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/479995ea-2562-433c-bd20-f12d5329bd4b/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193954Z&X-Amz-Expires=3600&X-Amz-Signature=f59c5c91effbbe0f40f0687aaadfdb4bd372db6a9f1672683564d1e78a5d8e03&X-Amz-SignedHeaders=host&x-id=GetObject)
1. (Deptno, Job)

1. (Deptno)

1. (Job)

1. ()

  
### 더 다양한 그룹 조건 만들기

Group By절에는 여러 조합이 들어갈 수 있고

괄호로 묶느냐 아니냐에 따라 그룹의 단위가 달라진다.

  
이를 활용하면 더 다양하게 원하는 그룹을 만들어낼 수 있다.

**() 사용하기**


 ``` 
SELECT EMPNO, ENAME, DEPTNO, SUM(SAL)
  FROM EMP 
 GROUP BY ROLLUP((EMPNO, ENAME, DEPTNO));
 ``` 


1. (EMPNO, ENAME, DEPTNO)

1. ()


 ``` 
SELECT DEPTNO, EMPNO, ENAME, SUM(SAL)
  FROM EMP 
 GROUP BY DEPTNO, ROLLUP((EMPNO, ENAME));
 ``` 


1. (DEPTNO, EMPNO, ENAME)

1. (DEPTNO)

**ROLLUP + CUBE**


 ``` 
GROUP BY ROOLUP(A,B), CUBE(C,D)
 ``` 


1. (A,B,C,D)

1. (A,B,C)

1. (A,B,D)

1. (A,B)

1. (A,C,D)

1. (A,C)

1. (A,D)

1. (C,D)

  
  
조합은 이렇게 만들 수 있는데, 이 조합을 추출해서 활용하는 방법은 함수를 사용하면 된다.

  
### 생각하기

기본 키(EMPNO)를 그룹핑 단위에 사용하면 해당 그룹에는 데이터가 1개 밖에 없기 때문에 집계 함수를 사용해도 그 값이 그대로 나오게 된다.

`rollup(EMPNO, EMPNAME)`을 쓰게 되면

- 조합은 (EMPNO,EMPNAME) , (EMPNO), ()

-  (EMPNO,EMPNAME) , (EMPNO) 이 두 개는 결과가 동일하다. 어차피 EMPNO가 기본 키기 때문에 그룹 내 데이터가 1개 밖에 없기 때문이다.

- 이럴 땐 괄호를 한번 더 감싸서 사용하는 게 의미가 있을 것이다.

# GROUPING SETS

원하는 조합을 지정해서 결과 추출

- ROLLUP, CUBE에 많은 컬럼을 넣게 되면 결과가 너무 많이 나와 내가 원하는 그룹만 보기가 어려우니 필요한 조합 지정


 ``` 
select deptno, job,MGR, sum(sal) as sum_sal
from emp
group by grouping sets((deptno,job), (DEPTNO,MGR));
 ``` 


![3ad4a501-50ae-41d2-a450-d690cb75252b](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/4a29409c-0796-4e22-bdc9-903b0c0512ea/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193954Z&X-Amz-Expires=3600&X-Amz-Signature=de9482d37807180b312413be56ca1da1bf531fb5e65a2150e189065202becb27&X-Amz-SignedHeaders=host&x-id=GetObject)
  
### 성능

GROUPING SET은 기본 쿼리 집합을 한 번 액세스해서 임시 테이블을 생성하기 때문에 경우에 따라 과도한 디스크 I/O가 발생할 수 있다.

힌트로 작성된 쿼리를 Union으로 수행하도록 유도할 수 있다


 ``` 
/*+ EXPAND_GSET_TO_UNION */ -- 쿼리가 Union all로 수행하도록 유도
 ``` 


  
### NULL 처리

- 컬럼이 그룹 생성에 참여를 했는지 여부를 (NULL)로 확인할 수 있을까?

- 데이터에 NULL 값이 있을 때의 값과 그룹에 포함되었는지 확인할 수 있을까?

결론부터 말하면 `GROUPING` 함수를 사용하면 된다.

![1f31a84a-a856-463d-8067-a0f3eff12b98](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/07e16147-d180-462f-9417-6472883c7ac8/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193954Z&X-Amz-Expires=3600&X-Amz-Signature=40531d2f5b4b1942a0927a2e82ac36099b95047c827af2abe188a0285607ab67&X-Amz-SignedHeaders=host&x-id=GetObject)
결과를 확인해보면 NULL, NULL, NULL 인 그룹이 2개인데, SUM(SAL)의 값이 다르게 나오는 것을 볼 수 있다.

→ MGR에 실제로 NULL이라는 값이 있기 때문에 중복되서 보이는 것이고 이걸로 봐선 구분되지 않는다.

  
이럴 땐 GROUPING이라는 함수를 사용해서 해결할 수 있다.

# GROUPING

컬럼이 그룹 생성에 포함되었는지 여부를 이진수로 표현해준다.

- 0 : 컬럼이 그룹 생성에 포함됨

- 1 : 컬럼이 그룹 생성에 포함 X

  
Grouping 함수 + Having 절을 사용하면 필요한 조합만 추출해낼 수 있다.


 ``` 
SELECT DEPTNO, JOB, MGR, SUM(SAL) 
      ,GROUPING(DEPTNO), GROUPING(JOB), GROUPING(MGR)
  FROM EMP 
 GROUP BY CUBE(DEPTNO, JOB, MGR) 
 HAVING GROUPING(DEPTNO) = 0 
   AND GROUPING(JOB)   = 0 
   AND GROUPING(MGR) =  1 ; 
 ``` 


# GROUPING_ID

GROUPING 의 조건식을 하나씩 나열하기 복잡하면 좀 더 간단하게 조건식을 세울 수 있다.

Group에 대한 ID값을 부여해주고, 그 ID값을 찾아내는 것으로

순서에 따라서 각각의 그룹이 참여 여부를 숫자로 표현준다.


 ``` 
GROUPING_ID(DEPTNO, JOB, MGR) => (0 0 1) -> 1
 ``` 


  
참여 여부가 2진수로 표현된 것을 → 10진수로 표현해서 확인 가능

그러면 Grouping 만 사용했을 때보다 결과를 쉽게 뽑아낼 수 있다.

  

 ``` 
GROUP BY CUBE(DEPTNO, JOB, MGR) 
HAVING GROUPING_ID(DEPTNO,JOB,MGR) IN (1,2) ;
 ``` 


  
# 응용

**급여의 합계와 평균을 한번에 표현**


 ``` 
SELECT CASE GROUPING('A') WHEN 0 THEN SUM(SAL) ELSE AVG(SAL) END 
  FROM EMP 
 GROUP BY ROLLUP('A') ; 
 ``` 


![503746a6-1c60-4054-8655-b274aeb9491f](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/c929ae68-caa4-4c2e-a452-1ec347caa6d3/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193954Z&X-Amz-Expires=3600&X-Amz-Signature=b7f3d04b86bbd916eb36e506f5403e62c75168997db02fd8ca05e8d2259a0992&X-Amz-SignedHeaders=host&x-id=GetObject)

 ``` 
select sum(sal), avg(sal)
from emp;
 ``` 


AVG, SUM을 사용하면 컬럼으로 나오는데 이렇게 하면 행으로 분리되서 표현이 가능하다.

  
위 방법 말고도 하나의 행을 2개의 행으로 분리하는 방법이 있는데


 ``` 
select CASE NO WHEN 1 THEN SUM_SAL ELSE AVG_SAL END 
from (select sum(sal) as sum_sal, avg(sal) as avg_sal
				from emp) A
			,(select ROWNUM as no
				from dual
				connect by level <= 2) B
 ``` 


Cross Join을 통해서 원하는 수만큼 행을 불려 놓고

Case문을 사용해서 필요한 값만 뽑아내는 프로세스이다.

  
**다음 조건에 만족하는 행 검색**

- 사원 정보에서 평균,합계 급여를 행 단위로 표현

**상수를 잘 활용해서 원하는 그룹 조합을 만들어내고**

**CASE, DECODE 문 등을 이용해서 필요한 집계 함수를 사용하는 것이 방법이다.**

위에서 Cross Join으로 행을 불려 놓는 원리처럼 상수 값으로 그룹 조합을 불려 놓고 필요한 것을 꺼내 쓰는 것이다.


 ``` 
select deptno,empno,
        decode(grouping_id(1,deptno,2,empno), 1, 'DEPT_SUM', 3,'DEPT_AVG',
                                              7, 'TOTAL_SUM', 15,'TOTAL_AVG'
                                                  , ename) AS ename,
        decode(grouping_id(1,deptno,2,empno), 1, sum(sal), 3, round(avg(sal),1),
                                              7, sum(sal), 15,round(avg(sal),1),
                                                 sum(sal)) AS SAL                                       
from emp
group by rollup(1,deptno,2,(empno,ename));
 ``` 


![a906c10a-d6e6-4305-b1a8-aef1e41ac292](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/22af4a6a-899f-4e07-8c94-44b36d826673/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193954Z&X-Amz-Expires=3600&X-Amz-Signature=c552b35157bfd6bb53bc1e7e3ac205059a7945962542cd03cb971eb6a11b0442&X-Amz-SignedHeaders=host&x-id=GetObject)
  
그룹 조합

1. 1,deptno,2,(empno,ename)

1. 1,deptno,2

1. 1,deptno

1. 1

1. ()

  
여기서 2,3번의 조합 결과는 동일하다. (상수 2만 빼고)

마찬가지로4,5번의 조합 결과도 동일하다.


 ``` 
(1 ,deptno , 2)
(1,10,2)
(1,10,2)
(1,10,2)
(1,20,2)
(1,20,2)
(1,20,2)
...

(1, deptno)
(1,10)
(1,10)
(1,10)
(1,20)
(1,20)
(1,20)
...
 ``` 


  
grouping_id 값을 한번 확인해보면

![453a04a4-edc1-4df3-bcd7-8d9cb1c4834b](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/1a73a3cb-5a6d-40fd-9c7b-912b9eda38a9/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193954Z&X-Amz-Expires=3600&X-Amz-Signature=759aa7262144770f814b3b580cdb1be73152bed25144d3ad92190a7c0997bf18&X-Amz-SignedHeaders=host&x-id=GetObject)
(1,deptno,2,empno) 

- 0,0,0,0 ⇒ 0

- 0,0,0,1 ⇒ 1

- 0,0,1,1 ⇒ 3

- 0,1,1,1 ⇒ 7

- 1,1,1,1 ⇒ 15

  
이 값을 활용해서 집계를 구하면 된다.

- ID 1과 3 : dept 집계

- ID 7과 15 : 전체 집계

  
_______
# 행을 컬럼(세로 → 가로) 변환하기

[문제] 부서별 JOB들의 급여 평균 찾기

![17104319-d496-4e11-b137-2cbddbf35ac8](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/c9b14145-8d90-4807-948d-4cf8b298ad88/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193954Z&X-Amz-Expires=3600&X-Amz-Signature=61eb3e8850767b56e8b49e3b9f8cc7f3b747d4ee40b54f9f958443a1c51f0981&X-Amz-SignedHeaders=host&x-id=GetObject)
### 방법1) SUM(CASE()) / SUM(DECODE())


 ``` 
-- SUM(CASE())
SELECT deptno, SUM(CASE job WHEN 'ANALYST'   THEN sal END)  AS analyst, 
               SUM(CASE job WHEN 'CLERK'     THEN sal END)  AS clerk, 
               SUM(CASE job WHEN 'MANAGER'   THEN sal END)  AS manager,
               SUM(CASE job WHEN 'PRESIDENT' THEN sal END)  AS president, 
               SUM(CASE job WHEN 'SALESMAN'  THEN sal END)  AS salesman
 FROM emp 
 GROUP BY deptno 
 ORDER BY deptno ;
 
 -- SUM(DECODE())
 SELECT deptno, SUM(DECODE(job,'ANALYST' ,sal))  AS analyst, 
               SUM(DECODE(job, 'CLERK'   ,sal))  AS clerk, 
               SUM(DECODE(job, 'MANAGER' ,sal))  AS manager,
               SUM(DECODE(job,'PRESIDENT',sal))  AS president, 
               SUM(DECODE(job,'SALESMAN' ,sal))  AS salesman
 FROM emp 
 GROUP BY deptno 
 ORDER BY deptno ;
 ``` 


- 행 : Group By절

- 열 : Select 에 SUM(CASE()), SUM(DECODE(()) 사용

&ensp; &ensp; - 필요한 열들을 모두 선언해줘야 한다

&ensp; &ensp; - 어디에 어떤 값을 넣을지 미리 통을 만들어주는 것임

  
EMP에 1억 개의 행이 있으면

1. DEPTNO 별로 Group by를 하지만

1. JOB은 Group 되어 있지 않아, 1억개 * 6개의 Case문을 반복 수행하게 된다

  
⇒ Inline View를 이용해서 튜닝 수행이 가능함

### 방법2) Inline View

그룹화 결과를 미리 생성해두면 CASE문도 그룹의 갯수 만큼만 수행할 수 있다.


 ``` 
SELECT deptno, SUM(DECODE(job,'ANALYST' ,sum_sal))  AS analyst, 
               SUM(DECODE(job, 'CLERK'   ,sum_sal))  AS clerk, 
               SUM(DECODE(job, 'MANAGER' ,sum_sal))  AS manager,
               SUM(DECODE(job,'PRESIDENT',sum_sal))  AS president, 
               SUM(DECODE(job,'SALESMAN' ,sum_sal))  AS salesman
 FROM ( select deptno, job, sum(sal) as sum_sal
        from emp
        group by deptno, job)
 group by deptno
 ORDER BY deptno ;
 ``` 


  
### 방법3) Pivot

Oracle 11g 부터 PIVOT문을 지원해주고 ANSI표준이다


 ``` 
select *
from (select deptno,job,sal
        from emp)
pivot(sum(sal) for job in ('ANALYST' AS analyst,
                            'CLERK' AS clerk,
                            'MANAGER' AS manager,
                            'PRESIDENT' AS president,
                            'SALESMAN' AS salesman))
order by deptno;
 ``` 


- AS 뒤에 있는 명이 Column Name으로 들어간다 ⇒ 같은 값이 들어가면 안됨

문장을 잘 보면 deptno를 pivot안에서 명시되어 사용되지 않는다.

  
**그렇다면 그룹핑의 기준을 어떻게 알아내는 걸까?**

select절에 있는 컬럼 중 어디에도 사용되지 않은 컬럼을 묵시적으로 Group 기준으로 삼는다

  
  
  
  
_______
  
여태는 이런 그룹, 집계 함수가 익숙하지 않아 DB에서 통계 보고서 작성할 때 Splunk dbconnect를 이용해서 자료를 뽑아내고 거기서 stats, chart를 이용해서 원하는 형태로 뽑아냈었다.

Splunk가 더 익숙해진 것이다.. 이제는 배웠으니 Splunk 영역을 좀 줄이고 SQL로 짜보면서 좀 익숙하게 사용해봐야겠다.

  
  