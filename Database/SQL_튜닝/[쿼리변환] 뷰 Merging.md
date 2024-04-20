  
# 뷰 머지

옵티마이저는 최적화를 좀 더 잘 하기 위해 쿼리 블록을 풀어내려는 습성을 갖는다.

  
### 뷰 Merging 실행계획

실행 계획에 `VIEW`  라는 단어 O ⇒ 뷰 머징 안됨

조인으로 처리 ⇒ 뷰 머징 됨

  
### 뷰 Merging하면 오히려 성능이 더 나빠질 수 있음

- Group by 절

- select-list에 distinct 연산자 포함

  
### 힌트


 ``` 
--- 뷰쪽 select 문에
/*+ merge */ 

/*+ no_merge */ 
 ``` 

