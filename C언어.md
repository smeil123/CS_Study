


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

### realloc

### free
힙 영역에 할당된 메모리를 해제하는 함수
```c
#include <stdilb.h>
void free(void* ptr)

int *arr;
arr = (int*) malloc(sizeof(int)*
```
<!--stackedit_data:
eyJoaXN0b3J5IjpbOTk0Nzc3M119
-->