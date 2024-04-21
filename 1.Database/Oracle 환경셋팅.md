# Oracle 환경셋팅

- 환경 : MAC M1

오라클 설치 배포파일은 M1환경이 없어서 좀 셋팅이 까다롭다.

구글링을 통해서 여러 자료를 찾아보고 아래와 같이 구축한 히스토리를 정리한다.

1. Colima & Docker 설치

참고 사이트

- [https://velog.io/@devsaza/M1-M2-Mac-OS에서-Oracle-DB-사용하기](https://velog.io/@devsaza/M1-M2-Mac-OS%EC%97%90%EC%84%9C-Oracle-DB-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0)
- [https://velog.io/@dmdwns2/MacM1-limactl-is-running-under-rosetta-please-reinstall-lima-with-native-arch](https://velog.io/@dmdwns2/MacM1-limactl-is-running-under-rosetta-please-reinstall-lima-with-native-arch)

colima 를 설치해서 docker 엔진은 x86으로 실행시킬 환경을 세팅 해주고 다 설치가 되면 아래 단계를 수행하면 된다.

```bash
# colima 가상환경 띄우기
colima start --memory 8 --arch x86_64

# Docker oracle 이미지 내려받기
docker pull oracleinanutshell/oracle-xe-11g

# Docker 컨테이너 생성
docker run --name oracle -d -p 49160:22 -p 49161:1521 -v /Users/jang-eunji/oracle oracleinanutshell/oracle-xe-11g
## docker start oracle

# Oracle SQLPLUS 실행하기
docker exec -it oracle bash
> sqlplus
# 최초 계정 : system / oracle

# 혹은 원격지 sqlplus 접속
> sqlplus 계정/비밀번호@IP:1521/DB명

# 끄기
docker stop oracle
colima stop

```