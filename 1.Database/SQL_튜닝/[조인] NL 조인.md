
  
_______
  
# 힌트


 ``` 
select /*+ ordered use_nl(B) use_nl(c) use_hash(D) */ *
from A,B,C,D
where ...

==
select /*+ leading(A, B, C, D) ~~~ */
 ``` 


A→B→C→D 순으로 조인하되

B와 C와 조인할 땐 NL, 마지막으로 D와 조인할 땐 해쉬 방식으로 하라는 의미

  

 ``` 
select /*+ use_nl(A,B,C,D) */ *
 ``` 


`ordered` 나 `leading` 힌트를 기술하지 않으면, 옵티마이저 스스로 정하도록 맡기는 것

  
## NL 조인 수행 순서

1. Driving 테이블의 인덱스를 사용해서 조건에 맞는 인덱스 스캔 (엑세스, 필터링)

1. Driving 테이블의 조건으로 테이블 필터링

1. 조인 조건 수행 ⇒ Driven 테이블의 조인 키 스캔 (=인덱스 엑세스, 필터링)

1. Driven 테이블의 조건으로 테이블 필터링

1. 정렬

**각 단계는 한 레코드씩 순차 진행**

단, 정렬이 있으면 그 단계는 모두 완료한 후에 진행

  
## NL 조인 부하 시점

![08411b96-d865-4168-b398-4d85158f3908](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/67e3f9f6-ab81-4512-ac50-54dc29ebc7f7/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T194115Z&X-Amz-Expires=3600&X-Amz-Signature=5456b34d73d56d12cd7b1f2d54e7187f46411aa909d09fa295bc5a989617e00f&X-Amz-SignedHeaders=host&x-id=GetObject)
1. 테이블 엑세스에 대한 부하

&ensp; &ensp; 1. gb=’2’ 조건에 필터링 되는게 많으면 ⇒ `인덱스 추가 고려`

1. emp_deptno_idx 탐색에 부하

&ensp; &ensp; 1. outer테이블에 의해 탐색량이 결정 ⇒ `조인 순서 고려 혹은 조인 변경`

1. emp테이블 엑세스 부하

&ensp; &ensp; 1. 마찬가지로 `인덱스 추가 고려`

  
## NL 조인 특징

1. Random 엑세스 위주 조인

&ensp; &ensp; 1. 오라클은 한 레코드를 읽기 위해 블록을 통째로 읽음 ⇒ 비효율이 있는데

&ensp; &ensp; 1. 한 레코드씩 조인할 때 마다 블록을 읽어오게 됨 ⇒ `대량 데이터 조인에 부적합`

1. 한 레코드씩 순차적으로 진행

&ensp; &ensp; 1. 위와 반대로 소량 집합일 때 극적인 속도 ⇒ `부분 범위 처리 가능`** **

&ensp; &ensp; 1. 부분 범위 처리가 가능하려면 sort , group by 가 나오면 안된다.

1. 인덱스를 활용한 조인으로 인덱스가 매우 중요

  
종합적으로 온라인 트랜잭션 환경에 적합한 방식

  
## NL 조인 실행계획 이해하기

![e4feeba1-7f31-4915-8806-2756f62e33f0](https://prod-files-secure.s3.us-west-2.amazonaws.com/d575ed96-de76-4b49-9077-84702d32c50e/ccd1f47c-69f8-4806-a94f-01d58d8b1769/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240420%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240420T194115Z&X-Amz-Expires=3600&X-Amz-Signature=5aa03cba3e217ce0bab778c89754b856101173ef6c86668d7be4058f1b3aca9f&X-Amz-SignedHeaders=host&x-id=GetObject)
  
# 테이블 Prefetch

>모든 DBMS는 디스크 블록을 읽을 때 곧이어 읽을 가능성이 높은 블록을 미리 읽어오는 Prefetch 기능을 제공한다

### Prefectch 란

**한번에 여래 개 Single Block I/O 를 동시 수행하는 것**

- 인접하지 않은 블록을 미리 적재

- I/O Call을 병렬 방식으로 동시에 여러 개 수행

- 적중률이 낮으면(캐시에서 밀려나는 비율) 기능이 작동되지 못하도록 정지

~= Multiblock I/O는 한번의 I/O Call로 서로 인접한 블록들을 같이 읽어 적재

  
Prefetch된 블록들을 모니터링하는 기능은 `CKPT 프로세스` 가 수행


 ``` 
SQL> select name, value from v$sysstat
  2  where name in ('physical reads cache prefetch'  
  3  ,'prefetched blocks aged out before use');

NAME								      VALUE
---------------------------------------------------------------- ----------
physical reads cache prefetch					       4501
prefetched blocks aged out before use					  0
 ``` 


  
### 성능이 향상되는 이유는

데이터 블록을 읽는 도중에 물리적인 디스크 I/O 가 필요하면

→ 서버 프로세스는 I/O Call을 발생시키고 대기

→ 어차피 대기 상태에 쉬어야하므로 곧 읽을 가능성이 높은 블록들을 `미리 버퍼캐시에 적재`

→ 대기 이벤트 발생 횟수를 줄일 수 있음

  
Prefetch는 db file paralled read 대기 이벤트로 측정된다

  
### 실행계획

이 기능 때문에 NL조인에서 새 포맷의 실행계획이 나타난다

! `Outer 쪽 인덱스를 Unique Scan할 때는 작동하지 않음`

  
- Inner 쪽 Non-Unique 인덱스를 Range Scan할 때 항상 나타난다.

- Inner 쪽 Unique 인덱스를 Non-Unique 조건(모두 ‘=’ 조건이 아닐 때) 으로 Range Scan할 때 항상 나타난다.

- Inner 쪽 Unique 인덱스를 Unique 조건으로 액세스할 때도 나타날 수 있다.

&ensp; &ensp; - 드라이빙 집합(outer)의 카디널리티에 따라 나타날 수 있는걸로 보이는데 정확한 규칙은 모름

  
# 배치 I/O

오라클 11g에서 시작, 아직 공식적으로 매커니즘이 알려진 바는 없고 실행계획으로 추정

  
**Inner 쪽 인덱스만으로 조인을 하고 나서 테이블과의 조인은 나중에 일괄 처리하는 매커니즘**

⇒ 우선 조인하고 필요한 테이블은 나중에 가져온다(?)
