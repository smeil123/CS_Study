
_______
  
  
# LOCK

- 래치 : SGA에 공유된 각종 자료구조 보호

- 버퍼 Lock : 버퍼 블록에 대한 엑세스 직렬화

- 라이브러리 캐시 Lock & Pin : 라이브러리 캐시에 공유된 SQL 커서와 PL/SQL 프로그램 보호

- DML Lock : 다중 트랜잭션이 동시에 엑세스하는 사용자 데이터의 무결성 보호

&ensp; &ensp; - 테이블 Lock, 로우 Lock

  
## DML 로우 Lock

두 개의 동시 트랜잭션이 같은 로우를 변경하는 것을 방지

### 특징

- 모든 DBMS는 DML 로우 Lock에는 배타적 모드 사용

- UPDATE, DELETE 가 진행 중이면 다른 트랜잭션은 U/D 부락

- INSERT에 대한 로우 Lock 경합은 `Unique`한 인덱스가 있을 때만 `블록킹`발생

&ensp; &ensp; - 후행 트랜잭션이 기다렸다가

&ensp; &ensp; &ensp; &ensp; - 선행 트랜잭션이 성공하면 ⇒ Insert 실패

&ensp; &ensp; &ensp; &ensp; - 선행 트랜잭션이 롤백하면 ⇒ Insert 성공

&ensp; &ensp; - 두 트랜잭션이 서로 다른 값을 입력하거나 Unique 인덱스가 아에 없으면 로우 Lock 경합은 발생하지 않음

### 오라클 Select (MVCC 모델)

- Select문에 로우 Lock을 사용하지 않음(for update 절 X)

- 다른 트랜잭션이 변경한 로우를 읽을 대 복사본 블록을 만들어서 쿼리가 시작된 시점으로 되돌려 읽음

&ensp; &ensp; - select 쿼리가 시작된?

- 변경이 진행 중인 로우를 읽을 때는 Lock 이 풀릴 때까지 기다리지 않고 복사본을 만들어 읽음

>오라클에서 DML과 SELECT는 서로 진행을 방해하지 않음

  
## DML 테이블 Lock = `TM Lock`

오라클은 DML 로우 Lock을 설정하기에 앞서 테이블 Lock을 먼저 설정한다

- 로우 Lock : 항상 배타적 모드 사용

- 테이블 Lock : 여러가지 모드 사용

  
### 종류

- RS : row share

- RX : row exclusive

- S : share

- SRX : share row exclusive

- X : exclusive

### 동작

선행 트랜잭션과 호환되지 않는 모드로 테이블 Lock을 설정하려는 후행 트랜잭션은 대기하거나 작업을 포기해야 한다.

- INSERT, UPDATE, DELETE, MERGE 문 : **RX** 모드 테이블 Lock

- SELECT FOR UPDATE : 10g 이하 RS, 11g 이상 **RX**

  
테이블 Lock 은 어떤 작업을 수행 중인지 알리는 푯말로

어떤 모드를 사용했는지에 따라 후행 트랜잭션이 수행할 수 있는 작업의 범위 결정

  
## SELECT FOR UPDATE 문 옵션

1. Lock이 해제될 때까지 기다림 : select * from t for update

&ensp; &ensp; 1. DML 문 기본설정

1. 일정 시간만 기다리도 포기 : select * from t for update wait 3

1. 기다리지 않고 작업 포기 : select * from t for update nowait

&ensp; &ensp; 1. DDL 문 기본설정

&ensp; &ensp;   