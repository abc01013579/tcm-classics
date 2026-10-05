---
title: arrays of structures
date: 2026-10-05
---

```c
#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace()
#include <string.h>     //for strcmp()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c < cc-c.c
//         or:  printf 'int main(void)\n{\n    int i;\n    for (i = 0; i < 10; i++)\n        if (i > 5)\n            break;\n    return 0;\n}\n' | ./cc-c

//K&R2 section 6.3: arrays of structures -- count C keywords.
//
//The book's listing on p.134 leaves out the pieces it showed just
//before and after it; they're filled in here so the block compiles:
//  - struct key and the keytab[] initializer (p.133). The book lists
//    only "auto", "break", ... "while"; here it's all 32 C89 keywords.
//    The table MUST stay in alphabetical order -- binsearch depends on it.
//  - NKEYS, computed by the compiler from the table's size (p.135), so
//    adding a keyword never needs a count updated by hand.
//  - getword (p.136) and getch/ungetch (section 4.3).
//
//Note: the binsearch prototype mentions struct key, so struct key must
//be declared ABOVE it -- the book's order on p.134 assumes p.133 came
//first.
//
//getword doesn't skip string constants or comments (that's exercise
//6-1), so a keyword inside "..." or after // still gets counted.
#define MAXWORD 100

struct key {
    char *word;
    int count;
} keytab[] = {
    { "auto", 0 },
    { "break", 0 },
    { "case", 0 },
    { "char", 0 },
    { "const", 0 },
    { "continue", 0 },
    { "default", 0 },
    { "do", 0 },
    { "double", 0 },
    { "else", 0 },
    { "enum", 0 },
    { "extern", 0 },
    { "float", 0 },
    { "for", 0 },
    { "goto", 0 },
    { "if", 0 },
    { "int", 0 },
    { "long", 0 },
    { "register", 0 },
    { "return", 0 },
    { "short", 0 },
    { "signed", 0 },
    { "sizeof", 0 },
    { "static", 0 },
    { "struct", 0 },
    { "switch", 0 },
    { "typedef", 0 },
    { "union", 0 },
    { "unsigned", 0 },
    { "void", 0 },
    { "volatile", 0 },
    { "while", 0 }
};

#define NKEYS (sizeof keytab / sizeof keytab[0])

int getword(char *, int);
int binsearch(char *, struct key *, int);

//count C keywords
int main(void)
{
    int n;
    char word[MAXWORD];

    while (getword(word, MAXWORD) != EOF)
        if (isalpha(word[0]))
            if ((n = binsearch(word, keytab, NKEYS)) >= 0)
                keytab[n].count++;
    for (n = 0; n < (int) NKEYS; n++)
        if (keytab[n].count > 0)
            printf("%4d %s\n",
                keytab[n].count, keytab[n].word);
    return 0;
}

//binsearch:  find word in tab[0]...tab[n-1]
int binsearch(char *word, struct key tab[], int n)
{
    int cond;
    int low, high, mid;

    low = 0;
    high = n - 1;
    while (low <= high) {
        mid = (low+high) / 2;
        if ((cond = strcmp(word, tab[mid].word)) < 0)
            high = mid - 1;
        else if (cond > 0)
            low = mid + 1;
        else
            return mid;
    }
    return -1;
}

int getch(void);
void ungetch(int);

//getword:  get next word or character from input
int getword(char *word, int lim)
{
    int c;
    char *w = word;

    while (isspace(c = getch()))
        ;
    if (c != EOF)
        *w++ = c;
    if (!isalpha(c)) {
        *w = '\0';
        return c;
    }
    for ( ; --lim > 0; w++)
        if (!isalnum(*w = getch())) {
            ungetch(*w);
            break;
        }
    *w = '\0';
    return word[0];
}

#define BUFSIZE 100

char buf[BUFSIZE];      //buffer for ungetch
int bufp = 0;           //next free position in buf

//getch:  get a (possibly pushed back) character
int getch(void)
{
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

win@DESKTOP-MEIH88T:~$ cd webdev-projects
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c < cc-c.c
   2 auto
 120 break
 141 case
 568 char
  40 const
  14 continue
  30 default
  18 do
  93 double
 326 else
  11 enum
  11 extern
  32 float
 363 for
   1 goto
 740 if
1137 int
  50 long
   1 register
 512 return
  12 short
  28 signed
  67 sizeof
  46 static
  22 struct
  26 switch
   4 typedef
   5 union
 116 unsigned
 460 void
   4 volatile
 203 while
```
