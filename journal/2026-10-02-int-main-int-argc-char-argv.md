---
title: int main(int argc, char *argv[])
date: 2026-10-02
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
    for (int i =0; i < argc; i ++)
        printf("argv[%d] = %s\n", i, argv[i]);

    return 0;
}

Every C program starts running at main. When you type ./c-c -df -n hello, the system splits the line into words and hands main two things:

argc ("argument count"): the number of words, here 4: ./c-c, -df, -n and hello. The program's own name counts.

argv ("argument vector"): an array of pointers, one per word, followed by NULL:

argv ──► [0] ──► "./c-c"
         [1] ──► "-df"
         [2] ──► "-n"
         [3] ──► "hello"
         [4]     NULL

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra c-c.c -o c-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./args -df -n hello
-bash: ./args: No such file or directory
win@DESKTOP-MEIH88T:~/webdev-projects$ ./c-c args -df-n hello
argv[0] = ./c-c
argv[1] = args
argv[2] = -df-n
argv[3] = hello
win@DESKTOP-MEIH88T:~/webdev-projects$ ./c-c args "hello world"
argv[0] = ./c-c
argv[1] = args
argv[2] = hello world
```
