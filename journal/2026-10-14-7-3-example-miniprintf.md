---
title: 7.3 example miniprintf
date: 2026-10-14
---

```c
#include <stdio.h>
#include <stdarg.h>     //va_list, va_start, va_arg, va_end
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 section 7.3: minprintf -- a minimal printf with a variable
//argument list. The "..." in the declaration means "any number of
//further arguments, of any type"; stdarg.h is how a function walks them.

void minprintf(char *fmt, ...);

int main(void)
{
    minprintf("int: %d, double: %f, string: %s, percent: %%\n",
              42, 3.14, "hello");
    minprintf("no arguments at all\n");
    minprintf("%s is %d years old\n", "K&R2", 2026 - 1988);
    return 0;
}

//minprintf: minimal printf with variable argument list
void minprintf(char *fmt, ...)
{
    va_list ap;                         //points to each unnamed arg in turn
    char *p, *sval;
    int ival;
    double dval;

    va_start(ap, fmt);                  //make ap point to 1st unnamed arg
    for (p = fmt; *p; p++) {
        if (*p != '%') {
            putchar(*p);
            continue;
        }
        switch (*++p) {
        case 'd':
            ival = va_arg(ap, int);
            printf("%d", ival);
            break;
        case 'f':
            dval = va_arg(ap, double);
            printf("%f", dval);
            break;
        case 's':
            for (sval = va_arg(ap, char *); *sval; sval++)
                putchar(*sval);
            break;
        default:
            putchar(*p);
            break;
        }
    }
    va_end(ap);                         //clean up when done
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
int: 42, double: 3.140000, string: hello, percent: %
no arguments at all
K&R2 is 38 years old
```
