


### 변수 선언 방식 차이
| 차이점 | var | let | const |
|--|--|--|--|
| 중복선언 | O | X | X |
| 값 재할당 | O | O | X |
| scope | 함수 레벨(함수 내부에서 선언된변수만 지역변수, 나머지는 전역변수) | 블록 레벨(거의 지역변수로 취급) | 블록 레벨(거의 지역변수로 취급)|
| 호이스팅 | 변수 호이스팅 발생 | 변수 선언만 해두고, 초기화는 코드 실행과정됨 | 변수 선언만 해두고, 초기화는 코드 실행과정됨 |
| 전역객체 프로퍼티 부여 | window | X | X |

> 호이스팅은 자바스크립트 특성으로, 코드 실행하기 전에 필요한 변수가 미리 선언된다
```
console.log(a); // undefined  
var a = 10; 
console.log(a); // 10  
````

**결론**
1순위 : const를 최우선적으로 사용한다.
2순위 : let은 변수 값을 재할당할 필요가 있을 때만 사용한다.

### 메모리 구조, 변수 생셩 원리, 가비지컬렉터
https://curryyou.tistory.com/275
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTU1ODg3OTkzNV19
-->