---
title: 7-4 exercise  minscanf
date: 2026-10-14
---

```c
#include <stdio.h>
#include <stdarg.h>     //va_list, va_start, va_arg, va_end
#include <ctype.h>      //isspace, isdigit
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf '14/10/2026 TSM 186.5\n15/10/2026 BRK 471.25\n' | ./cc-c
//              printf '14-10-2026 TSM 186.5\n' | ./cc-c    # mismatch at '-'
//              ./cc-c < /dev/null                          # EOF right away

//K&R2 exercise 7-4: minscanf, a private scanf analogous to minprintf.
//Same trick as exercise 7-3: each %-spec is copied into a small local
//format string and handed to the real scanf with ONE argument, fetched
//with va_arg. Everything between specs is handled here, by hand:
//whitespace in fmt skips any amount of whitespace in the input, and
//any other character must match the next input character exactly.
//
//Handled: width (%19s), the l modifier, conversions d i o u x c s e f g,
//and %% for a literal percent. Not handled: %*d (assignment suppression).
//Returns the number of items assigned, or EOF if input ended first.
//
//The key difference from minprintf: every argument is a POINTER.
//scanf has to store into the caller's variables, and C passes by value,
//so the caller sends addresses. Pointers are not promoted, so here
//%f means float * and %lf means double * -- unlike printf, where a
//float has already become a double by the time it arrives.

#define LOCALFMT 100    //room for one conversion spec

int minscanf(char *fmt, ...);

int main(void)
{
    int day, month, year, n;
    char ticker[20];
    double price;

    while ((n = minscanf("%d/%d/%d %19s %lf",
                         &day, &month, &year, ticker, &price)) == 5)
        printf("%04d-%02d-%02d  %-5s %8.2f\n", year, month, day, ticker, price);
    printf("minscanf returned %d\n", n);
    return 0;
}

//minscanf: minimal scanf with variable argument list
int minscanf(char *fmt, ...)
{
    va_list ap;                         //points to each unnamed arg in turn
    char *p;
    char localfmt[LOCALFMT];
    int c, i, n;
    int islong;
    int nassigned = 0;

    va_start(ap, fmt);                  //make ap point to 1st unnamed arg
    for (p = fmt; *p; p++) {
        if (isspace(*p)) {              //whitespace: skip any amount of it
            while (isspace(c = getchar()))
                ;
            ungetc(c, stdin);           //one too far: push it back
            continue;
        }
        if (*p != '%' || *(p+1) == '%') {   //a literal: must match exactly
            if (*p == '%')
                p++;                    //"%%" matches a single '%'
            if ((c = getchar()) != *p) {
                if (c == EOF && nassigned == 0)
                    nassigned = EOF;
                ungetc(c, stdin);       //leave the mismatch for the caller
                break;
            }
            continue;
        }

        i = 0;
        localfmt[i++] = '%';
        while (isdigit(*(p+1)) && i < LOCALFMT - 4)    //width
            localfmt[i++] = *++p;
        islong = 0;
        if (*(p+1) == 'l') {
            localfmt[i++] = *++p;
            islong = 1;
        }
        localfmt[i++] = *++p;           //the conversion character
        localfmt[i] = '\0';
        if (*p == '\0')                 //fmt ended inside a spec
            break;

        //each group: conversions that store into this pointer type
        switch (*p) {
        case 'd': case 'i':
            if (islong)
                n = scanf(localfmt, va_arg(ap, long *));
            else
                n = scanf(localfmt, va_arg(ap, int *));
            break;
        case 'o': case 'u': case 'x':
            if (islong)
                n = scanf(localfmt, va_arg(ap, unsigned long *));
            else
                n = scanf(localfmt, va_arg(ap, unsigned int *));
            break;
        case 'e': case 'f': case 'g':
            if (islong)
                n = scanf(localfmt, va_arg(ap, double *));
            else
                n = scanf(localfmt, va_arg(ap, float *));
            break;
        case 'c': case 's':
            n = scanf(localfmt, va_arg(ap, char *));
            break;
        default:                        //unknown conversion: stop
            n = 0;
            break;
        }
        //scanf returns 1 if it stored the item, 0 on a mismatch, EOF if
        //input ended before anything was read
        if (n != 1) {
            if (n == EOF && nassigned == 0)
                nassigned = EOF;
            break;
        }
        nassigned++;
    }
    va_end(ap);                         //clean up when done
    return nassigned;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ printf '14/10/2026 TSM 186.5\n15/10/2026 BRK 471.25\n' | ./cc-c
2026-10-14  TSM     186.50
2026-10-15  BRK     471.25
minscanf returned -1
win@DESKTOP-MEIH88T:~/webdev-projects$ printf '14-10-2026 TSM 186.5\n' | ./cc-c
minscanf returned 1
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c < /dev/null
minscanf returned -1
win@DESKTOP-MEIH88T:~/webdev-projects$ printf '14/10/2026 TSM \n' | ./cc-c
minscanf returned 4
```
