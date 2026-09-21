---
title: things get complicated
date: 2026-09-21
---

```c
#include <stdio.h>
#include <string.h>   //only for the reference strncpy/strncat/strncmp and memset in main
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 5-5: write versions of the library functions strncpy,
//strncat, and strncmp, which operate on at most the first n characters
//of their argument strings. (Appendix B has the full descriptions.)
//
//The three behaviors that are easy to get wrong -- all taken from
//Appendix B, and all checked against the real library in main():
//
//  strncpy(s, ct, n)  copies at most n characters of ct to s, and PADS
//                     s with '\0' out to n characters if ct is shorter.
//                     If ct has n or more characters it does NOT
//                     terminate s -- a famous trap, kept on purpose.
//  strncat(s, ct, n)  appends at most n characters of ct to s and ALWAYS
//                     terminates s with '\0' (so it may write n+1 bytes
//                     past the old end -- unlike strncpy).
//  strncmp(cs, ct, n) compares at most n characters, stops early at a
//                     '\0', and compares as UNSIGNED chars, so a byte
//                     like 0xe9 sorts above 'a' even where plain char
//                     is signed (checked by the last test case).
//
//Every loop is driven by the pointers and the countdown n -- no indices.
//Each function takes const char * for the source it only reads, so the
//compiler stops it from ever writing through that pointer.
char *my_strncpy(char *s, const char *ct, size_t n)
{
    char *start = s;       //s itself will move; remember where it began

    while (n > 0 && *ct) { //copy real characters
        *s++ = *ct++;
        n--;
    }
    while (n > 0) {        //ct ran out first: pad with '\0'
        *s++ = '\0';
        n--;
    }
    return start;
}

char *my_strncat(char *s, const char *ct, size_t n)
{
    char *start = s;

    while (*s)             //find end of s
        s++;
    while (n > 0 && *ct) { //append at most n characters
        *s++ = *ct++;
        n--;
    }
    *s = '\0';             //always terminate, even when n == 0
    return start;
}

int my_strncmp(const char *cs, const char *ct, size_t n)
{
    for (; n > 0; cs++, ct++, n--) {
        if ((unsigned char)*cs != (unsigned char)*ct)
            return (unsigned char)*cs - (unsigned char)*ct;
        if (*cs == '\0')   //both ended together, equal so far
            return 0;
    }
    return 0;              //n characters compared, all equal (or n == 0)
}

static void show(const char *b, int len)   //'\0' shown as '.' so padding is visible
{
    int i;

    putchar('[');
    for (i = 0; i < len; i++)
        putchar(b[i] ? b[i] : '.');
    putchar(']');
}

static int sign(int x)
{
    return (x > 0) - (x < 0);
}

int main(void)
{
    size_t ns[] = {0, 3, 5, 8};
    int nn = sizeof(ns) / sizeof(ns[0]);
    int i;

    printf("--- strncpy(s, \"hello\", n) into a buffer pre-filled with X ---\n");
    for (i = 0; i < nn; i++) {
        char mine[12], lib[12];
        char *r;

        memset(mine, 'X', sizeof(mine));
        memset(lib, 'X', sizeof(lib));
        r = my_strncpy(mine, "hello", ns[i]);
        strncpy(lib, "hello", ns[i]);
        printf("n=%zu  ", ns[i]);
        show(mine, 12);
        printf("  %s\n", (r == mine && memcmp(mine, lib, 12) == 0) ? "ok" : "FAIL");
    }

    printf("\n--- strncat(\"ab\", \"cdefgh\", n) ---\n");
    for (i = 0; i < nn; i++) {
        char mine[20] = "ab";
        char lib[20] = "ab";
        char *r;

        r = my_strncat(mine, "cdefgh", ns[i]);
        strncat(lib, "cdefgh", ns[i]);
        printf("n=%zu  ", ns[i]);
        show(mine, 12);
        printf("  %s\n", (r == mine && memcmp(mine, lib, 20) == 0) ? "ok" : "FAIL");
    }

    printf("\n--- strncmp(a, b, n): sign of result, mine vs library ---\n");
    {
        char *a[] = {"abc", "abc", "abc", "", "abc", "a", "\xe9"};
        char *b[] = {"abd", "abd", "ab",  "", "abc", "b", "a"};
        size_t cn[] = {2,     3,     3,    5,  100,   0,   1};
        int nc = sizeof(cn) / sizeof(cn[0]);

        for (i = 0; i < nc; i++) {
            int m = sign(my_strncmp(a[i], b[i], cn[i]));
            int l = sign(strncmp(a[i], b[i], cn[i]));

            printf("n=%-3zu mine=%2d lib=%2d  %s\n", cn[i], m, l, m == l ? "ok" : "FAIL");
        }
    }

    return 0;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
--- strncpy(s, "hello", n) into a buffer pre-filled with X ---
n=0  [XXXXXXXXXXXX]  ok
n=3  [helXXXXXXXXX]  ok
n=5  [helloXXXXXXX]  ok
n=8  [hello...XXXX]  ok

--- strncat("ab", "cdefgh", n) ---
n=0  [ab..........]  ok
n=3  [abcde.......]  ok
n=5  [abcdefg.....]  ok
n=8  [abcdefgh....]  ok

--- strncmp(a, b, n): sign of result, mine vs library ---
n=2   mine= 0 lib= 0  ok
n=3   mine=-1 lib=-1  ok
n=3   mine= 1 lib= 1  ok
n=5   mine= 0 lib= 0  ok
n=100 mine= 0 lib= 0  ok
n=0   mine= 0 lib= 0  ok
n=1   mine= 1 lib= 1  ok
```
