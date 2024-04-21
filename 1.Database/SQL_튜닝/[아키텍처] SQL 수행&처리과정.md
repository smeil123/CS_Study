  
  
![732b2d56-867a-41d7-85e9-7a632b1e3e80](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/09ba3175-bc66-43d2-b354-47b9fc805f88/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T194006Z&X-Amz-Expires=3600&X-Amz-Signature=3d88489798cccdb5660cfe729dbf2a204491a1b692b5dc634158b9797ef222e3&X-Amz-SignedHeaders=host&x-id=GetObject)
## SQL ‘ Structed Query Language’

- 절차적

- 구조적

- 집합적

- 선언적

  
## Redo 로그

![4d7bade1-4d7e-4570-933e-6f05856f195d](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/3863c8fd-3f30-4a34-bdbe-19456f357783/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T194006Z&X-Amz-Expires=3600&X-Amz-Signature=56240e0ba9992f268ff25633d7073a9ec359a6e982d4345e44ee7f2e1d653e33&X-Amz-SignedHeaders=host&x-id=GetObject)
### 목적

1. Database Recovery

1. Cache Recovery

1. Fast Commit

<details><summary>부연설명</summary></details>

&ensp; &ensp; Cache Recovery

&ensp; &ensp; &ensp; &ensp; DBMS 는 I/O성능을 위해 버퍼캐시 사용하지만 버퍼캐시는 휘발성

&ensp; &ensp; &ensp; &ensp; 인스턴스가 비정상적으로 종료하면 그때까지의 작업을 모두잃게 된다

&ensp; &ensp; &ensp; &ensp; 이를 대비하기위해 Redo로그를 남김

&ensp; &ensp; Fast Commit

&ensp; &ensp; &ensp; &ensp; 사용자가 요구한 갱신을 버퍼캐시에만 기록한 채 디스트에 영구 기록하지 않앗더라도 Redo로그를 믿고 빠르게 커밋을 완료한다는 의미

&ensp; &ensp; &ensp; &ensp; 사용자 프로세스가 안심하고 커밋해도 된다

  
### 매커니즘

1. Log Force at Commit

&ensp; &ensp; 1. DML 수행 → 로그 버퍼에 로깅 → 데이터 블록 변경

&ensp; &ensp; 1. LGWR : 로그 퍼버 기록 → Redo 로그파일에 기록

&ensp; &ensp; 1. 최소한 커밋 시점에는 로그를 메모리가 아닌 데이터파일에 기록해야된다는 의미

1. Fast Commit

&ensp; &ensp; 1. 갱신사항이 아직 버퍼캐시에만 있을 때 Redo로그를 믿고 빠르게 커밋

1. Write Ahead Logging

&ensp; &ensp; 1. DML이 동작해서 버퍼캐시를 갱신하기 전에 Redo엔트리를 로그버퍼에 먼저기록

&ensp; &ensp; 1. `LGWR이` Redo엔트리를 모두 Redo로그 파일에 기록했음 보장 → `DBWR` 이 Dirty블록들을 데이터파일에 기록 전

## Undo 로그

  
### CR Copy 블록

오라클은 변경되었거나 변경이 진행중인 블록을 읽으면 과거 시점으로 되돌린 `CR Copy 블록`을 만들어서 읽는다

- 이때, Undo 정보를 이용

- 필요한 Undo 블록이 다른 트랜잭션에 의해 재사용(Overwriting)된 상태면 CR Copy를 생성 불가

- Snapshot Too Old 에러 발생

  
## 버퍼 블록

버퍼 블록은 아래 세 가지 상태를 가짐

- Free 버퍼 : 비어있거나 데이터 블록과 동기화된 상태

&ensp; &ensp; - 언제든이 덮어 써도 무방한 상태

- Dirty 버퍼 : 데이터파일에 기록하지 않아 동기화가 필요한 상태

- Pinned 버퍼 : 읽기 또는 쓰기 작업을 위해 현재 액세스되고 있는 버퍼 블록

  
  