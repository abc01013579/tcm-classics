---
title: getch and ungetch
date: 2026-10-13
---

```c
#define BUFSIZE 100

char buf[BUFSIZE];      //buffer for ungetch
int bufp = 0;           //next free position in buf

//getch:  get a (possibly pushed back) character
int getch(void)
{
    //IDIOM: (n > 0) ? buf[--n] : getchar() -- take a pushed-back char first, else read a new one
    return (bufp > 0) ? buf[--bufp] : getchar();
}

//ungetch:  push character back on input
void ungetch(int c)
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters\n");
    else
        buf[bufp++] = c;
}

int getch(viod)
{
    if (bufp > 0)
         return buf[- -bufp];
    else
        return getchar();
}

buf[bufp++] = c

buf[bufp] = c;
bufp = bufp + 1; 


```
