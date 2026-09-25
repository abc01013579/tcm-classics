---
title: printbits
date: 2026-09-25
---

```c
#include <stdio.h>
#include <limits.h>

void printbits(unsigned x, int n)
{
    for (int i = n - 1; i >= 0; i--) {
        putchar((x >> i) & 1 ? '1' : '0');
        if (i % 4 == 0 && i) putchar(' ');   /* space between nibbles */
    }
    putchar('\n');
}

int main(void)
{
    printf("CHAR_BIT        = %d\n", CHAR_BIT);
    printf("sizeof(int)     = %zu bytes = %zu bits\n", sizeof(int), sizeof(int) * CHAR_BIT);
    printf("UINT_MAX        = %u\n", UINT_MAX);

    printf("'7' as int      = %d, '7' - '0' = %d\n", '7', '7' - '0');

    printf("214             = "); printbits(214, 8);
    printf("-1 (8 bits)     = "); printbits((unsigned char)-1, 8);

    int x = 0x12345678;
    unsigned char *p = (unsigned char *)&x;
    printf("0x12345678 bytes in memory: %02x %02x %02x %02x\n", p[0], p[1], p[2], p[3]);
    return 0;

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra ccc-c.c -o ccc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./ccc-c
CHAR_BIT        = 8
sizeof(int)     = 4 bytes = 32 bits
UINT_MAX        = 4294967295
'7' as int      = 55, '7' - '0' = 7
214             = 1101 0110
-1 (8 bits)     = 1111 1111
0x12345678 bytes in memory: 78 56 34 12
```
