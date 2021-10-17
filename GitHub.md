## 간단한 깃헙 사용법

```
git init
git remote add origin url
git add .
git commit -m "comment"
git push origin master

git status # 저장소에 파일이 추가되었는지 확인
```

* commit : 파일을 추가하거나 변경 내용을 저장소에 저장하는 작업
* push : 파일을 추가하거나 변경 내용을 원격 저장소에 업로드하는 작업
> 저장소는 원격 저장소(github), 로컬저장소(내 컴퓨터)가 있다.

## branch 사용
```
git branch # 현재 브랜치

git branch other # other라는 브랜치 생성
git checkout other # other 브랜치로 이동
git checkout -b other2 # 위 2개를 합친거

git push origin branch명 # 이렇게 푸쉬해야한다
```

### branch merge
```
git checkout master # 합치고자하는 머리로 올라가기(master)
git merge other
git push origin master
```

### 브랜치 삭제
```
git branch -d other
```

### 그 이외
```
git log # 로컬 저장소의 커밋 히스토리 확인
git grep # 저장소의 파일 내용 검색
git clone # 원격 저장소를 로컬에 다운로드
git reset # 로컬 저장소 커밋 취소
```
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTMxODQzNTkyNF19
-->