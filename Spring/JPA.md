
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


### Entity 클래스와 기본 Entity Repository를 생성해서 사용한다

* 두 개 파일은 같은 경로에 존재해야 한다
* 기본 Repository 없이는 Entity클래스의 역할을 할 수 가 없다.
* 
예시 entity 클래스
```java
package com.springboot.project.domain.posts;  
  
import lombok.Builder;  
import lombok.Getter;  
import lombok.NoArgsConstructor;  
  
import javax.persistence.Column;  
import javax.persistence.Entity;  
import javax.persistence.GeneratedValue;  
import javax.persistence.GenerationType;  
import javax.persistence.Id;  
  
@Getter  
@NoArgsConstructor // 기본 생성자 자동 추가, public Posts() {}와 같은 효과  
@Entity  
public class Posts {  
  
    @Id // 해당 테이블의 PK필드를 나타냄  
  @GeneratedValue(strategy = GenerationType.IDENTITY) //PK생성규칙  
  private Long id;  
  
  // 테이블의 컬럼, 굳이 안써도되지만 기본값 외에 추가로 변경이 필요한 옵션이 있으면 사용  
  @Column(length = 500, nullable = false)  
    private String title;  
  
  @Column(columnDefinition = "TEXT", nullable = false)  
    private String content;  
  
 private String author;  
  
  @Builder // 해당 클래스의 빌더 패턴 클래스 생성, 생성자 상단에 선언 시 생성자에 포함된 필드만 빌더  
  // 생성자나 빌더나 생성 시점에 값을 채워주는 역할은 똑같으나,  
 // 생성자의 경우 지금 채워야할 필드가 무엇인지 지정할 수가 없다  
  public Posts(String title, String content, String author){  
        this.title = title;  
 this.content = content;  
 this.author = author;  
  }  
  
}
```

entity repository
```java
package com.springboot.project.domain.posts;  
  
import org.springframework.data.jpa.repository.JpaRepository;  
  
public interface PostsRepository extends JpaRepository<Posts, Long>{  
  
}
```

### JPA 테스트 코드

1. 테스트용 데이터 insert
2. 데이터 조회하여 값 비교

```java
import org.junit.After;  
import org.junit.Test;  
import org.junit.runner.RunWith;  
import org.springframework.beans.factory.annotation.Autowired;  
import org.springframework.boot.test.context.SpringBootTest;  
import org.springframework.test.context.junit4.SpringRunner;  
  
import java.util.List;  
  
import static org.assertj.core.api.Assertions.assertThat;  
  
@RunWith(SpringRunner.class)  
@SpringBootTest  
public class PostsRepositoryTest {  
    @Autowired  
    PostsRepository postsRepository;  
  
  @After // Junit에서 단위 테스트가 끝날 때마다 수행되는 메소드 지정  
  // 보통은 배포 전 전체 테스트를 수행할 때 테스트간 데이터 침범을 막기 위함  
  // ex) 여러 테스트를 동시에 수행하면, 테스트용 데이터가 남아있어 영향을 줄 수 있음  
  public void cleanup(){  
        postsRepository.deleteAll();  
  }  
  
    @Test  
    public void 게시글저장_불러오기(){  
        //given  
  String title = "테스트게시글";  
  String content = "테스트본문";  
  
  // posts테이블에 insert/update 실행  
  // id가 있으면 update, 없으면 insert  postsRepository.save(Posts.builder()  
                .title(title)  
                .content(content)  
                .author("eunji@gmail.com")  
                .build());  
  
  //when  
  List<Posts> postsList = postsRepository.findAll(); // posts테이블에 있는 모든 데이터 조회  
  
  //then  
  Posts posts = postsList.get(0);  
  assertThat(posts.getTitle()).isEqualTo(title);  
  assertThat(posts.getContent()).isEqualTo(content);  
  }  
}
```

### JPA실행결과 확인방법

/src/main/resources 경로에 application.properties 파일을 생성하고 아래 코드를 추가
![jpa실행결과_설정](https://github.com/smeil123/CS_Study/blob/master/image/jpa실행결과_설정.PNG)

mysql 쿼리문 형식으로 결과를 조회하고 싶으면, 아래 코드 한 줄 더 추가
```
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL5InnoDBDialect
```


하고, JPA테스트 결과를 실행하면 아래와 같이 JPA로 실행된 SQL을 볼 수 있다
![jpa실행결과](https://github.com/smeil123/CS_Study/blob/master/image/jpa실행결과.PNG)
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTk4OTQzMjEwNSwtMTUwMDMyODE5OCwxNj
kzMDg2MjM0LC0yMDgwMDU4MTAzLDEzODE5MTU3OTJdfQ==
-->