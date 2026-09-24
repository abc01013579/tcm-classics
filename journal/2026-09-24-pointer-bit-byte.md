---
title: pointer & bit byte
date: 2026-09-24
---

```c
#include <stdio.h>

int main() {
    printf("char 占用 %zu 字节 = %zu 位\n", sizeof(char), sizeof(char) * 8);
    printf("int 占用 %zu 字节 = %zu 位\n", sizeof(int), sizeof(int) * 8);
    printf("指针 占用 %zu 字节 = %zu 位\n", sizeof(int*), sizeof(int*) * 8);
    return 0;
}

win@DESKTOP-MEIH88T:~$ cd webdev-projects
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra ccc-c.c -o ccc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./ccc-c
char 占用 1 字节 = 8 位
int 占用 4 字节 = 32 位
指针 占用 8 字节 = 64 位
```
