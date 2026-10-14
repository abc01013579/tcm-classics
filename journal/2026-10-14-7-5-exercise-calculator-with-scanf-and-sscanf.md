---
title: 7-5 exercise calculator with scanf and sscanf
date: 2026-10-14
---

```c
#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf '1 2 - 4 5 + *\n3.5e2 10 /\n-3 4 +\n' | ./cc-c
//              ./cc-c        # interactive: type "2 3 +" and Enter

//K&R2 exercise 7-5: the chapter 4 postfix calculator, with scanf and
//sscanf doing the input and number conversion. Chapter 4's getop read
//one character at a time with getch/ungetch, decided by hand where a
//number ended, and main called atof. Here:
//  scanf  splits the input into tokens (and notices the newlines)
//  sscanf decides whether a token is a number, and converts it
//So getch, ungetch, the buffer between them, and atof are all gone.

#define MAXOP   100     //max size of operand or operator
#define NUMBER  '0'     //signal that a number was found
#define MAXVAL  100     //maximum depth of val stack

int getop(char s[], double *num);
void push(double f);
double pop(void);

//reverse Polish calculator
int main(void)
{
    int type;
    double op2, num;
    char s[MAXOP];

    while ((type = getop(s, &num)) != EOF) {
        switch (type) {
        case NUMBER:
            push(num);
            break;
        case '+':
            push(pop() + pop());
            break;
        case '*':
            push(pop() * pop());
            break;
        case '-':
            op2 = pop();
            push(pop() - op2);
            break;
        case '/':
            op2 = pop();
            if (op2 != 0.0)
                push(pop() / op2);
            else
                printf("error: zero divisor\n");
            break;
        case '\n':
            printf("\t%.8g\n", pop());
            break;
        default:
            printf("error: unknown command %s\n", s);
            break;
        }
    }
    return 0;
}

//getop:  get next operator or numeric operand; a number's value goes
//into *num. Returns NUMBER, the operator character, '\n', or EOF.
int getop(char s[], double *num)
{
    char c;
    int n;

    //%*[ \t] -- skip blanks and tabs, but NOT newlines: '\n' is a command
    //here ("print the result"), so it must reach main. A plain " " or
    //"%s" in the format would swallow it as just more whitespace.
    //The * means "match but don't store", so no argument is needed.
    scanf("%*[ \t]");

    if (scanf("%c", &c) != 1)           //%c reads ANY char, '\n' included
        return EOF;
    if (c == '\n')
        return '\n';
    ungetc(c, stdin);                   //part of a token: give it back

    //%99[^ \t\n] -- read everything up to the next blank, tab or newline.
    //The width must be written into the format itself: in scanf, * means
    //"suppress", not "width from an argument" as it does in printf.
    //99 = MAXOP - 1, leaving room for the '\0'
    scanf("%99[^ \t\n]", s);

    //IDIOM: sscanf(s, "%lf%n", ...) -- %n stores how many characters were
    //consumed so far. The token is a number only if the conversion worked
    //AND it used up the whole token: "12" yes, "12abc" no.
    //"-" and "+" alone fail the conversion, so they fall through as
    //operators, while "-3" converts as a negative number
    if (sscanf(s, "%lf%n", num, &n) == 1 && s[n] == '\0')
        return NUMBER;
    if (s[1] == '\0')                   //a single character: an operator
        return s[0];
    return '?';                         //anything else: unknown command
}

int sp = 0;           //next free stack position
double val[MAXVAL];   //value stack

//push:  push f onto value stack
void push(double f)
{
    if (sp < MAXVAL)
        val[sp++] = f;
    else
        printf("error: stack full, can't push %g\n", f);
}

//pop:  pop and return top value from stack
double pop(void)
{
    if (sp > 0)
        return val[--sp];
    else {
        printf("error: stack empty\n");
        return 0.0;
    }
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ printf '1 2 - 4 5 + *\n3.5e2 10 /\n-3 4 +\n' | ./cc-c
        -9
        35
        1
win@DESKTOP-MEIH88T:~/webdev-projects$  ./cc-c
2 3 +
        5
```
