
# JPA 란?

관계형 데이터베이스는 SQL을 통해서만 데이터를 접근할 수 있다.
그렇기에 프로젝트를 진행하면 코드의 대부분은 SQL로 작성되어진다.

### 문제점
RDB는 어떻게 데이터를 저장할지에 초점이 맞춰진 기술이나,
객체지향 프로그래밍 언어인 JAVA는 메세지를 기반으로 기능과 속성을 한 곳에서 관리하는 기술이다.

둘의 시작점이 다르기 때문에, 서로를 이해하는데 어려움이 존재했고 이를 완하하고자 JPA라는 기술을 사용한다.

즉, JPA 를 이용해 SQL에 종속적인 개발을 하지 않고, 객체지향적인 프로그래밍을 할 수 있게 한다.

#### 예시
```
User user = findUser();
Group group = user.getGroup();
```
이 코드를 보면, User-Group = 부모-자식 관계임을 알 수 있다.

반대로, 아래의 코드는 DB조회를 위한 코드이다
```
User user = userDao.findUser();
Group group = groupDao.findGroup(user.getGroupId());
```
user의 그룹아이디로 group정보를 받아오는 건 알 수 있으나, 둘 사이가 어떤 관계인지는 알 수 없다.


### Spring Data JPA
JPA는 인터페이스로서 자바 표준명세서이다.
* 인터페이스인 JPA를 사용하기 위해서는 구현체가 필요하다.
	* 대표적으로 Hibernate, EclipseLine 등
* 하지만 Spring에서는 이 구현체들을 직접 다루진 않고, Sping Data JPA사용
	* JPA <- Hibernate <- Spring Data JPA

왜 한단계 더 감싸둔 Spring Data JPA를 사용하는가?
* 구현체 교체의 용이성
	* Hibernate외에 다른 구현체로 쉽게 교체하기 위함
* 저장소 교체의 용이성
	* RDB외에 다른 저장소로 쉽게 교체하기 위함

### 실무에서 JPA

<!--stackedit_data:
eyJoaXN0b3J5IjpbMTM4MTkxNTc5Ml19
-->