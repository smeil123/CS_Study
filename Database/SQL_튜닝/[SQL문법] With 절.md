
_______
  
- oracle 9i부터 사용 가능

- 쿼리 내에서 한 번 이상 사용되는 집합을 미리 **임시 테이블**로 저장

- 문장 안에서 반복 사용이 가능

&ensp; &ensp; - 다른 쿼리에서는 사용이 불가함

  
### 사용하는 이유

사실 With절 없어도 Inline뷰를 사용하면 쿼리는 가능하나

상황에 따라 같은 테이블을 여러 번 반복 읽어야되고, 코드가 복잡해져 유지보수가 용이하지 못한 단점이 있다.

이 때, With절을 사용하면 반복 접근이 필요한 뷰를 With절에 선언해두고 아래 쿼리에서 사용하면 되어 활용도가 높아진다.

## 사용 예시


 ``` 
**with agg_emp as (select deptno, round(avg(sal)) as avg_sal
                    from emp
                    group by deptno)**
select a.empno, b.avg_sal
from emp a
    ,**agg_emp **b
where a.deptno = b.deptno
and a.sal > b.avg_sal;
 ``` 


with 절에서 만들 테이블 명을 명시하고, 뒤에 select절을 붙이면 된다.

, 로 연결해서 여러 개의 임시 테이블도 만들 수 있다.


 ``` 
WITH agg_emp AS (SELECT deptno, ROUND(AVG(sal)) AS avg_sal 
                   FROM emp 
                  GROUP BY deptno) 
   , avg_emp AS (SELECT ROUND(AVG(avg_sal)) avg_tot
                   FROM agg_emp) 
 ``` 


  
위 쿼리는 Inline View로도 충분히 가능하다.

그렇다면 성능적인 면에서는 어떤 차이가 있는지 확인해보자.

## 실행계획 비교하기(Inline view VS With)

두 개 실행 계획을 뽑아봤는데 동일한 플랜이 나오는 걸 확인했다.

여기서 알 수 있는 점은

**with절에서 정의한 테이블을 한 번만 사용하면 Temp Table을 만들지 않고 옵티마이저가 inline와 동일하게 실행한다는 것이다.**


 ``` 
--- With 절 & inline view 절
----------------------------------------------------------------------------------------------
| Id  | Operation                    | Name          | Rows  | Bytes | Cost (%CPU)| Time     |
----------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT             |               |     1 |    51 |     7  (29)| 00:00:01 |
|   1 |  MERGE JOIN                  |               |     1 |    51 |     7  (29)| 00:00:01 |
|   2 |   TABLE ACCESS BY INDEX ROWID| EMP           |    14 |   350 |     2   (0)| 00:00:01 |
|   3 |    INDEX FULL SCAN           | EMP_DEPTNO_IX |    14 |       |     1   (0)| 00:00:01 |
|*  4 |   FILTER                     |               |       |       |            |          |
|*  5 |    SORT JOIN                 |               |     3 |    78 |     5  (40)| 00:00:01 |
|   6 |     VIEW                     |               |     3 |    78 |     4  (25)| 00:00:01 |
|   7 |      SORT GROUP BY           |               |     3 |    21 |     4  (25)| 00:00:01 |
|   8 |       TABLE ACCESS FULL      | EMP           |    14 |    98 |     3   (0)| 00:00:01 |
----------------------------------------------------------------------------------------------
 ``` 


  
### 그렇다면 두 번 접근하면 실행계획은?

**Inline View**


 ``` 
--- 부서원 급여 합계 평균보다 높은 부서
select deptno, sum(sal) as sum
from emp
group by deptno
having sum(sal) > (select avg(sum(sal))
										from emp
										group by deptno);
-----------------------------------------------------------------------------
| Id  | Operation            | Name | Rows  | Bytes | Cost (%CPU)| Time     |
-----------------------------------------------------------------------------
|   0 | SELECT STATEMENT     |      |     1 |     7 |     4  (25)| 00:00:01 |
|*  1 |  FILTER              |      |       |       |            |          |
|   2 |   HASH GROUP BY      |      |     1 |     7 |     4  (25)| 00:00:01 |
|   3 |    TABLE ACCESS FULL | EMP  |    14 |    98 |     3   (0)| 00:00:01 |
|   4 |   SORT AGGREGATE     |      |     1 |     7 |     4  (25)| 00:00:01 |
|   5 |    SORT GROUP BY     |      |     1 |     7 |     4  (25)| 00:00:01 |
|   6 |     TABLE ACCESS FULL| EMP  |    14 |    98 |     3   (0)| 00:00:01 |
-----------------------------------------------------------------------------
 ``` 


EMP 테이블을 2번 Access한 것을 확인할 수 있다.

1. [4-6] EMP 테이블을 group by 하고 집계한 결과에 집계함수를 사용하면서 sort aggregate 절이 나타남

1. [1-3] having 절에서 filter하여 결과를 반환

>궁금증? 똑같이 group by 했는데 왜 한번은 sort group by 이고 한번은 hash group by 이지?
hash group by → group by 만
sort group by → group by + order by

  
**With 절**


 ``` 
with sum_sal as (select deptno, sum(sal) as sum
                    from emp
                    group by deptno)
select * 
from sum_sal
where sum > (select avg(sum) from sum_sal);

----------------------------------------------------------------------------------------------------------------------
| Id  | Operation                                | Name                      | Rows  | Bytes | Cost (%CPU)| Time     |
----------------------------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                         |                           |     3 |    78 |     8  (13)| 00:00:01 |
|   1 |  TEMP TABLE TRANSFORMATION               |                           |       |       |            |          |
|   2 |   LOAD AS SELECT (CURSOR DURATION MEMORY)| SYS_TEMP_0FD9D7747_184A40 |       |       |            |          |
|   3 |    HASH GROUP BY                         |                           |     3 |    21 |     4  (25)| 00:00:01 |
|   4 |     TABLE ACCESS FULL                    | EMP                       |    14 |    98 |     3   (0)| 00:00:01 |
|*  5 |   VIEW                                   |                           |     3 |    78 |     2   (0)| 00:00:01 |
|   6 |    TABLE ACCESS FULL                     | SYS_TEMP_0FD9D7747_184A40 |     3 |    21 |     2   (0)| 00:00:01 |
|   7 |    SORT AGGREGATE                        |                           |     1 |    13 |            |          |
|   8 |     VIEW                                 |                           |     3 |    39 |     2   (0)| 00:00:01 |
|   9 |      TABLE ACCESS FULL                   | SYS_TEMP_0FD9D7747_184A40 |     3 |    21 |     2   (0)| 00:00:01 |
----------------------------------------------------------------------------------------------------------------------
 ``` 


Temp Table이라는 구문이 나타났고, EMP테이블은 한번만 엑세스함을 알 수있따.

그 이후에는 SYS_TEMP이란 것을 활용해서 쿼리 수행이 이뤄진다.

아까와는 달리 실행계획이 다르게 나타남을 확인할 수 있다.

  
### 성능적인 부분(주의 사항)

위 예시는 deptno 로 group by하기 때문에 테이블의 크기가 작아서 with 절을 사용하는데 전혀 문제가 없다.

  
**만약 여기서 임시 테이블의 크기가 커진다면?**

- 임시 테이블을 저장하기에 메모리공간이  부족하여 디스크로 넘어가게 되면 오히려 성능에 영향을 줄 수 있다.

&ensp; &ensp; → 디스크 I/O작업이 발생하는데, 그냥 테이블을 읽기만하던 작업이 쓰기까지 동반하게 된다

&ensp; &ensp; → 인라인 뷰로 작성하면 여러 조인과 최적화 작업으로 해결할 수 있음

무차별적인 남용은 지양해야된다!

  
## 힌트 ( materialize )

그리고 이때 힌트를 사용해서 TEMP Table을 만질지 여부를 조정할 수 있다.


 ``` 
/*+ materialize */ -- 임시테이블 생성
/*+ inline */ -- 임시테이블을 생성하지 않고 인라인뷰로 수행
 ``` 


## 정리

- 문장 안에서 With 절의 Subquery 사용 횟수에 따라 실행계획이 달라진다.

&ensp; &ensp; - 두 번 이상 사용되면 → 임시 테이블 생성

&ensp; &ensp; - 한번 사용하면 Inline View 와 동일함

- Temp Table 생성 여부를 유도하는 힌트도 존재

- With 절의 임시 테이블 형식의 사용은 Physical I/O를 동반할 수 있으므로 그 크기가 크지 않는 경우 유리

  