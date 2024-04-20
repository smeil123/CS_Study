  
# 트랜잭션 고립화 수준

### 레벨 0 ( = Read Uncommitted)

- 트랜잭션에서 처리 중인, 아직 커밋되지 않은 데이터를 다른 트랜잭션이 읽는 것을 허용

- Dirty Read, Non-Repeatable Read, Phantom Read 현상 발생

- 오라클은 지원 X

  
### 레벨 1 ( = Read Committed)

- Dirty Read 방지 : 트랜잭션이 커밋되어 확정된 데이터만 읽는 것을 허용

- 대부분의 DBMS가 기본모드로 채택하고 있는 일관성 모드

- Non-Repeatale Read, Phantom Read 현상 발생

- Oracle은 Lock을 사용하지 않고 쿼리시작 시점의 Undo 데이터를 제공하는 방식으로 구현

- 그 외, 읽기 공유 Lock 을 이용해 구현

  
### 레벤 2 ( = Repeatable Read)

- 선행 트랜잭션이 읽은 데이터는 트랜잭션이 종료될 때까지 후행 트랜잭션이 갱신하거나 삭제하는 것을 불허 ⇒ 같은 데이터를 두 번 쿼리했을 때 일관성 있는 결과 리턴

- Phantom Read 현상 발생

- Oracle은 레벨을 명시적으로 지원하지 X

&ensp; &ensp; - for update절을 이용해 구현 가능

- 그 외, 트랜잭션 고립화 수준을 Repeatable Read로 변경하면 읽은 데이터에 걸린 공유 Lock을 커밋할 때까지 유지하는 방식으로 구현

  
### 레벨 3 ( = Serializable)

- 선행 트랜잭션이 읽은 데이터를 후행 트랜잭션이 갱신하거나 삭제하지 모할 뿐만 아니라 `중간에 새로운 레코드를 삽입하는 것도 막음`

- **완벽한 읽기 이관성 모드 제공**
