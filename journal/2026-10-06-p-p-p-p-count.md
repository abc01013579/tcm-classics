---
title: p *p &p p->count
date: 2026-10-06
---

```c
#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace()
#include <string.h>     //for strcmp()

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
struct key *binsearch(char *, struct key *, int);

//count C keywords; pointer version
int main(void)
{
    char word[MAXWORD];
    struct key *p;

    while (getword(word, MAXWORD) != EOF)
        if (isalpha(word[0]))
            if ((p = binsearch(word, keytab, NKEYS)) != NULL)
                p->count++;
    for (p = keytab; p < keytab + NKEYS; p++)
        if (p->count > 0)
            printf("%4d %s\n", p->count, p->word);
    return 0;
}

//binsearch:  find word in tab[0]...tab[n-1]
struct key *binsearch(char *word, struct key *tab, int n)
{
    int cond;
    struct key *low = &tab[0];
    struct key *high = &tab[n];
    struct key *mid;

    while (low < high) {
        mid = low + (high-low) / 2;
        if ((cond = strcmp(word, mid->word)) < 0)
            high = mid;
        else if (cond > 0)
            low = mid + 1;
        else
            return mid;
    }
    return NULL;
}

The three forms you saw in GDB, p, *p and &p, mean three different things. These are real values from your program, stopped at line 93:

Expression	GDB shows	Meaning	Size
p	0x555555558110 <keytab+240>	an address: where the row is	8 bytes
*p	{word = "if", count = 0}	the row itself, at that address	16 bytes
&p	0x7fffffffdcd8	where p itself is stored	—
p->count	0	one member of the row: (*p).count	4 bytes

 &p = 0x7fffffffdcd8                 p = 0x…8110
 ┌──────────────────┐               ┌──────────────┬─────────┐
 │ p:  0x…8110  ────┼─────────────► │ word → "if"  │ count 0 │   ← this is *p
 └──────────────────┘               └──────────────┴─────────┘
  p's own box (8 bytes,              keytab[15] (16 bytes,
  among main's local variables)      in the global table)

p is what's written inside the small box: just a number, an address.
*p means "go to that address": the big box at the other end of the arrow.
&p is the address of the small box itself. p is a variable too, so it lives somewhere in memory.

The same * symbol does two jobs, depending on where it appears:

In a declaration, struct key *p; says "p is a pointer to a struct key".
In an expression, *p says "follow p to what it points at".
```
