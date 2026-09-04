---
title: returning to childhood mode
date: 2026-09-04
---

line by line, one exercise at a time
joy is in the details.

```c
#include <stdio.h>
#include <limits.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 2-8: rightrot(x,n) returns x rotated right by n bit
//positions; bits that fall off the low end wrap around to become the
//new high bits (a circular rotation -- no bits are lost, unlike a
//plain shift). width is derived from sizeof(x)*CHAR_BIT rather than
//hardcoded, so this works whatever the actual width of unsigned is on
//a given machine. presumably n is in [0, width); n == 0 is handled
//explicitly since shifting by the full width would otherwise be
//undefined behavior.

//print_bits: print the low nbits bits of x, most significant bit first
void print_bits(unsigned x, int nbits)
{
    int i;
    for (i = nbits - 1; i >= 0; i--)
        putchar((x & (1u << i)) ? '1' : '0');
}

unsigned rightrot(unsigned x, int n)
{
    int bits = (int) sizeof(x) * CHAR_BIT;   //width of unsigned on this machine

    n %= bits;   //rotating by the full width (or a multiple of it) is a no-op
    if (n == 0)  //n == 0 would make x << bits below undefined behavior
        return x;

    return (x >> n) | (x << (bits - n));
}

int main(void)
{
    unsigned x = 0x6A;
    int bits = (int) sizeof(x) * CHAR_BIT;

    printf("             x = "); print_bits(x, bits); printf("   (0x%X)\n", x);
    printf("      --------------\n");

    printf("rightrot(x, 1) = "); print_bits(rightrot(x, 1), bits);
    printf("   -- bit 0 wraps around to become the top bit\n");

    printf("rightrot(x, 3) = "); print_bits(rightrot(x, 3), bits);
    printf("   -- lowest 3 bits wrap around to become the top 3 bits\n");

    printf("rightrot(x, bits) = "); print_bits(rightrot(x, bits), bits);
    printf("   -- rotating by the full width is a no-op\n");

    return 0;
}
```
the answer: 
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
             x = 00000000000000000000000001101010   (0x6A)
      --------------
rightrot(x, 1) = 00000000000000000000000000110101   -- bit 0 wraps around to become the top bit
rightrot(x, 3) = 01000000000000000000000000001101   -- lowest 3 bits wrap around to become the top 3 bits
rightrot(x, bits) = 00000000000000000000000001101010   -- rotating by the full width is a no-op
