---
title: printf("word: %s letters", *argv);
date: 2026-10-03
---

```c
#include <stdio.h>
//compile with: gcc -Wall -Wextra c-c.c -o c-c
//run with:     ./c-c -df -n hello        # word: -df  letters: d f | word: -n  letters: n | stopped at: hello

//Your two lines (unchanged), inside a main so they can run. The outer
//loop steps through the WORDS on the command line; the inner loop
//steps through the LETTERS of one word.

int main(int argc, char *argv[])
{
    int c;

    while (--argc > 0 && (*++argv)[0] == '-') {
        printf("word: %s  letters:", *argv);
        while((c = *++argv[0]))
            printf(" %c", c);
        printf("\n");
    }
    if (argc > 0)
        printf("stopped at: %s (doesn't start with -)\n", *argv);
        
    return 0;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ ./c-c -d -f -n -r shuiming_cc
word: -d  letters: d
word: -f  letters: f
word: -n  letters: n
word: -r  letters: r
stopped at: shuiming_cc (doesn't start with -)
win@DESKTOP-MEIH88T:~/webdev-projects$ ./c-c -d -f -nr -r -n shuiming_cc
word: -d  letters: d
word: -f  letters: f
word: -nr  letters: n r
word: -r  letters: r
word: -n  letters: n
stopped at: shuiming_cc (doesn't start with -)
win@DESKTOP-MEIH88T:~/webdev-projects$ echo $?
0
```
