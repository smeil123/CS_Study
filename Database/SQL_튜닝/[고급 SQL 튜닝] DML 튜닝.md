
_______
  
# DML 성능

성능에 영향을 미치는 요소

- 인덱스

- 무결성 제약

- 조건절

- 서브쿼리

- Redo / Undo 로깅

- Lock

- 커밋

- 옵티마이저는 아님 → 항상  ALL_Rows로 작동

  
Update를 수행할 때

- 테이블 레코드 : 직접 변경

- 인덱스 레코드 : Delete & Insert 방식으로 처리

&ensp; &ensp; - Undo 레코드도 2개씩 기록

⇒ 인덱스 개수에 따라 Update 성능이 좌우됨

⇒ 대량의 데이터를 입력, 수정, 삭제 시 인덱스를 모두 `Drop 하거나 Unusable 상태로 변경`

  
## 인덱스 및 제약 해제를 통한 대량 DML 튜닝

1,000 만 건 데이터를 입력할 때


- NOVALIDATE 옵션 : 기 입력된 데이터에 대한 무결성 체크를 생략

- PK 인덱스는 unusable 상태이면 데이터를 넣을 수 없어 비활성화하면서 아예 drop해야 함.(2번)

&ensp; &ensp; - drop하지 않고 데이터를 입력하고 싶으면 non-unique 인덱스 사용해야 함(3번)

# Update 튜닝

## 대량의 데이터를 업데이트하면 오래걸림

이유

- 테이블 데이터를 갱신하는 본연의 작업

- 인덱스 데이터까지 갱신

- **버퍼 캐시에 없는 블록을 디스크에서 읽어 버퍼 캐시에 적재한 후 갱신**

- 내부적으로 Redo와 Undo 정보 생성

- 블록에 빈 공간이 없으면 새 블록 할당

## 조인을 내포한 Update 튜닝

### 전통적인 방식

한달이내 거래가 있었던 고객들의 최종 거래를 업데이트


 ``` 
update 고객
set (최종거래일시, 최근거래금액) = (select max(거래일시), sum(거래금액)
													from 거래
													where 고객번호 = 고객.고객번호
													and 거래일시 >= trunc(add_months(sysdate,-1))
where exists ( select 'x'
						from 거래
						where 고객번호 = 고객.고객번호
						and 거래일시 >= trunc(add_month(sysdate,-1))
 ``` 


기본적으로 `고객번호+거래일시` 인덱스가 있어야함

<details><summary>발생하는 비효율</summary></details>

&ensp; &ensp; <details><summary>거래 테이블을 2번 조회함</summary></details>

<details><summary>튜닝 방법</summary></details>

&ensp; &ensp; <details><summary>unnest + hash_sj</summary></details>

&ensp; &ensp; &ensp; &ensp; - 랜덤 액세스를 줄일 수 있으나, 거래 테이블을 2번 액세스하는 비효율까진 줄이지 못함

&ensp; &ensp; <details><summary>수정 가능 조인 뷰 활용</summary></details>

&ensp; &ensp; <details><summary>Merge 문 활용</summary></details>

  
## 수정 가능 조인 뷰

>12c 이상 : 정상적으로 실행
10g 이하 : Update 옆에 bypass_ujvc 힌트 사용
11g : 실행안됨
⇒ 단 Unique인덱스를 잘 활용하면 버전에 상관없이 실행됨

>`조인 뷰`

&ensp; &ensp; - from 절에 **두개 이상 테이블**을 가진 뷰

&ensp; &ensp; - 조인뷰를 통해 원본 테이블에 입력, 수정, 삭제가 가능

>**제약사항**

&ensp; &ensp; - **키-보존 테이블에만** 입력, 수정, 삭제가 허용

&ensp; &ensp; &ensp; &ensp; - 키-보존 테이블 : 조인된 결과 집합을 통해서도 중복 없이 Unique하게 식별가능한 테이블

&ensp; &ensp; &ensp; &ensp; &ensp; &ensp; - 1쪽 집합인 DEPT랑 조인한 EMP는 키-보존 테이블

&ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; - dept랑 emp랑 조인했을 때 emp테이블 키가 보존되고

&ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; - dept는 증폭되니까 테이블 키가 보존되지 않음!!

&ensp; &ensp; &ensp; &ensp; &ensp; &ensp; - 즉, **EMP 테이블은 수정 가능하지만 DEPT 테이블은 수정 불가**

&ensp; &ensp; &ensp; &ensp; - 테이블에 Unique인덱스가 있는지, 조인 키 컬럼으로 Group by를 했는지를 통해 유일성 확인

  
10g 이하 버전 유의

- M쪽 집합을 group by를 통해서 유일성을 확보했더라도 오류가 발생함

- 키가 보존되지만 옵티마이저가 불필요한 제약을 가한 것


 ``` 
update /*+ bypass_ujvc */
 ``` 


- Updatable Join View Check

- 11g 이상부터는 merge문으로 바꿔줘야 함

  

 ``` 
update
	(select /*+ ordered use_hash(c) no_merge(t) */
				**c.최종거래일시, c.최근거래금액, t.거래일시, t.거래금액**
	from (select 고객번호, max(거래일시) 거래일시, max(거래금액) 거래금액
				 from 거래
				 where 거래일시 >= trunc(add_month(sysdate, -1))
				 group by 고객번호) t
				 , 고객 c -- 1쪽 집합
				where c.고객번호 = t.고객번호)
set 최종거래일시 = 거래일시
	 ,최근거래금액 = 거래금액

-- 최근거래일시와 최근거래금액이 맞는 데이터만 입력
 ``` 


`버전에 상관없이 실행`


 ``` 
update
	(select t.주문연락처, t.배송지주소, c.고객연락처, t.고객주소
	 from 거래 t, 고객 c
	 where c.고객번호 = t.고객번호
	 and t.거래일시 >= trunc(sysdate)
	 and t.거래검증코드 = 'INVLD')
set 주문연락처 = 고객연락처
	 ,배송지주소 = 고객주소
 ``` 


위와 다르게 고객테이블을 조회하면서 고객 테이블에 `Unique 인덱스`가 있어서 버전에 상관없이 실행

  
### Merge 문 사용

>Merge into 문은 ⇒ 하나의 SQL안에서 insert, delete, update 한번에 가능

>9i 제공
10g 부터 delete까지 처리
SQL Server도 지원

문법

![f3a751b9-11e5-4677-9ba7-cdc08a3ff384](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/8a13aba1-50cb-4714-9048-02ab0475f761/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T194035Z&X-Amz-Expires=3600&X-Amz-Signature=afadcd8967c6718665a5dd06d8b5c6aef77ae773cd86ebfbd9c3e9a1b6bf4d7a&X-Amz-SignedHeaders=host&x-id=GetObject)
- on 절에 사용한 컬럼은 update에 사용할 수 없음!!


 ``` 
merge into 고객 t using 고객변경분 s on (t.고객번호 = s.고객번호)
when matched then update
	set t.고객번호 = s.고객번호, t.고객명 = s.고객명, t.이메일 = s.이메일,
when not matched then insert
	(고객번호, 고객명, 이메일, 전화번호, 거주지역, 주소, 등록일시) values
	(s.고객번호, s.고객명, s.이메일, s.전화번호, s.거주지역, s.주소, s.등록일시)
 ``` 


  
위에서 봤던 예시를 풀면


 ``` 
merge into 고객 c
using (select 고객번호, max(거래일시) 거래일시, sum(거래금액) 거래금액
			from 거래
			where 거래일시 >= trunc(add_month(sysdate, -1))
			group by 고객번호) t
on (c.고객번호 = t.고객번호)
when matched then update set c.최종거래일시 = t.거래일시, c.최근거래금액 = t.거래금액
 ``` 


  
### 그외 활용 방안

<details><summary>**(1) When절에 조건 가능**</summary></details>

&ensp; &ensp; 
 ``` 
merge into .. using .. on ..
when matched then update
	set t.cust_nm = s.cust_nm, t.email = s.email..
	where reg_dt >= to_date('20200101', 'yyyymmdd')
when not matched then insert
	(cust_id, cust_nm) = (s.cust_id, s.cust_nm)
	where reg_dt <= trunc(sysdate);
 ``` 


<details><summary>**(2) DELETE 절도 가능**</summary></details>

&ensp; &ensp; 
 ``` 
merge into customer t using customer_delta s on (t.cust_id = s.cust_id)
when matched then
	update set t.cust_nm = s.cust_nm, t.email = s.email, ...
	**delete where t.withdraw is not null -- 탈퇴일시가 null 이 아닌 레코드 삭제**
when not matched then insert
...
 ``` 


&ensp; &ensp; MERGE 문에서 **UPDATE가 이뤄진 결과**로 withdraw가 null이 아니면 삭제한다

&ensp; &ensp; → 즉, Merge 수행 결과 null 이면 삭제하지 않는다

<details><summary>**(3)USING 문에 조인한 테이블이 들어가도 됌**</summary></details>

&ensp; &ensp; - 핵심은 불필요한 UPDATE를 안하게 하는것

&ensp; &ensp; - USING이든 ON 이든 업데이트가 필요없는 데이터는 제외되도록 조건절 사용

&ensp; &ensp; 
 ``` 
MERGE INTO 상품재고_X
USING (
	SELECT /*+ */
				A.상품번호, B.신규_품질유지일
	FROM 상품재고 A
				, (SELECT 상품번호, (TRUNC(SYSDATE) - TO_DATE(MAX(변경일자), 'YYYYMMDD')) 신규_품질유지일
					FROM 상품재고이력
					GROUP BY 상품번호 ) B
	WHERE A.업체코드 = 'Z'
	AND NVL(A.가상재고수량,0) <= 0
	AND A.상품번호 = B.상품번호
**	AND A.품질유지일 <> B.신규_품질유지일 -- 업데이트 하지 않아도 되는 것은 거르기
**	) A
ON (X.상품번호 = T.상품번호)
WHEN MATCHED THEN UPDATE
set X.ㅂㅜㅁ질유지비=
 ``` 


<details><summary>**(4)USING문 DUAL 활용(값이 있으면 update, 없으면 insert)**</summary></details>

&ensp; &ensp; 
 ``` 
merge into dept a
using (select :var1 deptno, :var2 dname, :var3 loc from dual) b
on (b.deptno = a.deptno)
when matched then
	update set dname = b.dname, loc = b.loc
when not matched then
	insert (a.deptno, a.dname, a.loc) values (b.deptno, b.dname, b.loc);
 ``` 


  
### Merge Into 가 항상 정답은 아님


 ``` 
merge into emp t2
using (select t.rowid as rib, s.ename
			from emp t, emp_src s
			where t.empno = s.empno
			and e.ename <> s.ename) s
on (t2.rowid = s.rid)
when matched then update set t2.ename=s.ename;
 ``` 


문제점

- emp 테이블을 2번 읽음 (select 때 , update 때)

- using에서 검증된 테이블을 만들고 위에 merge문을 씌운 구조 

- 굳이 이렇게 할 필요가 없음

`개선1` - merge문 사용


 ``` 
merge into emp t2
using (select s.empno, s.ename from emp_src ) s
on t2.empno = s.empno
when matched then update set t2.ename = s.ename
where t2.ename <> s.ename;
 ``` 


`개선2`- 수정가능한 조인 뷰


 ``` 
update (
	select t.ename as t_name, s.ename as s_name
	from emp t, emp_src s
	where t.empno = s.empno
	and e.ename <> s.ename
)
set t_name = s_name;
 ``` 


  
_______
# Direct Path I/O

배치 프로그램의 경우 `버퍼캐시`를 경유하는게 더 비효율

- 캐시에 원하는 값이 있을 확률이 낮음, 자주 접근하는 데이터가 아니기 때문에

- 온라인 트랙잭션에선 성능 향상에 도움을 줌

>**버퍼 캐시**를 경유하지 않고 곧바로 **데이터 블록**을 읽고 쓸 수 있는 기능

  
### Direct Path I/O 동작하는 경우

1. 병렬 쿼리로 **Full Scan**

&ensp; &ensp; <details><summary>예시 : parallel(t 4)</summary></details>

&ensp; &ensp; &ensp; &ensp; 
 ``` 
select /*+ full(t) parallel(t 4) */ from big_table t;

select /*+ index_ffs(t big_table_x1) parallel_index(t big_table_x1 4)*/ count(*)
from big_table t;
 ``` 


&ensp; &ensp; &ensp; &ensp; 병렬도를 4로 지정하면 4배 빨라지는게 아니라 수십 배 빨라짐 → 버퍼캐시를 탐색하지 않는 효과

&ensp; &ensp; &ensp; &ensp;   
1. **병렬 DML**

&ensp; &ensp; <details><summary>예시</summary></details>

&ensp; &ensp; &ensp; &ensp; 1. INSERT 는 append 힌트로 병렬 쿼쿼리 유도 가능

&ensp; &ensp; &ensp; &ensp; 1. UPDATE, DELETE 는 병렬 DML을 활성화해야함 (INSERT 도 동일)

&ensp; &ensp; &ensp; &ensp; 
 ``` 
alter session enable parallel dml;

-- append 힌트를 지정하지 않아도 Direct Path Insert 방식 사용
insert /*+ parallel(c 4) */ into 고객 c
select /*+ full(o) parallel(o 4)*/ from 외부가입고객 o;


update /*+full(c) parallel(c 4) */ 고객 c set 고객상태 ='WD';
delete /*+full(c) parallel(c 4) */ from 고객 c
 ``` 


&ensp; &ensp; &ensp; &ensp; - 12C 부터는 힌트도 지원

&ensp; &ensp; &ensp; &ensp; 
 ``` 
insert /*+ enable_parallel_dml parallel(c 4)*/ ...
 ``` 


&ensp; &ensp; &ensp; &ensp; **이 때도 Exclusive 모드 TM Lock이 걸리는 사실 꼭 기억하기**

&ensp; &ensp; &ensp; &ensp; `실행계획`

&ensp; &ensp; &ensp; &ensp; 
 ``` 
...
PX COORDINATOR
	..
	UPDATE
-- 이 순서로 나와야 병렬처리 된 것
 ``` 


1. **Direct Path Insert**

1. Temp 세크먼트 블록들을 읽고 쓸 때

1. direct 옵션을 지정하고 export할 때

1. nocache 옵션을 지정한 LOB 컬럼을 읽을 때

  
# Insert 튜닝

  
Oracle엔 아래 두가지 방법 존재

## 1. Direct Path Insert (Oracle)

>예외) IOT는 정해진 키 순으로 정렬하면서 값을 입력

일반적인 힙 구조 테이블은 순서 없이 Freelist(빈 공간에)부터 할당받은 블록에 무작위로 값을 입력한다.

  
- 일반적인 트랜잭션 처리 : 빈 공간부터 찾아 채워나가는 방식이 효율적

&ensp; &ensp; - 빈 공간 사용을 효율적으로

- 대량 데이터 입력: 위 방법이 비 효율적, 하나씩 빈공간을 찾아가야됨

&ensp; &ensp; - `Direct Path Inser``t 방식` : Freeliest, 버퍼캐시를 거치지 않고 데이터 파일에 곧바로 입력 & `Undo 데이터도 안쌓음`

  
### 방법

1. insert select 문장에 `/*+ append */` 힌트 사용

1. 병렬 모드로 Insert

&ensp; &ensp; - 병렬 DML을 활성화한 상태에서 INSERT문에 parallel 힌트 사용


 ``` 
ALTER SESSION ENABLE PARALLEL DML

INSERT /*+ PARALLEL(T 4) */ INTO target_t T
select * FROM source_t;
 ``` 


1. direct옵션을 지정하고 SQL*Loader(sqlldr)로 데이터 로드

1. `CTAS` 문장 수행

  
### 빠른 이유

1. Freelist를 참조하지 않고 HWM 바깥 영역에 데이터를 순차적으로 입력

1. 블록을 버퍼캐시에서 탐색하지 않음

1. 버퍼캐시에 적재하지 않고, 데이터 파일에 직접 기록

1. Undo 로깅을 안함

1. Redo 로깅을 안하게 할 수 있음

&ensp; &ensp; 
 ``` 
alter table t NOLOGGING;
-- insert문에 힌트로는 불가
 ``` 


### 주의점

>-

&ensp; &ensp; 1. **Exclusive 모드 테이블 Lock이 걸림**

&ensp; &ensp; &ensp; &ensp; - 커밋 전까지 해당 **테이블**에 다른 트랜잭션 접근 불가

&ensp; &ensp; 1. 테이블에 여유 공간이 있어도 재활용하지 않음

&ensp; &ensp; &ensp; &ensp; 1. 과거 데이터를 주기적으로 delete해서 여유 공간이 생겨도 이 방식으로만 계속 insert하는 **테이블은 사이즈가 줄지 않고 계속 늘어감**

&ensp; &ensp; &ensp; &ensp; &ensp; &ensp; 1. **DROP**으로 공간 반환을 해주거나, 비 파티션 테이블이면 주기적으로 **Reorg **작업을 수행해줘야 한다.

&ensp; &ensp; &ensp; &ensp; &ensp; &ensp; 1. DELETE 방식으로는 지운 공간이 반환되지 않고 INSERT에 의해 재활용

## 2. nologging 모드 Insert (Oracle)

**Redo로그 최소화됨 ⇒ 이 기능은 Direct Path Insert일 때만 작동**

>일반 Insert문을 로깅하지 않는 방법은 없음
**힌트로 제공되는것이 아님**

위에 포함되는 내용이긴 함


 ``` 
alter table t NOLOGGING;

INSERT /*+ APPEND */ INTO t
select * from source_t;
 ``` 


  
### 주의

장애 발생 시 복구 불가

**DW시스템에서 읽기 전용 데이터 적재 시 유용**

  
<details><summary>Sql Server는 아래 다른 방법 사용</summary></details>

&ensp; &ensp; ## 최소 로깅

&ensp; &ensp; 
 ``` 
-- 아래 설정이 되어있어야하고
alter database SQLPRO set recovery SIMPLE

BULK INSERT ~~
FROM ~~
WITH
(
  ...
  TABLOCK
)
 ``` 


&ensp; &ensp; 다음에 다시 정리

&ensp; &ensp;   
  
_______
  
# Delete vs Truncate

**Delete 문**

- Redo로그와 Undo를 생성하면서 레코드 단위로 삭제

  
**Truncate 문**

- 딕셔너리 상에서 익스텐트만 반환하는 방식으로 빠름

  
  
  
_______
## 응용 편

<details><summary>온라인 트랜잭션있는 주간에 대량 데이터 INSERT 튜닝</summary></details>

&ensp; &ensp; <details><summary>Array Processing O</summary></details>

&ensp; &ensp; <details><summary>Direct Path Insert X</summary></details>

&ensp; &ensp; &ensp; &ensp; <details><summary>해당 테이블 DML 불가</summary></details>

&ensp; &ensp; <details><summary>nologging X</summary></details>

&ensp; &ensp; &ensp; &ensp; <details><summary>이 기능은 Direct Path Insert와 함께 써야 함</summary></details>

<details><summary>아래 쿼리 튜닝</summary></details>

&ensp; &ensp; 
 ``` 
DELETE FROM TARGET_T;

COMMIT;

ALTER SESSION ENABLE PARALLEL DML;

INSERT /*+ APPEND */ INTO TARGET_T T1
SELECT /*+ FULL(T2) PARALLEL(T2 4) */
FROM SOURCE_T T2;

COMMIT;

ALTER SESSION DISABLE PARALLEL DML;
 ``` 


&ensp; &ensp; <details><summary>튜닝 쿼리</summary></details>

&ensp; &ensp; 
 ``` 
TRUNCATE TARGET_T;

ALTER TABLE TARGET_T MODIFY CONSTRAINT TARGET_T_PK DISABLE DROP INDEX;

ALTER SESSION ENABLE PARALLEL DML;

INSERT /*+ PARALLEL(T1 4)*/ INTO TARGET_T T1
SELECT /*+ FULL(T2) PARALLEL(T2 4) */
FROM SOURCE_T T2;

COMMIT;

ALTER TABLE TARGET_T MODIFY CONSTRAINT TARGET_T_PK ENABLE NOVALIDATE;

ALTER TABLE TARGET_T LOGGING;

ALTER SESSION ENABLE PARALLEL DML;
 ``` 


&ensp; &ensp; - Truncate문으로 빠르게 삭제

&ensp; &ensp; - 제약조건을 해제하고 인덱스를 Unable 상태로 변경

&ensp; &ensp; - 읽기말고 Insert도 병렬로 처리하도록 추가

<details><summary>아래 쿼리 튜닝</summary></details>

&ensp; &ensp; - UPDATE 문 c1조건절 만족 데이터 90%

&ensp; &ensp; - MYTAB 테이블 PK = DT + ID

&ensp; &ensp; - 병렬처리 X

&ensp; &ensp; 
 ``` 
**CREATE TABLE MYTAB_TEMP
AS
SELECT C0 AS ID, C1, C2, C3, C4
FROM YOURTAB@RDS
WHERE 1=2; -- 테이블 스키마만 가져간다**

**ALTER TABLE MYTAB_TEMP ADD CONSTRAINT MYTAB_TEMP_PK PRIMARY_KEY(ID);
**
DECLARE
	V_CNT NUMBER;
BEGIN
	**INSERT INTO MYTAB_TEMP
	SELECT C0, C1, C2, C3, C4
	FROM YOURTAB@RDS
	WHERE C0 IS NOT NULL
	AND C5 > 0;**
	
	-- 90%
	**UPDATE MYTAB_TEMP SET C4 = C4 + 1 WHERE C1 < TRUNC(SYSDATE);**

	-- 배치 프로그램 재실행 대비
	DELETE FROM MYTAB WHERE DT = TO_CHAR(SYSDATE, 'YYYYMMDD');
**
	INSERT INTO MYTAB (DT, ID, C1, C2, C3, C4)
	SELECT TO_CHAR(SYSDATE, 'YYYYMMDD'), A.* FROM MYTAB_TEMP A;**

	
 ``` 


&ensp; &ensp; <details><summary>튜닝문</summary></details>

&ensp; &ensp; 
 ``` 
CREATE TABLE MYTAB_TEMP
NOLOGGING
AS
SELECT C0 AS ID, C1, C2, C3
			, (CASE WHEN C1 < TRUNC(SYSDATE) THEN C4+1 ELSE C4 END) AS C4
FROM YOURTAB@RDS
WHERE CO IS NOT NULL
AND C5 > 0;

DECLARE
	V_CNT NUMBER;
BEGIN
	-- ID에 중복 값이 있는지 확인
	SELECT COUNT(*) INTO V_CNT
	FROM ( SELECT ID
					FROM MYTAB_TEMP
					GROUP BY ID
					HAVING COUNT(*) > 1);

	IF V_CNT > 0 THEN
		INSERT_LOG(SYSDATE, 'INSERT MYTAB_TEMP', 'FAIL', '중복 데이터');
	ELSE
		DELETE FROM MYTAB WHERE DT = TO_CHAR(SYSDATE, 'YYYYMMDD');
	**
		INSERT INTO MYTAB (DT, ID, C1, C2, C3, C4)
		SELECT TO_CHAR(SYSDATE, 'YYYYMMDD'), A.* FROM MYTAB_TEMP A;

...**

 ``` 


&ensp; &ensp; - UPDATE를 하면 REDO와 UNDO를 건건이 생성하면서 오래 걸림

&ensp; &ensp; &ensp; &ensp; - 따로하지 않고 MYTAB_TEMP생성 시 한번에

&ensp; &ensp; &ensp; &ensp; - CTAS문을 사용하면 Direct Path Insert 기능 작동

&ensp; &ensp; - PK 제약을 생성한 후 대량 데이터 입력시 시간이 오래 걸림

&ensp; &ensp; &ensp; &ensp; - ID에 중복값이 존재하는지 확인한 후에 입력하도록 수정하면 굳이 생성하지 않아도 된다

<details><summary>아래 쿼리 튜닝</summary></details>

&ensp; &ensp; 
 ``` 
UPDATE 고객 C
SET 법정대리인_연락처 = 
			NVL ( (SELECT 연락처
							FROM 고객
							WHERE 고객번호 = C.법정대리인_고객번호)
						, C.법정대리인_연락처)
WHERE 성인여부 = 'N'
 ``` 


&ensp; &ensp; - 고객 : 100만명

&ensp; &ensp; - 미성년자 = 2%

&ensp; &ensp; - 법정대리인을 등록한 미성년자 = 50%

&ensp; &ensp; <details><summary>문제점은?</summary></details>

&ensp; &ensp; &ensp; &ensp; - 법정대리인을 등록하지 않은 미성년 고객까지 모두 UPDATE

&ensp; &ensp; &ensp; &ensp; - 법정대리인이 변경되지 않은 미성년 고객들도 UPDATE

&ensp; &ensp; &ensp; &ensp; ⇒ 불필요한 테이블 LOCK 을 유발시킴

&ensp; &ensp; &ensp; &ensp; <details><summary>수정가능 조인 뷰로 변경</summary></details>

&ensp; &ensp; &ensp; &ensp; 
 ``` 
UPDATE(
	SELECT /*+ LEADING(C) USE_NL(P) INDEX(C 고객_X3) INDEX(P 고객_PK)*/ 
				C. 법정대리인_연락처, P.연락처
	FROM 고객 C, 고객 P
	WHERE C.성인여부 = 'N'
	AND C.법정대리인_고객번호 IS NOT NULL -- 불필요한 조인을 제거 (옵티마이저가 자동으로 실행하지만 기재)
	AND P.고객번호 = C.법정대리인_고객번호 -- 조인
	AND P.연락처 <> C.법정대리인_연락처 -- 업데이트 된 사람만
)
SET 법정대리인_연락처 = 연락처
 ``` 


&ensp; &ensp; &ensp; &ensp; <details><summary>MERGE 문으로 변경</summary></details>

&ensp; &ensp; &ensp; &ensp; 
 ``` 
merge into emp_temp e
using emp_temp m
	on ( e.mgr is not null -- 불필요한 조인 컬럼
			and m.empno = e.mgr)
when matched then UPDATE
	set e.mgr_name = m.ename
	where e.mgr_name <> m.ename; -- set에서 사용하는 컬럼은 on절에 사용할 수 없음
 ``` 


&ensp; &ensp; &ensp; &ensp;   
  