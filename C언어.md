

## 포인터 배열, 배열 포인터
### 포인터 배열
* 포인터들의 배열이다
* 배열의 요소가 포인터들로 이루어져있다.
```c
char* arr[3];
arr[0] = "ASDF";
arr[1] = "QWER";
arr[2] = "ZXCV";

for(int i=0; i<3; i++){
	printf("%s\n", arr[i]);
}
```
```
ASDF
QWER
ZXCV
```

* arr는 char포인터를 담는다. 
* arr -> [ char *, char*, char* ]
* arr[0] == char* -> "ASDF"

### 배열 포인터
* 배열을 가리키는 포인터
* 특정 사이즈의 배열만 가리킬 수 있는 포인터이다

```c
char (*arr)[3];
char tmp1[3] = {'a','b','c'};
char tmp2[3] = {'d','e','\0'}; //문자열의 끝을 알리는 '\0'추ㅏ

arr = &tmp1;
printf("%s\n", (*arr)); //abc\335\227_\337
for(int i=0; i<(int)sizeof(*arr); i++)
{
	printf("%c",(*arr)[i]);
} // abc

arr = &tmp2;
printf("%s\n", (*arr)); // de
printf(

```

## 동적할당
### malloc
동적으로 메모리를 할당하는 함수(힙영역에 메모리 할당)
```c
#include <stdlib.h>
void* malloc(size_t size)

int *i = (int*) malloc (sizeof(int));
```
* malloc은 단순히 메모리만 할당하는 함수이기 때문에 어떤 void포인터를 반환해 형변환을 해주어야한다 -> (int *)

### calloc
malloc과 같은 기능이지만 형태가 조금 다르다 + 0으로 초기화해준다.
```c
#include <stdlilb.h>
void* calloc(size_t elt_count, size_t elt_size)

int * arr;
arr = (int*) calloc(5,sizeof(int));
```

### realloc
이미 할당된 공간의 크기를 바꿀 때 realloc함수를 사용한다.
```c
 #include <stdilb.h>
 void *realloc(void* memeblock, size_t size);
 int *arr;

 arr = (int*) malloc(sizeof(int)*5);
 realloc(arr, sizeof(int)*10); // 메모리를 40byte로 재할당
```

### free
힙 영역에 할당된 메모리를 해제하는 함수
```c
#include <stdilb.h>
void free(void* ptr)

int *arr;
arr = (int*) malloc(sizeof(int)*5);
free(arr);
```
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTkzMjExNjQ1NywtNTYwNDczNzc4LC0xOD
M3MzM3OTk4XX0=
-->