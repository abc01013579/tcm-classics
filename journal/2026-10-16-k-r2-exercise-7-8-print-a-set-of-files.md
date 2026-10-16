---
title: K&R2 exercise 7-8: print a set of files
date: 2026-10-16
---

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'a\nb\nc\nd\ne\n' | ./cc-c -2 | cat -v            # stdin, 2 lines a page: 3 pages
//              ./cc-c -2 <(printf 'a\nb\n') <(printf 'c\n') | cat -v   # 2 files, each from page 1
//              ./cc-c -30 cc-c-zh.txt zhouyi.txt | grep -a '==== '     # every title: 3 pages, then 149
//              ./cc-c zhouyi.txt nosuchfile cc-c-zh.txt | grep -a '==== ' | tail -3; echo "exit ${PIPESTATUS[0]}"   # bad file skipped, exit 2
//              ./cc-c cc-c-zh.txt zhouyi.txt | less                    # read it page by page (q quits)

//K&R2 exercise 7-8: print a set of files, each starting on a new page,
//with a title and a running page count for each file -- a small
//version of the Unix pr command.
//
//  ./cc-c [-N] file ...    N lines of text per page, 60 if not given
//                          no files: print standard input
//
//How a "new page" is made: the form feed character '\f' (ASCII 12).
//A printer that receives it rolls the paper to the top of the next
//sheet. A terminal mostly ignores it, which is why the run lines pipe
//through cat -v: that shows '\f' as ^L, so the page breaks are visible.
//
//Each page starts with a two-line title:
//  ==== zhouyi.txt ==== page 3 ====
//  (blank line)
//and the page number starts again at 1 with each new file.
//
//The title is printed lazily -- only when a line is about to go on a
//fresh page. So a file that exactly fills its last page doesn't get an
//empty extra page, and an empty file still gets its one titled page.

#define MAXLINE   1000
#define PAGELEN   60    //default lines of text per page

void printfile(FILE *fp, char *name, int pagelen);
void newpage(char *name, int page);

int main(int argc, char *argv[])
{
    char *prog = argv[0];
    FILE *fp;
    int pagelen = PAGELEN, trouble = 0;

    //IDIOM: argc > 1 && argv[1][0] == '-' -- the && guard: look at
    //argv[1]'s first char only after checking there IS an argv[1]
    if (argc > 1 && argv[1][0] == '-' && isdigit(argv[1][1])) {
        pagelen = atoi(argv[1] + 1);    //argv[1] + 1 skips the '-'
        if (pagelen < 1) {
            fprintf(stderr, "%s: page length must be at least 1\n", prog);
            exit(2);
        }
        argc--;
        argv++;
    }

    if (argc == 1)      //no files named: print standard input
        printfile(stdin, "(stdin)", pagelen);
    else
        //IDIOM: while (--argc > 0) with *++argv -- each file name once
        while (--argc > 0)
            //IDIOM: assign-in-test -- open and check for NULL in one expression
            if ((fp = fopen(*++argv, "r")) == NULL) {
                fprintf(stderr, "%s: can't open %s\n", prog, *argv);
                trouble = 1;    //report it, keep printing the rest
            } else {
                printfile(fp, *argv, pagelen);
                fclose(fp);
            }
    if (ferror(stdout)) {
        fprintf(stderr, "%s: error writing stdout\n", prog);
        exit(2);
    }
    return trouble ? 2 : 0;
}

//printfile:  print fp, pagelen lines per page, a title on each page
void printfile(FILE *fp, char *name, int pagelen)
{
    char line[MAXLINE];
    int lineno = 0;     //lines already on the current page
    int page = 0;       //this file's page count
    int len = 0;

    //IDIOM: while (fgets(line, max, fp) != NULL) -- read line by line
    while (fgets(line, MAXLINE, fp) != NULL) {
        if (lineno == 0)            //about to put a line on a fresh page
            newpage(name, ++page);
        fputs(line, stdout);
        len = strlen(line);
        //a line longer than MAXLINE arrives in pieces: count it only
        //when its '\n' has come (same rule as exercise 7-6)
        //IDIOM: line[strlen(line)-1] -- the last char of a non-empty string
        if (line[len - 1] == '\n')
            //IDIOM: ++n == max -- count, and wrap to 0 at the limit
            if (++lineno == pagelen)
                lineno = 0;
    }
    if (page == 0)                  //empty file: still give it a page
        newpage(name, ++page);
    else if (line[len - 1] != '\n')
        putchar('\n');  //last line had no '\n': end it, so the next
                        //file's form feed doesn't land mid-line
}

//newpage:  start a new page with its title
void newpage(char *name, int page)
{
    //IDIOM: static local -- keeps its value between calls; here it
    //remembers whether anything has been printed yet
    static int first = 1;

    if (!first)
        putchar('\f');  //no form feed before the very first page
    first = 0;
    printf("==== %s ==== page %d ====\n\n", name, page);
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'a\nb\nc\nd\ne\n' | ./cc-c -2 | cat -v
==== (stdin) ==== page 1 ====

a
b
^L==== (stdin) ==== page 2 ====

c
d
^L==== (stdin) ==== page 3 ====

e
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c -2 <(printf 'a\nb\n') <(printf 'c\n') | cat -v
==== /dev/fd/63 ==== page 1 ====

a
b
^L==== /dev/fd/62 ==== page 1 ====

c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c -30 cc-c-zh.txt zhouyi.txt | grep -a '==== '
==== cc-c-zh.txt ==== page 1 ====
```
