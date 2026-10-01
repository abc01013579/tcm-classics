---
title: dcl--complicated declarations
date: 2026-10-01
---

```c
#include <stdio.h>
#include <string.h>     //for strcpy(), strcat()
#include <ctype.h>      //for isalpha(), isalnum()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'char **argv\n' | ./cc-c                   # argv:  pointer to pointer to char
//         or:  printf 'int (*daytab)[13]\n' | ./cc-c             # daytab:  pointer to array[13] of int
//         or:  printf 'int *daytab[13]\n' | ./cc-c               # daytab:  array[13] of pointer to int
//         or:  printf 'void (*comp)()\n' | ./cc-c                # comp:  pointer to function returning void
//         or:  printf 'char (*(*x())[])()\n' | ./cc-c            # x:  function returning pointer to array[] of pointer to function returning char
//         or:  printf 'char (*(*x[3])())[5]\n' | ./cc-c          # x:  array[3] of pointer to function returning pointer to array[5] of char

//K&R2 section 5.12: complicated declarations. dcl reads a C
//declaration and says it in words:
//
//    char (*(*x())[])()   ->   x: function returning pointer to array[]
//                              of pointer to function returning char
//
//The grammar it follows (from the book):
//
//    dcl:     optional *'s  direct-dcl
//    direct-dcl:  name
//                 ( dcl )
//                 direct-dcl ()
//                 direct-dcl [optional size]
//
//In words: a declarator is some *'s in front of a direct declarator;
//a direct declarator is a name, or a whole declarator in parentheses,
//followed by any number of () and [] suffixes.
//
//dcl and dirdcl call EACH OTHER -- dcl calls dirdcl, and dirdcl calls
//dcl again when it meets "(". This is "recursive descent": one
//function per grammar rule, and the program's call stack mirrors the
//nesting of parentheses in the declaration.
//
//Why the words come out in the right order: dcl COUNTS its *'s first,
//lets dirdcl handle everything to the right (name, (), []), and only
//then appends " pointer to" once per *. So in *x[3], "array[3] of"
//is written before "pointer to" -- matching C's rule that [] and ()
//bind tighter than *.
//
//The book's own warnings (from the Chinese edition's text): dcl is
//deliberately simple. It handles only simple data types like char or
//int -- not argument types inside (), and not qualifiers like const.
//Unneeded blanks confuse it, and it has no error recovery, so an
//invalid declaration can throw it off. Fixing these is left to the
//exercises (5-18 to 5-20).
//
//Fixed from the book's text: main() -> int main(void). gcc 15 defaults
//to C23, which no longer allows a function without a return type.
#define MAXTOKEN 100

enum { NAME, PARENS, BRACKETS };

void dcl(void);
void dirdcl(void);
int gettoken(void);

int tokentype;              //type of last token
char token[MAXTOKEN];       //last token string
char name[MAXTOKEN];        //identifier name
char datatype[MAXTOKEN];    //data type = char, int, etc.
char out[1000];

//convert declaration to words
int main(void)
{
    while (gettoken() != EOF) {     //1st token on line
        strcpy(datatype, token);    //is the datatype
        out[0] = '\0';
        dcl();                      //parse rest of line
        if (tokentype != '\n')
            printf("syntax error\n");
        printf("%s: %s %s\n", name, out, datatype);
    }
    return 0;
}

//dcl:  parse a declarator
void dcl(void)
{
    int ns;

    for (ns = 0; gettoken() == '*'; )   //count *'s
        ns++;
    dirdcl();
    while (ns-- > 0)
        strcat(out, " pointer to");
}

//dirdcl:  parse a direct declarator
void dirdcl(void)
{
    int type;

    if (tokentype == '(') {             //( dcl )
        dcl();
        if (tokentype != ')')
            printf("error: missing )\n");
    } else if (tokentype == NAME)       //variable name
        strcpy(name, token);
    else
        printf("error: expected name or (dcl)\n");
    while ((type=gettoken()) == PARENS || type == BRACKETS)
        if (type == PARENS)
            strcat(out, " function returning");
        else {
            strcat(out, " array");
            strcat(out, token);
            strcat(out, " of");
        }
}

//gettoken:  return next token
int gettoken(void)
{
    int c, getch(void);
    void ungetch(int);
    char *p = token;

    while ((c = getch()) == ' ' || c == '\t')
        ;
    if (c == '(') {
        if ((c = getch()) == ')') {
            strcpy(token, "()");
            return tokentype = PARENS;
        } else {
            ungetch(c);
            return tokentype = '(';
        }
    } else if (c == '[') {
        for (*p++ = c; (*p++ = getch()) != ']'; )
            ;
        *p = '\0';
        return tokentype = BRACKETS;
    } else if (isalpha(c)) {
        for (*p++ = c; isalnum(c = getch()); )
            *p++ = c;
        *p = '\0';
        ungetch(c);
        return tokentype = NAME;
    } else
        return tokentype = c;
}

//--- from section 4.3 ---

#define BUFSIZE 100

char buf[BUFSIZE];          //buffer for ungetch
int bufp = 0;               //next free position in buf

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

```

win@DESKTOP-MEIH88T:~$ cd webdev-projects
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'char **argv\n' | ./cc-c
argv:  pointer to pointer to char
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'int (*daytab)[13]\n' | ./cc-c
daytab:  pointer to array[13] of int
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'int *daytab[13]\n' | ./cc-c
daytab:  array[13] of pointer to int
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'void (*comp)()\n' | ./cc-c
comp:  pointer to function returning void
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'char (*(*x())[])()\n' | ./cc-c
x:  function returning pointer to array[] of pointer to function returning char
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'char (*(*x[3])())[5]\n' | ./cc-c
x:  array[3] of pointer to function returning pointer to array[5] of char
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'int x)\n' | ./cc-c
syntax error
x:  int
error: expected name or (dcl)
syntax error
x:  x

You can also read declarations by hand with the right-left rule. Start at the name, go right while you can, go left when you hit ), and repeat:

```c
char (*(*x[3])())[5]
            x            x is
             [3]         array[3] of
          *              pointer to
               ()        function returning
        *                pointer to
                  [5]    array[5] of
char                     char
```
That's the same order dcl produces, because dcl is this rule written as code.

char **argv
 argv: pointer to char
int (*daytab)[13]
 daytab: pointer to array[13] of int
int *daytab[13]
 daytab: array[13] of pointer to int
void *comp()
 comp: function returning pointer to void
void (*comp)()
 comp: pointer to function returning void
char (*(*x())[])()
 x: function returning pointer to array[] of
 pointer to function returning char
char (*(*x[3])())[5]
 x: array[3] of pointer to function returning
 pointer to arra
