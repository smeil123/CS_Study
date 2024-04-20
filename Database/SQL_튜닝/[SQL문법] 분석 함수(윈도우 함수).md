

_______
  
오라클에서 8i버전부터 지원하고 있음

  
이 함수들은 분석 작업에 유용하기 때문에 Analytic Functions이라고 한다

  
분석 함수는 행 그룹을 기반으로 집계 값을 계산한다.

- Group by 절 없이도 select 때 집계 값을 계산할 수 있다.

  
분석 함수는 Aggregate Function뒤에 Analytic Clause(Over 절)을 통해 행 그룹을 정의하고 각 그룹당 결과 값을 반복하여 출력한다.

Over절에는 partition clause, order by clause, windowing clause 이 포함될 수 있다.

이러한 분석 함수는 Join 문장, where, group by, having등과 함께 쓰일 때 가장 마지막에 연산(집계)를 진행하며 select 절과 order by절에서만 사용 가능하다.

  
## 분석함수를 이용해야되는 이유

아래의 함수를 몰라도, max() 등의 집계함수, 인라인뷰의 조합으로 원하는 값을 다 뽑아낼 순 있다.

하지만 문제는 그런 방식은 같은 테이블을 여러번 읽어야되는 성능상의 이슈가 있다.

성능을 위해서도 지원해주는 문장을 사용하는게 좋다

### 예시

**MAX만 사용 시**


 ``` 
-- 쿼리 일부 추출
SELECT lnid, prod_cd, ln_amt 
FROM tacct a
WHERE lmt_typ IS NULL
AND ln_amt = (SELECT MAX(ln_amt)
							FROM tacct 
              WHERE prod_cd = a.prod_cd)
 ``` 


lm_amt 가 가장 큰 값을 뽑으려면 MAT값을 뽑을 때 테이블 스캔 1회

그 큰값에 대한 다른 컬럼을 찾기 위해 테이블 스캔 1회

이렇게 테이블을 두 번 읽어야한.

  
**분석 함수를 사용 시**


 ``` 
select lnid,prod_cd,ln_amt
from ( select lnid,prod_cd,ln_amt,
		           rank() over(partition by prod_cd order by ln_amt desc) as amt_rank
        from tacct
        where LMT_TYP is null)
where amt_rank=1
 ``` 


테이블 스캔은 한번만 해도 된다.

# Partition clause

>partition by

하나 이상의 컬럼(표현식)을 기반하여 행들을 그룹화한다.

group by와 비슷하지만, 그룹단위가 아니라 행 단위로 결과를 출력해준다.


 ``` 
select empno, ename, sal, deptno
      ,sum(sal) over()                    as sum_overall
      ,sum(sal) over(**partition by** deptno) as sum_deptno
from emp;
 ``` 


![28faab15-755b-4c36-921d-00d74601ba41](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/8f0a1cc2-314d-4902-bb47-62f777e58e5c/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193958Z&X-Amz-Expires=3600&X-Amz-Signature=31bd0412505528874ff26be6f7235b809b8a9d34fb821edbeea3b1d122a0d1ad&X-Amz-SignedHeaders=host&x-id=GetObject)
  
# Order by clause

>partition by + order by

파티션 내에서 정렬 방식을 지정할 때 사용된다.

지정된 순서에 따라 누적 집계된 값이 표현된다.

반드시 Order by 절을 포함해야지 결과를 만들 수 있다.


 ``` 
select empno, ename, sal, deptno
      ,rank() over(partition by deptno order by sal desc) as rank
      ,dense_rank() over(partition by deptno order by sal desc) as drank
      ,row_number() over(partition by deptno order by sal desc) as rnum
from emp;
 ``` 


![d422e3f5-b262-425b-b616-3ac92b9b00fa](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/345eb46d-4498-473c-b43a-3f02a66a09aa/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193958Z&X-Amz-Expires=3600&X-Amz-Signature=a233a2debd4b0455282516a718f02993b5f3cb8f41305e2703a9c4cfd5ce37c6&X-Amz-SignedHeaders=host&x-id=GetObject)
  
여기서 범위를 지정해서 원하는 조건에 맞는 값들만 집계할 수도 있다.

  
# Windowing clause

>order by + ROWS | RANGE

Function 이 적용될 Window(범위)를 정의해서 누적 집계를 만들 수 있다.

>예를 들어, 특정일자 전 후 1년 간의 월급을 구하기 가능

- ROWS : 물리적 범위 지정

- RANGE : 논리적 범위 지정

&ensp; &ensp; - 위 예시를 찾으려면 RANGE를 사용하면 된다.

행 순서를 보정하기 위해 order by 절 사용은 필수이며 계산한 행의 범위를 지정한다.

정렬된 상태에서 원하는 행 개수를 이용하여 계산 범위를 지정할 수 있다.

필요하다면 첫 번째, 마지막, 현재 행을 활용할 수 있다.

- UNBOUNDED PRECEDING : 첫 번째 행

- UNBOUNDED FOLLOWING : 마지막 행

- CURRENT ROW : 현재 행

**ROWS**


 ``` 
select empno, ename, sal, deptno
      ,sum(sal) over(order by empno) as sum1
      ,sum(sal) over(order by empno rows unbounded preceding) as sum2
      ,sum(sal) over(order by empno rows between unbounded preceding
                                            and current row) as sum3
      ,sum(sal) over(order by empno rows between current row
                                            and unbounded following) as sum4
      ,sum(sal) over(order by empno rows between 1 preceding
                                            and 1 following) as sum5
from emp;
 ``` 


1. order by 절은 필수

1. ROWS 키워드를 통해 물리적 범위를 사용하겠다 선언

1. 적절한 조건으로 구체적인 범위를 명시

  
구문을 하나씩 설명해보면

- sum1 = sum2 = sum3 결과가 동일하다

&ensp; &ensp; - empno으로 정렬

&ensp; &ensp; - 첫번째 행 ~ 현재 행까지 합계

- sum4

&ensp; &ensp; - 마찬가지로 empno으로 정렬

&ensp; &ensp; - 현재 행 ~ 마지막 행까지 합계

- sum5

&ensp; &ensp; - empno 정렬

&ensp; &ensp; - 앞 1개 ~ 뒤1개까지 합계

![afdb2100-a5da-47e5-a12c-aa7b6c7e9da1](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/fb0dff63-6d2d-4d4e-b7de-91a85d39a196/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193958Z&X-Amz-Expires=3600&X-Amz-Signature=d0d24c24db4c68b5ede0d19c4bd8d37869098ca1cbab998a6660f7bce2df84d9&X-Amz-SignedHeaders=host&x-id=GetObject)
  
**RANGE**


 ``` 
select empno, ename, mgr, sal
    , hiredate - numtoyminterval(1,'YEAR') as "1 years ago"
    , hiredate
    , hiredate + numtoyminterval(1,'YEAR') as "1 years ago"
    , sum(sal) over(order by hiredate range numtoyminterval(1,'YEAR') preceding) as sum1
    , sum(sal) over(order by hiredate range between numtoyminterval(1,'YEAR') preceding
                                                and numtoyminterval(1,'YEAR') following ) as sum2
from emp;
 ``` 


위와 구조는 동일하고, 키워드만 RANGE로 변경되었다.

집계의 범위를 Range뒤에 오는 논리적인 연산으로 지정할 수 있는 것이다.

  
- sum1 : 입사일자 - 1년 간의 합계

- sum2 : 입사일자 -1년 ~ +1년 간의 합계

![94443513-8ea1-420d-9a8d-a05c12a7b46b](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/2166c433-e896-49a2-bcda-8b22a1260a60/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193958Z&X-Amz-Expires=3600&X-Amz-Signature=06dd38f9ac0105cb1f27026965a8570c3cdb92c0fc4e307007288883e80f861a&X-Amz-SignedHeaders=host&x-id=GetObject)
  
  
_______
# 함께 사용할 수 있는 함수

## KEEP 집계 함수 - 최초값|최종값


 ``` 
MAX() KEEP(**DENSE_RANK **[FIRST|LAST] ORDER BY)
MIN() KEEP(**DENSE_RANK** [FIRST|LAST] ORDER BY)

MAX(grade) KEEP(DENSE_RANK LAST ORDER BY RK) AS grade
-- RK를 기준으로 정렬 후 마지막 Grade 컬럼 검
 ``` 


## Lag, Lead

현재 행보다 위에 있는 값, 아래에 있는 값 찾아주는 함수


 ``` 
-- 현재 사원보다 먼저 입사한 사원, 나중에 입사한 사원 이름 검색
select empno, ename, hiredate
     , lag(ename) over(order by hiredate) as prev_ename
     , lead(ename) over(order by hiredate) as next_ename
from emp
order by hiredate, empno
 ``` 


  
바로 위아래가 아닌 지정된 개수 이전, 이후의 행을 가져올 수도 있음


 ``` 
LAG(sal,2,0) over (order by ename) prev_sal,
LEAD(sal,2,0) over (order by ename) next_sal
 ``` 


  
Q. 구매 기간의 텀의 평균 내기


 ``` 
SELECT AVG(C1)
  FROM (SELECT TIME_ID - LAG(TIME_ID) OVER(ORDER BY TIME_ID) AS C1 
          FROM (SELECT DISTINCT TIME_ID  
                  FROM SALES 
                 WHERE CUST_ID = 987 
                   AND TIME_ID BETWEEN TO_DATE('1998/02/01','YYYY/MM/DD')
                                   AND TO_DATE('1998/03/01','YYYY/MM/DD') - 1/86400
                 ORDER BY TIME_ID ) 
        );
-- 결과는 상수로 나옴
 ``` 


그런데 이렇게 복잡하게 작성할 필요가 없다

평균 일수만 구하면 되기 때문에

- (마지막 날짜 - 최초 날짜) / (유니크한 구매 일수 -1)


 ``` 
select (max(time_id) - min(time_id)) / (count(distinct time_id)-1)
 ``` 


## LISTAGG

행 연결해서 한 라인으로 표현하기


 ``` 
-- v11gR2
select deptno
      ,LISTAGG(ename, ',') within group (order by ename) as employee
from emp
group by deptno

-- 12c
-- 너무 길어지면 에러가 났는데 이를 생략해서 표현 가능
select deptno
			,LISTAGG(ename,',' on overflow truncate '...' with count) 
			within group (order by ename) as employee
from emp
group by deptno
 ``` 


![b16722cc-5da5-4e46-bb93-b7e347da01c1](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/2f431bc7-3412-4dc9-a4ec-e43f50eee314/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193959Z&X-Amz-Expires=3600&X-Amz-Signature=9388b5bb972514a99226040d14f9faf678377e4a976d3d2b9570b5e709a110bd&X-Amz-SignedHeaders=host&x-id=GetObject)
over절이 없음 ⇒ 분석 함수가 아닌 집계 함수!

그래서 group by 절이 필요한 것이다.

order by 순서대로 행이 연결된다.

  
여기에 엑셀처럼 concat도 가능함


 ``` 
select d.dname, LISTAGG(e.ename || '('||e.sal||')',',') within group (order by ename) as employee
from emp e, dept d
where e.deptno = d.deptno
group by d.dname;
 ``` 


![96f7ad30-847e-4377-b0cf-ba60efb0ab53](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/84c92a31-3595-43cd-a82e-fc0e7e6f98c4/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T193959Z&X-Amz-Expires=3600&X-Amz-Signature=2ceb36071e21b023fcb0a86037dc6305f09d1d84e5b894b014dca65143301bbe&X-Amz-SignedHeaders=host&x-id=GetObject)
  
## ratio_to_report

백분율 계산하기

  
이 함수는 WINDOW영역의 합계에서 현재 값이 차지하는 백분율을 계산해준다.


 ``` 
-- 부서별 누적된 급여, 부서별 급여의 백분율, 전체 사원의 급여 합계에서의 백분율 검색
select deptno, ename, sal
      ,sum(sal) over (partition by deptno order by sal, ename) as cum_sal
      ,round(100*ratio_to_report(sal) over (partition by deptno),1)  as PCT_DEPT
      ,round(100*ratio_to_report(sal) over (),1)  as PCT_DEPT
from emp;
 ``` 


  
이 함수와 ROLLUP을 함께 사용해서

**Q. 각 부서별 사원 급여의 백분율 및 부서별 급여 합계와 부서별 급여 합계의 백분율을 구해보자**

내용이 어려운데 oracle로 분석 보고서를 뽑는 일이 흔하지 않다고해서 보다가 스킵함


 ``` 
select decode(grouping_id(deptno,empno),0,deptno) as deptno
      ,empno, ename
      ,decode(grouping_id(deptno,empno),0,sum(sal)
                                       ,1,sum(sal) over(partition by deptno)) as sal
      ,lpad(decode(grouping_id(deptno,empno)
                   ,0,round(ratio_to_report(sal) over(partition by deptno) * 100,1)||'%'
                   ,1,round(ratio_to_report(decode(grouping_id(deptno,empno),1,sum(sal)))
                                over()*100,1)||'%'),5,' ') as pct
from emp
group by deptno, rollup((empno,ename,sal));
 ``` 


우선 생성되는 그룹은 아래 조합으로 이뤄진다.

1. deptno, empno, ename, sal

&ensp; &ensp; 1. 사원 급여 백분율 계산

1. deptno

&ensp; &ensp; 1. 부서별 급여 합계와 백분율 계산

1. ()

1번과 2번을 나누어 출력하기 위해 grouping_id + decode 함수를 사용한다.

`round(ratio_to_report(decode(grouping_id(deptno,empno),1,sum(sal)))`

  
  
_______
참고 : https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Analytic-Functions.html#GUID-527832F7-63C0-4445-8C16-307FA5084056
