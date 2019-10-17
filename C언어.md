


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
eyJoaXN0b3J5IjpbLTE2NDQwNDU3MjhdfQ==
-->