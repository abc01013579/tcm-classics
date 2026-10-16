---
title: K&R2 exercise 7-7: section 5.10's find (the -x -n version)
date: 2026-10-16
---

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'dragon\nhorse\ndragon fly\n' | ./cc-c dragon      # no files: reads stdin
//              ./cc-c -n 龍 zhouyi.txt                                 # one file: no name printed
//              ./cc-c -n 2026 zhouyi.txt cc-c-zh.txt                   # two files: name on each line
//              ./cc-c -xn 龍 <(printf '龍\n馬\n')                       # -x still works: 2:馬
//              ./cc-c 龍 zhouyi.txt nosuchfile zhouyi.txt; echo "exit $?"   # bad file skipped, exit 2
//              ./cc-c nosuchpattern zhouyi.txt; echo "exit $?"         # nothing found, exit 1
//              ./cc-c -q 龍 zhouyi.txt; echo "exit $?"                 # illegal option, exit 2

//K&R2 exercise 7-7: section 5.10's find (the -x -n version), now reading
//from the files named after the pattern, or from stdin if none are named.
//
//What changed from the chapter 5 version:
//  - the read-and-match loop moved into findpat(fp, ...), so the same
//    code runs on stdin or on each opened file
//  - my_getline (which only read stdin) replaced by fgets(line, MAXLINE, fp)
//  - the line number starts again at 1 in each file
//  - errors go to stderr (section 7.6), and a file that won't open is
//    reported and skipped, so the other files are still searched
//  - exit status like grep: 0 something matched, 1 nothing matched,
//    2 trouble (bad option, missing pattern, unopenable file). The
//    chapter 5 version returned the match count, which the shell cuts
//    to one byte: 256 matches would look like "exit 0".
//
//"Should the file name be printed when a matching line is found?"
//  Only when more than one file is named -- grep's answer. With one
//  file (or stdin) you already know where the line came from, and the
//  output stays plain text you can pipe on. With several, a bare line
//  could be from any of them, so each line gets "name:" in front.

#define MAXLINE 10000   //zhouyi.txt has a 2029-byte line

long findpat(FILE *fp, char *fname, char *pattern,
             int except, int number, int showname);

//find:  print lines that match pattern, from named files or stdin
int main(int argc, char *argv[])
{
    char *prog = argv[0];
    char *pattern;
    FILE *fp;
    long found = 0;
    int c, except = 0, number = 0, trouble = 0, showname;

    //IDIOM: while (--argc > 0 && (*++argv)[0] == '-') -- step to each
    //word and keep going while it starts with '-' (a flag word)
    while (--argc > 0 && (*++argv)[0] == '-')
        //IDIOM: while ((c = *++argv[0])) -- walk the letters of one flag
        //word, "-xn", until its '\0'
        while ((c = *++argv[0]))
            switch (c) {
            case 'x':
                except = 1;
                break;
            case 'n':
                number = 1;
                break;
            default:
                fprintf(stderr, "%s: illegal option %c\n", prog, c);
                exit(2);
            }
    if (argc < 1) {
        fprintf(stderr, "usage: %s -x -n pattern file ...\n", prog);
        exit(2);
    }
    pattern = *argv;    //the first non-flag word
    argc--;             //argc now counts the file names after it

    if (argc == 0)      //no files named: read standard input
        found = findpat(stdin, "", pattern, except, number, 0);
    else {
        showname = argc > 1;
        while (argc-- > 0) {
            //IDIOM: assign-in-test -- open and check for NULL in one expression
            if ((fp = fopen(*++argv, "r")) == NULL) {
                fprintf(stderr, "%s: can't open %s\n", prog, *argv);
                trouble = 1;    //remember it, but keep going
            } else {
                found += findpat(fp, *argv, pattern, except, number, showname);
                fclose(fp);
            }
        }
    }
    if (trouble)
        return 2;
    return found > 0 ? 0 : 1;
}

//findpat:  print the lines of fp that match pattern (or don't, with
//except); return how many were printed
long findpat(FILE *fp, char *fname, char *pattern,
             int except, int number, int showname)
{
    char line[MAXLINE];
    long lineno = 0, found = 0;

    //IDIOM: while (fgets(line, max, fp) != NULL) -- read a stream line
    //by line; NULL only at end of file
    while (fgets(line, MAXLINE, fp) != NULL) {
        lineno++;
        //IDIOM: (test) != except -- the match test is 1 or 0; comparing
        //it with except (1 or 0) flips the result when -x is on
        if ((strstr(line, pattern) != NULL) != except) {
            if (showname)
                printf("%s:", fname);
            if (number)
                printf("%ld:", lineno);
            printf("%s", line);
            found++;
        }
    }
    return found;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'dragon\nhorse\ndragon fly\n' | ./cc-c dragon
dragon
dragon fly
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c -n 龍 zhouyi.txt
4187:**上六：龍戰于野，其血玄黃。**
4189:- **龍戰于野 (Lóng zhàn yú yě)**: Dragons fight in the wilderness.
win@DESKTOP-MEIH88T:~/webdev-projects$  ./cc-c -n 2026 zhouyi.txt cc-c-zh.txt
cc-c-zh.txt:2:2026-10-04
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c -xn 龍 <(printf '龍\n馬\n')
2:馬
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c 龍 zhouyi.txt nosuchfile zhouyi.txt; echo "exit $?"
zhouyi.txt:**上六：龍戰于野，其血玄黃。**
zhouyi.txt:- **龍戰于野 (Lóng zhàn yú yě)**: Dragons fight in the wilderness.
./cc-c: can't open nosuchfile
zhouyi.txt:**上六：龍戰于野，其血玄黃。**
zhouyi.txt:- **龍戰于野 (Lóng zhàn yú yě)**: Dragons fight in the wilderness.
exit 2
win@DESKTOP-MEIH88T:~/webdev-projects$ /cc-c nosuchpattern zhouyi.txt; echo "exit $?"
-bash: /cc-c: No such file or directory
exit 127
win@DESKTOP-MEIH88T:~/webdev-projects$  ./cc-c -q 龍 zhouyi.txt; echo "exit $?"
./cc-c: illegal option q
exit 2
```
