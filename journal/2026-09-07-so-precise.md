---
title: so precise
date: 2026-09-07
---

```c

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 2-10: rewrite lower(), which converts uppercase letters to
//lowercase, using a conditional expression instead of if/else -- both
//branches just produce a value to return, so the whole function body
//collapses to one expression
int lower(int c)
{
    return (c >= 'A' && c <= 'Z') ? c + 'a' - 'A' : c;
}

int main(void)
{
    printf("lower('A') = %c\n", lower('A'));
    printf("lower('Z') = %c\n", lower('Z'));
    printf("lower('a') = %c\n", lower('a'));
    printf("lower('5') = %c\n", lower('5'));
    printf("lower('!') = %c\n", lower('!'));

    return 0;
}


```win@DESKTOP-MEIH88T:~/webdev-projects$  gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
lower('A') = a
lower('Z') = z
lower('a') = a
lower('5') = 5
lower('!') = !
