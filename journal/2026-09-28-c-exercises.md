---
title: c exercises
date: 2026-09-28
---

```c

#include <stdio.h>
#include <stdlib.h>     //for atof()
#include <string.h>     //for strcmp(), strcpy()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf '10\n9\n100\n' | ./cc-c -n        (9 10 100)
//         or:  printf '10\n9\n100\n' | ./cc-c -nr       (100 10 9)
//         or:  printf 'pear\napple\nfig\n' | ./cc-c -r  (pear fig apple)

//K&R2 exercise 5-14: modify the sort program to handle a -r flag, which
//indicates sorting in reverse (decreasing) order. Be sure that -r works
//with -n.
//
//Builds on section 5.11's sort (archived just below). Two changes:
//
//1. Flags are read the way section 5.10's find reads -x and -n, so
//   they can be given separately (-n -r) or combined (-nr, -rn):
//       while (--argc > 0 && (*++argv)[0] == '-')
//           while ((c = *++argv[0]))
//               switch (c) ...
//   Anything else -- an unknown letter, or a word that isn't a flag --
//   prints a usage message.
//
//2. Reversing needs NO new comparison for text or for numbers. The
//   chosen comparison (strcmp_v or numcmp) is kept in a function
//   pointer, basecmp, and one small function wraps it:
//
//       int revcmp(void *a, void *b)  { return (*basecmp)(b, a); }
//
//   It calls the same comparison with its arguments SWAPPED. Asking
//   "how does b compare to a?" instead of "a to b" flips every answer,
//   so my_qsort -- unchanged -- sorts in decreasing order. Because
//   basecmp can point at either function, -r works with -n and without
//   it, for free. (Swapping is safer than writing -(*basecmp)(a, b):
//   negating the smallest possible int overflows, swapping can't.)
//
//   main then hands my_qsort one of three functions:
//       strcmp_v or numcmp          (normal order)
//       revcmp                      (reverse; revcmp calls basecmp)
//
//Same limits as 5.11: at most 5000 lines, 10000 bytes per line.
#define MAXLINES  5000      //max #lines to be sorted
#define MAXLEN    10000     //max length of any input line (book: 1000)
#define ALLOCSIZE 1000000   //size of available space for alloc

char *lineptr[MAXLINES];    //pointers to text lines

int readlines(char *lineptr[], int nlines);
void writelines(char *lineptr[], int nlines);
void my_qsort(void *lineptr[], int left, int right,
              int (*comp)(void *, void *));
int numcmp(void *, void *);
int strcmp_v(void *, void *);
int revcmp(void *, void *);

int (*basecmp)(void *, void *);     //the comparison revcmp reverses

//sort input lines
int main(int argc, char *argv[])
{
    int nlines;             //number of input lines read
    int numeric = 0;        //1 if -n: numeric sort
    int reverse = 0;        //1 if -r: decreasing order
    int c;

    while (--argc > 0 && (*++argv)[0] == '-')
        while ((c = *++argv[0]))
            switch (c) {
            case 'n':
                numeric = 1;
                break;
            case 'r':
                reverse = 1;
                break;
            default:
                printf("sort: illegal option %c\n", c);
                argc = -1;          //force the usage message below
                break;
            }
    if (argc != 0) {
        printf("usage: sort -n -r    e.g.  printf '10\\n9\\n' | ./cc-c -nr\n");
        return 1;
    }
    basecmp = numeric ? numcmp : strcmp_v;
    if ((nlines = readlines(lineptr, MAXLINES)) >= 0) {
        my_qsort((void **) lineptr, 0, nlines-1,
                 reverse ? revcmp : basecmp);
        writelines(lineptr, nlines);
        return 0;
    } else {
        printf("input too big to sort\n");
        return 1;
    }
}

//revcmp:  the comparison in basecmp, with its arguments swapped --
//so whatever basecmp calls "smaller" now sorts later
int revcmp(void *a, void *b)
{
    return (*basecmp)(b, a);
}

//my_qsort:  sort v[left]...v[right] into increasing order
void my_qsort(void *v[], int left, int right,
              int (*comp)(void *, void *))
{
    int i, last;
    void swap(void *v[], int, int);

    if (left >= right)      //do nothing if array contains
        return;             //fewer than two elements
    swap(v, left, (left + right)/2);
    last = left;
    for (i = left+1; i <= right; i++)
        if ((*comp)(v[i], v[left]) < 0)
            swap(v, ++last, i);
    swap(v, left, last);
    my_qsort(v, left, last-1, comp);
    my_qsort(v, last+1, right, comp);
}

//numcmp:  compare s1 and s2 numerically
int numcmp(void *s1, void *s2)
{
    double v1, v2;

    v1 = atof(s1);
    v2 = atof(s2);
    if (v1 < v2)
        return -1;
    else if (v1 > v2)
        return 1;
    else
        return 0;
}

//strcmp_v:  strcmp with the (void *, void *) type my_qsort expects
int strcmp_v(void *s1, void *s2)
{
    return strcmp(s1, s2);
}

//swap:  interchange v[i] and v[j]
void swap(void *v[], int i, int j)
{
    void *temp;

    temp = v[i];
    v[i] = v[j];
    v[j] = temp;
}

//--- from section 5.6 ---

int my_getline(char *, int);
char *alloc(int);

//readlines:  read input lines
int readlines(char *lineptr[], int maxlines)
{
    int len, nlines;
    char *p, line[MAXLEN];

    nlines = 0;
    while ((len = my_getline(line, MAXLEN)) > 0)
        if (nlines >= maxlines || (p = alloc(len)) == NULL)
            return -1;
        else {
            line[len-1] = '\0';  //delete newline
            strcpy(p, line);
            lineptr[nlines++] = p;
        }
    return nlines;
}

//writelines:  write output lines
void writelines(char *lineptr[], int nlines)
{
    int i;

    for (i = 0; i < nlines; i++)
        printf("%s\n", lineptr[i]);
}

//my_getline: read one line (including '\n') into s, return its length
int my_getline(char *s, int lim)
{
    int c = 0;
    char *p = s;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        *p++ = c;
    if (c == '\n')
        *p++ = c;
    *p = '\0';
    return p - s;
}

//alloc:  return pointer to n characters from one static buffer
static char allocbuf[ALLOCSIZE];
static char *allocp = allocbuf;

char *alloc(int n)
{
    if (allocbuf + ALLOCSIZE - allocp >= n) {
        allocp += n;
        return allocp - n;
    } else
        return NULL;
}

/*

#include <stdio.h>
#include <stdlib.h>     //for atof()
#include <string.h>     //for strcmp(), strcpy()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'pear\napple\nfig\n' | ./cc-c          (text order)
//         or:  printf '10\n9\n100\n' | ./cc-c -n             (number order)

//K&R2 section 5.11: pointers to functions. Sort input lines, either as
//text or -- with -n -- as numbers, using ONE sorting function. The
//comparison is passed to my_qsort as a pointer to a function:
//
//    int (*comp)(void *, void *)
//
//read it from the name outward: comp is a pointer (*comp) to a function
//taking (void *, void *) and returning int. The parentheses around
// *comp matter: without them, int *comp(void *, void *) would declare a
//FUNCTION returning a pointer to int -- something else entirely.
//
//Inside my_qsort, (*comp)(v[i], v[left]) calls whichever function comp
//points at. my_qsort never knows or cares whether it's comparing text
//or numbers -- main decides, by passing strcmp_v or numcmp.
//
//Why it matters: "10", "9", "100" sorted as TEXT is 10, 100, 9 ('1' <
//'9', character by character); as NUMBERS it's 9, 10, 100. Same sort,
//different comparison.
//
//Void pointers: my_qsort takes void *v[] -- an array of pointers to
//ANYTHING -- so the same function could sort pointers to other kinds of
//data too, given a suitable comparison. char * converts to void * and
//back freely.
//
//Fixed from the book's text:
//1. The book passes (numeric ? numcmp : strcmp), cast to
//   (int (*)(void*,void*)). gcc 15 refuses that line outright:
//   "error: pointer type mismatch in conditional expression" -- numcmp
//   takes char * but the real strcmp takes const char *, so the two
//   sides of ?: are different function types. Fix: both comparison
//   functions now take (void *, void *) -- exactly the type my_qsort
//   expects -- so no cast is needed at all. strcmp_v is a two-line
//   wrapper that hands its arguments to strcmp.
//   (Calling a function through a cast to a different function type,
//   as the book does, is formally undefined behavior; it happened to
//   work on 1988 machines. Matching the types exactly is the modern way.)
//2. qsort -> my_qsort, because <stdlib.h> (needed for atof) declares
//   the standard library's own qsort.
//3. main gets its `int` return type; a stray page number "107" removed;
//   block comments turned into //.
//4. readlines, writelines, swap, alloc and my_getline aren't in the
//   pasted text -- they come from section 5.6 (as in the archived 5.6
//   block further down this file). ALLOCSIZE raised from 10000 to
//   1000000 so a real file like zhouyi.txt (about 260 KB) fits, and
//   MAXLEN from 1000 to 10000 -- zhouyi.txt has a 2027-byte line that
//   the book's limit would split into three "lines".
#define MAXLINES  5000      //max #lines to be sorted
#define MAXLEN    10000     //max length of any input line (book: 1000)
#define ALLOCSIZE 1000000   //size of available space for alloc

char *lineptr[MAXLINES];    //pointers to text lines

int readlines(char *lineptr[], int nlines);
void writelines(char *lineptr[], int nlines);
void my_qsort(void *lineptr[], int left, int right,
              int (*comp)(void *, void *));
int numcmp(void *, void *);
int strcmp_v(void *, void *);

//sort input lines
int main(int argc, char *argv[])
{
    int nlines;             //number of input lines read
    int numeric = 0;        //1 if numeric sort

    if (argc > 1 && strcmp(argv[1], "-n") == 0)
        numeric = 1;
    if ((nlines = readlines(lineptr, MAXLINES)) >= 0) {
        my_qsort((void **) lineptr, 0, nlines-1,
                 numeric ? numcmp : strcmp_v);
        writelines(lineptr, nlines);
        return 0;
    } else {
        printf("input too big to sort\n");
        return 1;
    }
}

//my_qsort:  sort v[left]...v[right] into increasing order
void my_qsort(void *v[], int left, int right,
              int (*comp)(void *, void *))
{
    int i, last;
    void swap(void *v[], int, int);

    if (left >= right)      //do nothing if array contains
        return;             //fewer than two elements
    swap(v, left, (left + right)/2);
    last = left;
    for (i = left+1; i <= right; i++)
        if ((*comp)(v[i], v[left]) < 0)
            swap(v, ++last, i);
    swap(v, left, last);
    my_qsort(v, left, last-1, comp);
    my_qsort(v, last+1, right, comp);
}

//numcmp:  compare s1 and s2 numerically
int numcmp(void *s1, void *s2)
{
    double v1, v2;

    v1 = atof(s1);
    v2 = atof(s2);
    if (v1 < v2)
        return -1;
    else if (v1 > v2)
        return 1;
    else
        return 0;
}

//strcmp_v:  strcmp with the (void *, void *) type my_qsort expects
int strcmp_v(void *s1, void *s2)
{
    return strcmp(s1, s2);
}

//swap:  interchange v[i] and v[j]
void swap(void *v[], int i, int j)
{
    void *temp;

    temp = v[i];
    v[i] = v[j];
    v[j] = temp;
}

//--- from section 5.6 ---

int my_getline(char *, int);
char *alloc(int);

//readlines:  read input lines
int readlines(char *lineptr[], int maxlines)
{
    int len, nlines;
    char *p, line[MAXLEN];

    nlines = 0;
    while ((len = my_getline(line, MAXLEN)) > 0)
        if (nlines >= maxlines || (p = alloc(len)) == NULL)
            return -1;
        else {
            line[len-1] = '\0';  //delete newline
            strcpy(p, line);
            lineptr[nlines++] = p;
        }
    return nlines;
}

//writelines:  write output lines
void writelines(char *lineptr[], int nlines)
{
    int i;

    for (i = 0; i < nlines; i++)
        printf("%s\n", lineptr[i]);
}

//my_getline: read one line (including '\n') into s, return its length
int my_getline(char *s, int lim)
{
    int c = 0;
    char *p = s;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        *p++ = c;
    if (c == '\n')
        *p++ = c;
    *p = '\0';
    return p - s;
}

//alloc:  return pointer to n characters from one static buffer
static char allocbuf[ALLOCSIZE];
static char *allocp = allocbuf;

char *alloc(int n)
{
    if (allocbuf + ALLOCSIZE - allocp >= n) {
        allocp += n;
        return allocp - n;
    } else
        return NULL;
}

*/
/*

#include <stdio.h>
#include <stdlib.h>     //for malloc(), realloc(), free()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c < zhouyi.txt           (last 10 lines)
//         or:  ./cc-c -3 < zhouyi.txt        (last 3 lines)

//K&R2 exercise 5-13: write the program tail, which prints the last n
//lines of its input. By default, n is set to 10, let us say, but it can
//be changed by an optional argument so that
//    tail -n
//prints the last n lines. The program should behave rationally no
//matter how unreasonable the input or the value of n. Write the program
//so it makes the best use of available storage; lines should be stored
//as in the sorting program of Section 5.6, not in a two-dimensional
//array of fixed size.
//
//The idea: keep only the last n lines seen so far, in a RING of line
//pointers -- like section 5.6's lineptr[], but reused in a circle.
//Once the ring is full, each new line replaces the OLDEST one, whose
//memory is given back with free(). At the end, the ring holds exactly
//the last n lines, oldest first starting at `next`.
//
//  n = 3, input lines A B C D E:
//      after A B C:   [A B C]   next = 0  (full)
//      D arrives:     [D B C]   next = 1  (A freed; oldest is now B)
//      E arrives:     [D E C]   next = 2  (B freed; oldest is now C)
//      print from next, going round:  C D E
//
//"Best use of available storage":
//  - each line gets exactly as many bytes as it needs (malloc), and is
//    freed as soon as it drops out of the last n -- memory holds at
//    most n lines at any moment, never the whole input.
//    (Section 5.6's alloc() can only give memory back in reverse order,
//    so it can't free the oldest line; malloc()/free() can.)
//  - the ring itself grows only as needed (realloc, doubling), so
//    `tail -1000000000` on a 5-line file uses room for 5 pointers,
//    not a billion.
//
//"Rationally no matter how unreasonable":
//  - n = 0            prints nothing
//  - n bigger than the input      prints the whole input
//  - n absurdly large (more than 999999999)  treated as "all lines"
//  - a line of any length -- read_line() grows its buffer as needed,
//    so a million-character line is still ONE line (a fixed MAXLINE
//    would split it and miscount)
//  - a last line with no '\n' at the end is printed as it is
//  - empty input      prints nothing
//  - bad arguments (-x, -, 5, -5 -6)   usage message, exit status 1
//  - out of memory    an error message, exit status 1, never a crash
//
//Limitation: a zero byte ('\0') inside a line would end that line's
//string early. Text files don't contain them.
#define DEFLINES 10
#define MAXN     999999999L

int out_of_memory = 0;

char *read_line(void);
int digits_only(const char *s);

int main(int argc, char *argv[])
{
    long n = DEFLINES, cap = 0, count = 0, next = 0, i;
    char **ring = NULL, **bigger, *line, *s;

    if (argc > 2 || (argc == 2 && (argv[1][0] != '-' || !digits_only(argv[1] + 1)))) {
        printf("usage: tail -n    e.g.  ./cc-c -3 < zhouyi.txt\n");
        return 1;
    }
    if (argc == 2)                          //n from "-123"; cap absurd values
        for (n = 0, s = argv[1] + 1; *s != '\0'; s++)
            if ((n = 10 * n + (*s - '0')) > MAXN) {
                n = MAXN;
                break;
            }
    if (n == 0)
        return 0;

    while ((line = read_line()) != NULL) {
        if (count < n) {                    //still filling the ring
            if (count == cap) {             //full so far: grow it
                cap = (cap == 0) ? 16 : 2 * cap;
                if (cap > n)
                    cap = n;
                bigger = realloc(ring, cap * sizeof *ring);
                if (bigger == NULL) {
                    out_of_memory = 1;
                    free(line);
                    break;
                }
                ring = bigger;
            }
            ring[count++] = line;
        } else {                            //ring full: replace the oldest
            free(ring[next]);
            ring[next] = line;
            next = (next + 1) % n;
        }
    }
    if (out_of_memory) {
        printf("tail: out of memory\n");
        return 1;
    }
    for (i = 0; i < count; i++) {           //oldest first, going round
        fputs(ring[(next + i) % count], stdout);
        free(ring[(next + i) % count]);
    }
    free(ring);
    return 0;
}

//read_line:  read one line of ANY length (with its '\n', if it has one)
//into newly malloc'd memory; return NULL at end of input, or if memory
//runs out (then out_of_memory is set). The caller must free() the line.
char *read_line(void)
{
    char *buf = NULL, *bigger;
    long size = 0, len = 0;
    int c;

    while ((c = getchar()) != EOF) {
        if (len + 2 > size) {               //room for c and the '\0'?
            size = (size == 0) ? 128 : 2 * size;
            bigger = realloc(buf, size);
            if (bigger == NULL) {
                out_of_memory = 1;
                free(buf);
                return NULL;
            }
            buf = bigger;
        }
        buf[len++] = c;
        if (c == '\n')
            break;
    }
    if (len == 0)                           //nothing read: end of input
        return NULL;
    buf[len] = '\0';
    return buf;
}

//digits_only:  1 if s is one or more digits and nothing else (from 5-12)
int digits_only(const char *s)
{
    if (*s == '\0')
        return 0;
    for ( ; *s != '\0'; s++)
        if (*s < '0' || *s > '9')
            return 0;
    return 1;
}

*/
/*

#include <stdio.h>
#include <string.h>     //for strcmp()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c detab < zhouyi.txt              (default: every 8)
//         or:  ./cc-c detab -10 +4 < zhouyi.txt       (stops 10, 14, 18, ...)
//         or:  ./cc-c entab 4 8 12 < zhouyi.txt       (5-11 style list)

//K&R2 exercise 5-12: extend entab and detab to accept the shorthand
//    entab -m +n
//to mean tab stops every n columns, starting at column m. Choose
//convenient (for the user) default behavior.
//
//Builds on exercise 5-11 (archived just below): same detab/entab, same
//explicit stop list. New: -m and +n.
//
//Columns are counted from 0, as in 5-11 (col = characters already on
//the line). With -m +n the stops are
//    m, m+n, m+2n, m+3n, ...
//and a tab anywhere before column m jumps straight to m.
//
//Defaults -- chosen so that each flag does the obvious thing alone:
//    (nothing)     every 8:              8, 16, 24, ...   (terminal default)
//    +4            every 4:              4, 8, 12, ...    (m defaults to 0)
//    -10           first at 10, then every 8:  10, 18, 26, ...
//    -10 +4        first at 10, then every 4:  10, 14, 18, ...
//    4 8 12        explicit list, as in 5-11 (then every 8 past 12)
//Mixing the shorthand with an explicit list is refused -- it's unclear
//what that should mean, so it's safer to say so than to guess.
//
//Why m=0 as the default start: stop 0 never matters (col 0 is already
//the start of the line), so "-0 +n" is simply n, 2n, 3n, ... -- exactly
//what someone typing only +n expects.
//
//Parsing: each argument's FIRST character decides what it is -- '-'
//is m, '+' is n, a digit is a list entry. The rest must be all digits;
//digits_only() checks that, so "+x" or "-" alone are rejected instead
//of silently becoming 0. todigits() then builds the number the same way
//as K&R's atoi: n = 10 * n + (c - '0').
//
//Limitation (same as 5-11): columns are counted in bytes, so lines
//with Chinese (3 bytes, 2 columns wide) won't line up exactly.
#define TABINC   8      //default tab spacing
#define MAXSTOPS 100

int stops[MAXSTOPS];    //explicit stops (5-11 style), increasing
int nstops = 0;
int start = 0;          //m: first stop of the shorthand
int every = TABINC;     //n: spacing of the shorthand
int shorthand = 0;      //1 if -m or +n was given

int digits_only(const char *s);
int todigits(const char *s);
int nexttab(int col);
int istab(int col);
void detab(void);
void entab(void);

int main(int argc, char *argv[])
{
    int i, n;
    char *a;

    if (argc < 2 || (strcmp(argv[1], "detab") != 0 && strcmp(argv[1], "entab") != 0)) {
        printf("usage: detab|entab [-m] [+n]   or   detab|entab stop stop ...\n");
        return 1;
    }
    for (i = 2; i < argc; i++) {
        a = argv[i];
        if ((a[0] == '-' || a[0] == '+') && digits_only(a + 1)) {
            n = todigits(a + 1);
            if (a[0] == '-')
                start = n;                  //-m
            else if (n > 0)
                every = n;                  //+n
            else {
                printf("error: +n needs n of at least 1\n");
                return 1;
            }
            shorthand = 1;
        } else if (digits_only(a)) {
            n = todigits(a);
            if (n <= 0 || (nstops > 0 && n <= stops[nstops-1]) || nstops >= MAXSTOPS) {
                printf("error: tab stops must be positive and increasing: %s\n", a);
                return 1;
            }
            stops[nstops++] = n;
        } else {
            printf("error: don't understand '%s'\n", a);
            return 1;
        }
    }
    if (shorthand && nstops > 0) {
        printf("error: use either -m +n or a list of stops, not both\n");
        return 1;
    }
    if (argv[1][0] == 'd')
        detab();
    else
        entab();
    return 0;
}

//digits_only:  1 if s is one or more digits and nothing else
int digits_only(const char *s)
{
    if (*s == '\0')
        return 0;
    for ( ; *s != '\0'; s++)
        if (*s < '0' || *s > '9')
            return 0;
    return 1;
}

//todigits:  the number that the digit string s spells
int todigits(const char *s)
{
    int n = 0;

    for ( ; *s != '\0'; s++)
        n = 10 * n + (*s - '0');
    return n;
}

//nexttab:  the column a tab starting at col moves to
int nexttab(int col)
{
    int i;

    if (shorthand) {
        if (col < start)
            return start;                   //before m: jump to m
        return start + ((col - start) / every + 1) * every;
    }
    for (i = 0; i < nstops; i++)            //explicit list (5-11)
        if (stops[i] > col)
            return stops[i];
    return (col / TABINC + 1) * TABINC;
}

//istab:  1 if col is a tab stop, 0 if not
int istab(int col)
{
    int i;

    if (col == 0)
        return 0;
    if (shorthand)
        return col >= start && (col - start) % every == 0;
    for (i = 0; i < nstops; i++)
        if (stops[i] == col)
            return 1;
    if (nstops > 0 && col <= stops[nstops-1])
        return 0;
    return col % TABINC == 0;
}

//detab:  replace tabs with the right number of spaces
void detab(void)
{
    int c, col = 0;

    while ((c = getchar()) != EOF)
        if (c == '\t') {
            int stop = nexttab(col);
            while (col < stop) {
                putchar(' ');
                col++;
            }
        } else {
            putchar(c);
            col = (c == '\n') ? 0 : col + 1;
        }
}

//entab:  replace runs of spaces with tabs where they reach a tab stop
void entab(void)
{
    int c, col = 0, spaces = 0;

    while ((c = getchar()) != EOF) {
        if (c == ' ') {
            spaces++;
            col++;
            if (istab(col)) {
                putchar(spaces > 1 ? '\t' : ' ');
                spaces = 0;
            }
            continue;
        }
        if (c == '\t') {
            spaces = 0;
            putchar('\t');
            col = nexttab(col);
            continue;
        }
        for ( ; spaces > 0; spaces--)
            putchar(' ');
        putchar(c);
        col = (c == '\n') ? 0 : col + 1;
    }
    for ( ; spaces > 0; spaces--)
        putchar(' ');
}

*/
/*

#include <stdio.h>
#include <stdlib.h>     //for atoi()
#include <string.h>     //for strcmp()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c detab [stop ...] < input      (tabs -> spaces)
//         or:  ./cc-c entab [stop ...] < input      (spaces -> tabs)

//K&R2 exercise 5-11: modify the programs entab and detab (written as
//exercises in Chapter 1) to accept a list of tab stops as arguments.
//Use the default tab settings if there are no arguments.
//
//Chapter 1's exercises 1-20 (detab) and 1-21 (entab) weren't done yet
//in this file, so both are written here from scratch, with 5-11's tab
//stop list built in. Only one main() can be active in cc-c.c, so the
//first argument chooses which program runs.
//
//Columns are counted from 0: col = how many characters are already on
//the current line. A tab stop at 8 means "after the tab, the next
//character appears at position 8" -- the same as a terminal's default.
//
//  ./cc-c detab           stops every 8 columns: 8, 16, 24, ...
//  ./cc-c detab 4 8 12    stops at 4, 8, 12; past the last one given,
//                         stops continue at the default every-8 spacing
//                         (16, 24, ...), so a long line never runs out
//
//The stops must be positive and increasing. They're read from argv as
//TEXT ("4", "8", "12") and turned into numbers with atoi(), then kept
//in stops[]. Everything else asks two questions about a column:
//    nexttab(col)  where does a tab starting at col end?
//    istab(col)    is col itself a tab stop?
//
//detab: a tab becomes (nexttab(col) - col) spaces.
//
//entab: spaces are held back, not printed, while they're being
//counted. When the count reaches a tab stop, the held spaces are
//replaced by one tab. If any other character comes first, the held
//spaces are printed as spaces. Choice made (K&R asks about it in 1-21):
//a SINGLE space that happens to reach a tab stop stays a space -- a
//tab would save nothing and would hide the space.
//
//Limitation: columns are counted in BYTES (one char = one column),
//as in K&R. That's right for ASCII, but a Chinese character is 3 UTF-8
//bytes yet only 2 columns wide on screen, so lines containing Chinese
//won't line up correctly.
#define TABINC   8      //default tab spacing
#define MAXSTOPS 100    //most tab stops accepted on the command line

int stops[MAXSTOPS];    //tab stops from the command line, increasing
int nstops = 0;         //how many there are (0 = use the default)

int nexttab(int col);
int istab(int col);
void detab(void);
void entab(void);

int main(int argc, char *argv[])
{
    int i, n;

    if (argc < 2 || (strcmp(argv[1], "detab") != 0 && strcmp(argv[1], "entab") != 0)) {
        printf("usage: detab|entab [stop ...]\n");
        return 1;
    }
    for (i = 2; i < argc; i++) {            //argv[2], argv[3], ... = stops
        n = atoi(argv[i]);
        if (n <= 0 || (nstops > 0 && n <= stops[nstops-1])) {
            printf("error: tab stops must be positive and increasing: %s\n", argv[i]);
            return 1;
        }
        if (nstops >= MAXSTOPS) {
            printf("error: more than %d tab stops\n", MAXSTOPS);
            return 1;
        }
        stops[nstops++] = n;
    }
    if (argv[1][0] == 'd')
        detab();
    else
        entab();
    return 0;
}

//nexttab:  the column a tab starting at col moves to
int nexttab(int col)
{
    int i;

    for (i = 0; i < nstops; i++)            //first listed stop past col
        if (stops[i] > col)
            return stops[i];
    return (col / TABINC + 1) * TABINC;     //else the next multiple of 8
}

//istab:  1 if col is a tab stop, 0 if not
int istab(int col)
{
    int i;

    if (col == 0)
        return 0;
    for (i = 0; i < nstops; i++)
        if (stops[i] == col)
            return 1;
    if (nstops > 0 && col <= stops[nstops-1])
        return 0;                           //inside the listed range
    return col % TABINC == 0;               //default spacing beyond it
}

//detab:  replace tabs with the right number of spaces
void detab(void)
{
    int c, col = 0;

    while ((c = getchar()) != EOF)
        if (c == '\t') {
            int stop = nexttab(col);
            while (col < stop) {
                putchar(' ');
                col++;
            }
        } else {
            putchar(c);
            col = (c == '\n') ? 0 : col + 1;
        }
}

//entab:  replace runs of spaces with tabs where they reach a tab stop
void entab(void)
{
    int c, col = 0, spaces = 0;

    while ((c = getchar()) != EOF) {
        if (c == ' ') {
            spaces++;                       //hold it back for now
            col++;
            if (istab(col)) {
                if (spaces > 1)
                    putchar('\t');          //several spaces -> one tab
                else
                    putchar(' ');           //a single space stays a space
                spaces = 0;
            }
            continue;
        }
        if (c == '\t') {                    //held spaces never cross a
            spaces = 0;                     //stop, so the tab alone
            putchar('\t');                  //reaches the same place
            col = nexttab(col);
            continue;
        }
        for ( ; spaces > 0; spaces--)       //any other char: print the
            putchar(' ');                   //held spaces as spaces
        putchar(c);
        col = (c == '\n') ? 0 : col + 1;
    }
    for ( ; spaces > 0; spaces--)           //spaces at the very end
        putchar(' ');
}

*/
/*

#include <stdio.h>
#include <stdlib.h>     //for strtod()
#include <string.h>     //for strlen()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c 2 3 4 + '*'

//K&R2 exercise 5-10: write the program expr, which evaluates a reverse
//Polish expression from the command line, where each operator or
//operand is a separate argument. For example,
//    expr 2 3 4 + *
//evaluates 2 * (3+4).
//
//This joins two things from the book: chapter 4's reverse Polish
//calculator (a stack: numbers are pushed; an operator pops two numbers,
//combines them, and pushes the result) and section 5.10's argc/argv.
//Chapter 4 read its input character by character with getop(); here
//the shell has already split the input into words, so every argv[i]
//is either a whole number or a whole operator -- no getop() needed.
//
//Walking through  2 3 4 + *  (stack shown bottom -> top):
//    2   push          2
//    3   push          2 3
//    4   push          2 3 4
//    +   pop 4, 3      2 7        (3 + 4)
//    *   pop 7, 2      14         (2 * 7)
//    end: exactly one value left -> the answer, 14
//
//Order matters for - and /: the FIRST value popped is the RIGHT-hand
//operand. `5 2 -` pops 2, then 5, and computes 5 - 2 = 3, not 2 - 5.
//
//Telling numbers from operators:
//  - an argument that is exactly one of + - * / (length 1) is an operator
//  - anything else must be a number. strtod() converts it and sets
//    `end` to the first character it couldn't use; if that isn't the
//    '\0' at the end of the argument, the argument wasn't a number
//    (e.g. "2x" or "abc") and it's an error. This also lets "-5" be the
//    number minus five, while "-" alone is subtraction.
//
//Errors are reported and exit with status 1: too few numbers for an
//operator, dividing by zero, a word that's neither number nor operator,
//a full stack, or anything other than exactly one value left at the
//end (e.g. `2 3` with no operator).
//
//Shell note: * must be quoted, as '*' or \*. Unquoted, the shell
//replaces * with the list of file names in the current folder before
//the program ever runs -- expr would receive "cc-c.c ccc-c.c ..."
//instead of the operator.
#define MAXVAL 100      //maximum depth of the value stack

double val[MAXVAL];     //the value stack
int sp = 0;             //next free stack position

int push(double f);
int pop(double *f);

int main(int argc, char *argv[])
{
    double a, b, x;
    char *end;
    int i;

    if (argc < 2) {
        printf("usage: expr number number op ...   e.g. expr 2 3 4 + '*'\n");
        return 1;
    }
    for (i = 1; i < argc; i++) {
        char *s = argv[i];

        if (strlen(s) == 1 && strchr("+-*" "/", s[0]) != NULL) {
            if (!pop(&b) || !pop(&a)) {             //b = right, a = left
                printf("error: '%s' needs two numbers before it\n", s);
                return 1;
            }
            switch (s[0]) {
            case '+': x = a + b; break;
            case '-': x = a - b; break;
            case '*': x = a * b; break;
            case '/':
                if (b == 0.0) {
                    printf("error: division by zero\n");
                    return 1;
                }
                x = a / b;
                break;
            }
            push(x);
        } else {
            x = strtod(s, &end);
            if (end == s || *end != '\0') {
                printf("error: '%s' is not a number or operator\n", s);
                return 1;
            }
            if (!push(x)) {
                printf("error: stack full (more than %d numbers)\n", MAXVAL);
                return 1;
            }
        }
    }
    if (sp != 1) {
        printf("error: %d values left over -- missing an operator?\n", sp);
        return 1;
    }
    printf("%g\n", val[0]);
    return 0;
}

//push:  push f onto the value stack; 0 if the stack is full
int push(double f)
{
    if (sp >= MAXVAL)
        return 0;
    val[sp++] = f;
    return 1;
}

//pop:  pop the top value into *f; 0 if the stack is empty
int pop(double *f)
{
    if (sp <= 0)
        return 0;
    *f = val[--sp];
    return 1;
}

*/
/*

#include <stdio.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c [-x] [-n] pattern < some_text_file

//K&R2 section 5.10, second version of find: same search, plus two
//optional flags given before the pattern:
//    -x   "except": print the lines that DON'T match
//    -n   "number": put each printed line's line number in front
//Flags can come separately (-x -n) or combined (-xn / -nx).
//
//How the flags are read -- the two dense lines of this program:
//
//  while (--argc > 0 && (*++argv)[0] == '-')
//      ++argv steps argv to the next word; *argv is that word (a
//      char *); (*argv)[0] is its first char. So: "while there are
//      words left and the next one starts with '-'". The parentheses
//      matter: [] binds tighter than *, so *++argv[0] would mean
//      something else entirely (see next line).
//
//  while ((c = *++argv[0]))
//      argv[0] is the current word -- a char * pointing into "-xn".
//      ++argv[0] moves THAT pointer one char along (past the '-'
//      first time), and * reads the char there. So this walks the
//      letters x, n, ... of one flag word until it hits the '\0' at
//      its end, which is 0 = false and stops the loop.
//
//  For `./cc-c -xn 龙`, argv starts as:
//      argv[0] -> "./cc-c"   argv[1] -> "-xn"   argv[2] -> "龙"
//  The outer loop moves argv to "-xn"; the inner loop reads 'x' then
//  'n'; the outer loop moves argv to "龙", which has no '-', so it
//  stops with argc == 1 and *argv == "龙" -- the pattern.
//
//  (strstr(line, *argv) != NULL) != except
//      the match test is 1 or 0; comparing it with except (1 or 0)
//      flips the result when -x is on. One line does both modes.
//
//Fixed from the book's text:
//1. a stray "105" (a page number from the PDF) removed.
//2. getline -> my_getline, and main gets its `int` return type, as in
//   the first version of find.
//3. while (c = *++argv[0]) -> while ((c = *++argv[0])). Same meaning;
//   the extra parentheses tell gcc the = is intended, not a typo for
//   ==, so -Wall stops warning "suggest parentheses around assignment".
//4. MAXLINE raised from 1000 to 10000: Chinese text uses 3 bytes per
//   character, and zhouyi.txt has a 2028-byte line that the book's
//   limit would split into pieces.
//5. the book's block comment above main turned into a // comment.
//
//An illegal flag makes main return -1. The shell only keeps one byte
//of the exit status, so `echo $?` shows 255 (-1 is all bits set).
#define MAXLINE 10000

int my_getline(char *line, int max);

//find:  print lines that match pattern from 1st arg
int main(int argc, char *argv[])
{
    char line[MAXLINE];
    long lineno = 0;
    int c, except = 0, number = 0, found = 0;

    while (--argc > 0 && (*++argv)[0] == '-')
        while ((c = *++argv[0]))
            switch (c) {
            case 'x':
                except = 1;
                break;
            case 'n':
                number = 1;
                break;
            default:
                printf("find: illegal option %c\n", c);
                argc = 0;
                found = -1;
                break;
            }
    if (argc != 1)
        printf("Usage: find -x -n pattern\n");
    else
        while (my_getline(line, MAXLINE) > 0) {
            lineno++;
            if ((strstr(line, *argv) != NULL) != except) {
                if (number)
                    printf("%ld:", lineno);
                printf("%s", line);
                found++;
            }
        }
    return found;
}

//my_getline: read one line (including '\n') into s, return its length
//(the pointer-walking version from exercise 5-6)
int my_getline(char *s, int lim)
{
    int c = 0;
    char *p = s;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        *p++ = c;
    if (c == '\n')
        *p++ = c;
    *p = '\0';
    return p - s;
}

*/
/*

#include <stdio.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c pattern < some_text_file

//K&R2 section 5.10: find -- print every input line that contains the
//pattern given as the program's first command-line argument.
//
//argc = how many words were typed on the command line, program name
//included; argv[] = those words, as strings. For `./cc-c 龙`:
//    argc    == 2
//    argv[0] == "./cc-c"
//    argv[1] == "龙"
//So "exactly one pattern given" is argc == 2, and the pattern is argv[1].
//
//strstr(s, t) (from <string.h>) returns a pointer to the first place t
//occurs inside s, or NULL if it doesn't occur at all.
//
//Fixed from the book's text, same as the section 5.6 program:
//
//1. getline() renamed my_getline() -- modern <stdio.h> already declares
//   a different getline(), so the book's name collides.
//
//2. `main(int argc, ...)` with no return type was legal in 1988 C
//   ("implicit int") but isn't anymore; now `int main`.
//
//3. The book's slash-star comment above main turned into // -- a block
//   comment inside this block would break it when it's archived later.
//
//main returns `found`, the number of matching lines. The shell can
//see it with `echo $?` right after running -- a program's return
//value from main is its "exit status".
#define MAXLINE 10000

int my_getline(char *line, int max);

//find:  print lines that match pattern from 1st arg
int main(int argc, char *argv[])
{
    char line[MAXLINE];
    int found = 0;

    if (argc != 2)
        printf("Usage: find pattern\n");
    else
        while (my_getline(line, MAXLINE) > 0)
            if (strstr(line, argv[1]) != NULL) {
                printf("%s", line);
                found++;
            }
    return found;
}

//my_getline: read one line (including '\n') into s, return its length
//(the pointer-walking version from exercise 5-6)
int my_getline(char *s, int lim)
{
    int c = 0;
    char *p = s;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        *p++ = c;
    if (c == '\n')
        *p++ = c;
    *p = '\0';
    return p - s;
}

*/
/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 5-9: rewrite the routines day_of_year and month_day
//with pointers instead of indexing.
//
//Starts from exercise 5-8's checked versions (archived just below) --
//same checks, same test cases, same output -- only the way daytab is
//walked changes.
//
//The key idea from section 5.9: daytab is ONE block of 2 x 13 chars,
//laid out row after row in memory:
//
//    daytab[0]: 0 31 28 31 30 31 30 31 31 30 31 30 31
//    daytab[1]: 0 31 29 31 30 31 30 31 31 30 31 30 31
//
//daytab[leap] names one whole row. Used as a value, a row (an array of
//13 chars) turns into a pointer to its first char, so
//    char *p = daytab[leap];
//makes p point at that row's placeholder 0. From there:
//    *(p + month)   is the same as   daytab[leap][month]
//    *++p           steps p to the next month, then reads it
//and the month number itself falls out of pointer subtraction:
//    p - daytab[leap]   = how many chars p has moved from the row start
//
//(Fully pointer-ized, even the row choice could be written
// *(daytab + leap) instead of daytab[leap] -- same thing, since a[i] is
//defined as *(a + i). Kept daytab[leap] for the row because it reads
//more clearly; all the per-month work is pure pointers.)

static char daytab[2][13] = {
    {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31},
    {0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}
};

int is_leap(int year);
int day_of_year(int year, int month, int day);
void month_day(int year, int yearday, int *pmonth, int *pday);

int main(void)
{
    //{year, month, day} -- valid cases first, then bad ones
    int tests[][3] = {
        {2026,  9, 26},   //Sep 26
        {2024,  2, 29},   //Feb 29 in a leap year: ok
        {2026,  2, 29},   //Feb 29 in a non-leap year: bad
        {2026, 12, 31},   //last day: 365
        {2024, 12, 31},   //last day of leap year: 366
        {2026, 13,  1},   //month too big
        {2026,  0, 10},   //month too small
        {2026,  4, 31},   //April has 30 days
        {   0,  1,  1},   //year 0
    };
    int n = sizeof tests / sizeof tests[0];
    int i;

    printf("day_of_year:\n");
    for (i = 0; i < n; i++) {
        int d = day_of_year(tests[i][0], tests[i][1], tests[i][2]);
        printf("  %4d-%02d-%02d -> %4d%s\n", tests[i][0], tests[i][1],
               tests[i][2], d, d == -1 ? "   (error)" : "");
    }

    //{year, yearday}
    int ytests[][2] = {
        {2026, 269}, {2024, 60}, {2026, 365}, {2024, 366},
        {2026, 366}, {2026, 0}, {2026, -5}, {0, 100},
    };
    int m, d;

    printf("month_day:\n");
    for (i = 0; i < (int)(sizeof ytests / sizeof ytests[0]); i++) {
        month_day(ytests[i][0], ytests[i][1], &m, &d);
        printf("  %4d day %4d -> month %2d, day %2d%s\n", ytests[i][0],
               ytests[i][1], m, d, m == 0 ? "   (error)" : "");
    }
    return 0;
}

//is_leap:  1 if year is a leap year, 0 if not
int is_leap(int year)
{
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

//day_of_year:  set day of year from month & day; -1 on bad input
int day_of_year(int year, int month, int day)
{
    char *p;

    if (year < 1 || month < 1 || month > 12)
        return -1;
    p = daytab[is_leap(year)];      //p -> this year's row, at the 0
    if (day < 1 || day > *(p + month))
        return -1;
    while (--month > 0)             //add the lengths of months
        day += *++p;                //1 .. month-1
    return day;
}

//month_day:  set month, day from day of year; both 0 on bad input
void month_day(int year, int yearday, int *pmonth, int *pday)
{
    char *p, *row;
    int leap;

    if (year < 1) {
        *pmonth = *pday = 0;
        return;
    }
    leap = is_leap(year);
    if (yearday < 1 || yearday > (leap ? 366 : 365)) {
        *pmonth = *pday = 0;
        return;
    }
    row = p = daytab[leap];         //both -> the row's placeholder 0
    while (yearday > *++p)          //step to next month; still past it?
        yearday -= *p;
    *pmonth = p - row;              //months stepped = month number
    *pday = yearday;
}

*/
/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 5-8: there is no error checking in day_of_year or
//month_day. Remedy this defect.
//
//Section 5.7's versions trust their input completely. day_of_year(2026,
//13, 40) happily walks past the end of daytab's row (reading memory
//that isn't part of the table) and returns garbage; month_day with
//yearday 400 walks off the end the same way. Nothing tells the caller
//anything went wrong.
//
//What each function now checks:
//
//day_of_year(year, month, day):
//  - year  must be >= 1 (no year 0 in the Gregorian calendar)
//  - month must be 1..12 (daytab[leap][0] is a 0 placeholder, and
//    there is no daytab[leap][13])
//  - day   must be 1..days-in-that-month, looked up in daytab itself,
//    so Feb 29 is accepted only in leap years
//  returns -1 on bad input. -1 is safe as an error signal because a
//  real day of the year is always 1..366, never negative.
//
//month_day(year, yearday, *pmonth, *pday):
//  - year    must be >= 1
//  - yearday must be 1..365, or 1..366 in a leap year
//  it returns void, so it can't return -1 -- instead it sets *pmonth
//  and *pday to 0 on error. 0 is never a real month or day, so the
//  caller can check *pmonth == 0. (Changing it to return int would
//  also work, but this keeps the book's signature.)
//
//Also: the book's leap-year line
//    leap = year%4 == 0 && year%100 != 0 || year%400 == 0;
//is correct (&& binds tighter than ||), but gcc -Wall warns
//"suggest parentheses around '&&' within '||'". Added the parentheses
//so the intent is explicit -- same meaning, no warning. It's now in
//one helper, is_leap(), instead of being repeated in both functions.

static char daytab[2][13] = {
    {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31},
    {0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}
};

int is_leap(int year);
int day_of_year(int year, int month, int day);
void month_day(int year, int yearday, int *pmonth, int *pday);

int main(void)
{
    //{year, month, day} -- valid cases first, then bad ones
    int tests[][3] = {
        {2026,  9, 26},   //today
        {2024,  2, 29},   //Feb 29 in a leap year: ok
        {2026,  2, 29},   //Feb 29 in a non-leap year: bad
        {2026, 12, 31},   //last day: 365
        {2024, 12, 31},   //last day of leap year: 366
        {2026, 13,  1},   //month too big
        {2026,  0, 10},   //month too small
        {2026,  4, 31},   //April has 30 days
        {   0,  1,  1},   //year 0
    };
    int n = sizeof tests / sizeof tests[0];
    int i;

    printf("day_of_year:\n");
    for (i = 0; i < n; i++) {
        int d = day_of_year(tests[i][0], tests[i][1], tests[i][2]);
        printf("  %4d-%02d-%02d -> %4d%s\n", tests[i][0], tests[i][1],
               tests[i][2], d, d == -1 ? "   (error)" : "");
    }

    //{year, yearday}
    int ytests[][2] = {
        {2026, 269}, {2024, 60}, {2026, 365}, {2024, 366},
        {2026, 366}, {2026, 0}, {2026, -5}, {0, 100},
    };
    int m, d;

    printf("month_day:\n");
    for (i = 0; i < (int)(sizeof ytests / sizeof ytests[0]); i++) {
        month_day(ytests[i][0], ytests[i][1], &m, &d);
        printf("  %4d day %4d -> month %2d, day %2d%s\n", ytests[i][0],
               ytests[i][1], m, d, m == 0 ? "   (error)" : "");
    }
    return 0;
}

//is_leap:  1 if year is a leap year, 0 if not
int is_leap(int year)
{
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

//day_of_year:  set day of year from month & day; -1 on bad input
int day_of_year(int year, int month, int day)
{
    int i, leap;

    if (year < 1 || month < 1 || month > 12)
        return -1;
    leap = is_leap(year);
    if (day < 1 || day > daytab[leap][month])
        return -1;
    for (i = 1; i < month; i++)
        day += daytab[leap][i];
    return day;
}

//month_day:  set month, day from day of year; both 0 on bad input
void month_day(int year, int yearday, int *pmonth, int *pday)
{
    int i, leap;

    if (year < 1) {
        *pmonth = *pday = 0;
        return;
    }
    leap = is_leap(year);
    if (yearday < 1 || yearday > (leap ? 366 : 365)) {
        *pmonth = *pday = 0;
        return;
    }
    for (i = 1; yearday > daytab[leap][i]; i++)
        yearday -= daytab[leap][i];
    *pmonth = i;
    *pday = yearday;
}

*/
/*

#include <stdio.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 5-7: rewrite readlines to store lines in an array
//supplied by main, rather than calling alloc to maintain storage.
//How much faster is the program?
//
//What changed from section 5.6 (the block archived just below):
//
//1. main() now owns the storage: `char linestore[MAXSTORE]` is a local
//   array in main, passed down to readlines along with its size. The
//   static allocbuf/allocp pair and the alloc() function are gone.
//
//2. readlines keeps its own "next free byte" pointer p, starting at
//   linestore. For each line it checks there's room (p + len must not
//   run past linestore + maxstore), copies the line in, records p in
//   lineptr[], then advances p by len. That is EXACTLY what alloc() did
//   internally -- the bookkeeping just moved from a separate function
//   (with hidden static state) into readlines itself (with a local
//   variable). Lines still sit back to back in one block, each ending
//   in '\0'; len counts the '\n' that gets overwritten by '\0', so len
//   bytes is exactly enough.
//
//3. linestore is `static` inside main. 10000 bytes on the stack would
//   be fine, but if MAXSTORE is ever raised to megabytes, a plain local
//   array could overflow the stack (typically 8 MB on Linux). `static`
//   puts it in the same place allocbuf used to live (the data/bss
//   segment), so behavior is identical and the size limit is safe.
//   It's still main's array -- only main can name it; readlines only
//   sees what main hands it.
//
//How much faster? Essentially not at all. alloc() was already just a
//comparison and a pointer add -- no system call, no searching, nothing
//like malloc(). Removing it saves one function call per line, which
//the compiler may inline away anyway. The program's time goes into
//reading input (getchar), strcpy, strcmp during the sort, and printf.
//The real gain is design, not speed: no hidden global state, and the
//caller decides how much storage exists and where it lives.
#define MAXLINES 5000    //max #lines to be sorted
#define MAXLEN   1000    //max length of any input line
#define MAXSTORE 10000   //size of the line-storage array main supplies

char *lineptr[MAXLINES];  //pointers to text lines

int my_getline(char *, int);
int readlines(char *lineptr[], int maxlines, char *linestore, int maxstore);
void writelines(char *lineptr[], int nlines);
void my_qsort(char *lineptr[], int left, int right);
void swap(char *v[], int i, int j);

int main(void)
{
    int nlines;                         //number of input lines read
    static char linestore[MAXSTORE];    //where the line text actually lives

    if ((nlines = readlines(lineptr, MAXLINES, linestore, MAXSTORE)) >= 0) {
        my_qsort(lineptr, 0, nlines-1);
        writelines(lineptr, nlines);
        return 0;
    } else {
        printf("error: input too big to sort\n");
        return 1;
    }
}

//readlines:  read input lines into linestore, pointers into lineptr
int readlines(char *lineptr[], int maxlines, char *linestore, int maxstore)
{
    int len, nlines;
    char *p = linestore;                    //next free byte in linestore
    char *end = linestore + maxstore;       //one past the last byte
    char line[MAXLEN];

    nlines = 0;
    while ((len = my_getline(line, MAXLEN)) > 0)
        if (nlines >= maxlines || p + len > end)
            return -1;
        else {
            line[len-1] = '\0';  //delete newline
            strcpy(p, line);
            lineptr[nlines++] = p;
            p += len;            //step past this line (and its '\0')
        }
    return nlines;
}

//writelines:  write output lines
void writelines(char *lineptr[], int nlines)
{
    int i;
    for (i = 0; i < nlines; i++)
        printf("%s\n", lineptr[i]);
}

//my_getline: read one line (including '\n') into s, return its length
//(same pointer-walking version from exercise 5-6)
int my_getline(char *s, int lim)
{
    int c;
    char *p = s;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        *p++ = c;
    if (c == '\n')
        *p++ = c;
    *p = '\0';
    return p - s;
}

//my_qsort:  sort v[left]...v[right] into increasing order (unchanged
//from section 5.6)
void my_qsort(char *v[], int left, int right)
{
    int i, last;

    if (left >= right)      //do nothing if array contains
        return;             //fewer than two elements
    swap(v, left, (left + right)/2);
    last = left;
    for (i = left + 1; i <= right; i++)
        if (strcmp(v[i], v[left]) < 0)
            swap(v, ++last, i);
    swap(v, left, last);
    my_qsort(v, left, last-1);
    my_qsort(v, last+1, right);
}

//swap:  interchange v[i] and v[j] (unchanged from section 5.6)
void swap(char *v[], int i, int j)
{
    char *temp;
    temp = v[i];
    v[i] = v[j];
    v[j] = temp;
}

*/
/*

#include <stdio.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 5.6: sort a set of input text lines, using pointers
//instead of moving the text itself -- lineptr[] holds a POINTER to
//where each line lives (allocated once by alloc()), so sorting is just
//rearranging which pointers sit in which slots; the actual line bytes
//never move in memory. This is the payoff of the whole array-of-
//pointers idea introduced earlier in the chapter.
//
//What was fixed/added from the pasted text, and why:
//
//1. main()'s body had an empty { } immediately followed by the real
//   if/else floating outside any function -- a copy/paste artifact.
//   It's one function; the if/else is main()'s actual body.
//
//2. `if (nlines >= maxlines || p = alloc(len) == NULL)` is missing a
//   parenthesis pair. As literally written, `==` binds tighter than
//   `=`, so this would try to assign p the BOOLEAN result of
//   `alloc(len) == NULL` -- not what's wanted. The real book has
//   `(p = alloc(len)) == NULL`: call alloc, store its result in p,
//   THEN compare that stored pointer against NULL.
//
//3. A stray "98" sat mid-statement (a page number swept up by the
//   PDF copy) -- removed, no code content there.
//
//4. getline() and qsort() are both declared but would collide with
//   <stdio.h>'s real getline() and <stdlib.h>'s real qsort() --
//   renamed my_getline/my_qsort, the same fix already applied
//   elsewhere in this file (exercise 5-6's my_getline is reused
//   here verbatim; my_qsort is section 5.1's int-array qsort,
//   adapted to compare strings instead -- see the note above it).
//
//5. alloc() and swap() are CALLED by this excerpt but weren't
//   included in what was pasted -- both supplied below, straight
//   from the book (alloc: section 5.4; swap: section 5.6, identical
//   in spirit to section 5.1's swap, just typed for char* instead of
//   int).
#define MAXLINES  5000   //max #lines to be sorted
#define MAXLEN    1000   //max length of any input line
#define ALLOCSIZE 10000  //size of available space for alloc

char *lineptr[MAXLINES];  //pointers to text lines

int my_getline(char *, int);
char *alloc(int);
int readlines(char *lineptr[], int nlines);
void writelines(char *lineptr[], int nlines);
void my_qsort(char *lineptr[], int left, int right);
void swap(char *v[], int i, int j);

int main(void)
{
    int nlines;   //number of input lines read

    if ((nlines = readlines(lineptr, MAXLINES)) >= 0) {
        my_qsort(lineptr, 0, nlines-1);
        writelines(lineptr, nlines);
        return 0;
    } else {
        printf("error: input too big to sort\n");
        return 1;
    }
}

//readlines:  read input lines
int readlines(char *lineptr[], int maxlines)
{
    int len, nlines;
    char *p, line[MAXLEN];

    nlines = 0;
    while ((len = my_getline(line, MAXLEN)) > 0)
        if (nlines >= maxlines || (p = alloc(len)) == NULL)
            return -1;
        else {
            line[len-1] = '\0';  //delete newline
            strcpy(p, line);
            lineptr[nlines++] = p;
        }
    return nlines;
}

//writelines:  write output lines
void writelines(char *lineptr[], int nlines)
{
    int i;
    for (i = 0; i < nlines; i++)
        printf("%s\n", lineptr[i]);
}

//my_getline: read one line (including '\n') into s, return its length
//(same pointer-walking version from exercise 5-6 -- p advances through
//s directly instead of indexing s[i])
int my_getline(char *s, int lim)
{
    int c;
    char *p = s;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        *p++ = c;
    if (c == '\n')
        *p++ = c;
    *p = '\0';
    return p - s;
}

//alloc:  return pointer to n characters, carved out of one static
//buffer -- a bare-bones allocator (no free()) that just advances a
//pointer through a fixed block; returns NULL if the block is full
static char allocbuf[ALLOCSIZE];
static char *allocp = allocbuf;

char *alloc(int n)
{
    if (allocbuf + ALLOCSIZE - allocp >= n) {  //enough room left?
        allocp += n;
        return allocp - n;   //old p, before advancing
    } else
        return NULL;
}

//my_qsort:  sort v[left]...v[right] into increasing order --
//section 5.1's int-array qsort, unchanged in STRUCTURE; only the
//comparison changed (strcmp instead of <) because these are strings
void my_qsort(char *v[], int left, int right)
{
    int i, last;

    if (left >= right)      //do nothing if array contains
        return;             //fewer than two elements
    swap(v, left, (left + right)/2);
    last = left;
    for (i = left + 1; i <= right; i++)
        if (strcmp(v[i], v[left]) < 0)
            swap(v, ++last, i);
    swap(v, left, last);
    my_qsort(v, left, last-1);
    my_qsort(v, last+1, right);
}

//swap:  interchange v[i] and v[j] -- same idea as section 5.1's swap,
//just moving a char* (a pointer to where a line lives) instead of an int
void swap(char *v[], int i, int j)
{
    char *temp;
    temp = v[i];
    v[i] = v[j];
    v[j] = temp;
}

*/
/*

#include <stdio.h>
#include <ctype.h>
#include <string.h>   //for strlen() in my_reverse/my_getline's return-length parity check
#include <stdlib.h>   //for the real atoi(), to check my_atoi against
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 5-6: rewrite appropriate programs from earlier chapters
//with pointers instead of array indexing. Picked four of the book's own
//suggestions: atoi (ch2), the iterative itoa + reverse pair (ch3 --
//distinct from exercise 4-12/4-13's RECURSIVE versions, which never
//used indices to begin with), and getline (ch1/ch4).
//
//The general translation pattern, the same in all four: everywhere the
//array version had `s[i]` and incremented `i`, the pointer version
//keeps a pointer INTO s and increments the pointer itself instead --
//the position and the access become the same operation. Nothing about
//WHAT gets computed changes; only how "the next character" is reached.

//my_atoi: ch2's array-index version used s[i] and an index i throughout;
//here *s IS the current character, and s++ IS "look at the next one".
int my_atoi(char *s)
{
    int n, sign;

    while (isspace((unsigned char)*s))   //skip leading white space
        s++;
    sign = (*s == '-') ? -1 : 1;
    if (*s == '+' || *s == '-')
        s++;
    for (n = 0; isdigit((unsigned char)*s); s++)
        n = 10 * n + (*s - '0');
    return sign * n;
}

//my_reverse: ch3's version used two indices i (from the front) and j
//(from the back), swapping s[i]/s[j] while i<j. Here two POINTERS do
//the same job -- one starts at s, the other at s's last real character
//-- and they walk toward each other instead of two indices doing it.
void my_reverse(char *s)
{
    char *end = s + strlen(s) - 1;
    char c;

    while (s < end) {
        c = *s;
        *s++ = *end;
        *end-- = c;
    }
}

//my_itoa: ch3's version built digits least-significant-first via s[i++],
//then called reverse() at the end because that order comes out backwards
//-- this pointer version does the exact same thing, just writing through
//a moving pointer p instead of indexing s[i++].
void my_itoa(int n, char *s)
{
    int sign;
    char *p = s;

    if ((sign = n) < 0)
        n = -n;
    do {
        *p++ = n % 10 + '0';
    } while ((n /= 10) > 0);
    if (sign < 0)
        *p++ = '-';
    *p = '\0';
    my_reverse(s);
}

//my_getline: ch1/ch4's version indexed s[i] up to lim-1 characters. This
//walks a pointer p forward instead, and reports the count it copied as
//p - s (pointer subtraction -- the distance between two pointers into
//the SAME array, in elements) instead of returning the index i directly.
int my_getline(char *s, int lim)
{
    int c;
    char *p = s;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        *p++ = c;
    if (c == '\n')
        *p++ = c;
    *p = '\0';
    return p - s;
}

int main(void)
{
    char buf[50];
    int i;

    printf("--- my_atoi vs library atoi ---\n");
    char *nums[] = {"123", "  -456", "+789", "   42abc", "-0"};
    int nn = sizeof(nums) / sizeof(nums[0]);
    for (i = 0; i < nn; i++) {
        int mine = my_atoi(nums[i]);
        int lib = atoi(nums[i]);
        printf("\"%s\" -> mine=%d lib=%d  %s\n",
               nums[i], mine, lib, mine == lib ? "ok" : "FAIL");
    }

    printf("\n--- my_itoa then my_atoi (round trip) ---\n");
    int vals[] = {0, 7, -7, 123, -8400, 2147483647};
    int nv = sizeof(vals) / sizeof(vals[0]);
    for (i = 0; i < nv; i++) {
        my_itoa(vals[i], buf);
        int back = my_atoi(buf);
        printf("%d -> \"%s\" -> %d  %s\n",
               vals[i], buf, back, back == vals[i] ? "ok" : "FAIL");
    }

    printf("\n--- my_reverse, applied twice returns the original ---\n");
    char *words[] = {"", "a", "hello, world", "abcd"};
    int nw = sizeof(words) / sizeof(words[0]);
    for (i = 0; i < nw; i++) {
        strcpy(buf, words[i]);
        my_reverse(buf);
        printf("\"%s\" -> \"%s\"", words[i], buf);
        my_reverse(buf);
        printf(" -> \"%s\"  %s\n", buf, strcmp(buf, words[i]) == 0 ? "ok" : "FAIL");
    }

    printf("\n--- my_getline on piped stdin ---\n");
    int len;
    while ((len = my_getline(buf, sizeof(buf))) > 0)
        printf("len=%d  \"%s\"\n", len, buf);

    return 0;
}

*/

/*

#include <stdio.h>
#include <string.h>   //only for the reference strncpy/strncat/strncmp and memset in main
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 5-5: write versions of the library functions strncpy,
//strncat, and strncmp, which operate on at most the first n characters
//of their argument strings. (Appendix B has the full descriptions.)
//
//The three behaviors that are easy to get wrong -- all taken from
//Appendix B, and all checked against the real library in main():
//
//  strncpy(s, ct, n)  copies at most n characters of ct to s, and PADS
//                     s with '\0' out to n characters if ct is shorter.
//                     If ct has n or more characters it does NOT
//                     terminate s -- a famous trap, kept on purpose.
//  strncat(s, ct, n)  appends at most n characters of ct to s and ALWAYS
//                     terminates s with '\0' (so it may write n+1 bytes
//                     past the old end -- unlike strncpy).
//  strncmp(cs, ct, n) compares at most n characters, stops early at a
//                     '\0', and compares as UNSIGNED chars, so a byte
//                     like 0xe9 sorts above 'a' even where plain char
//                     is signed (checked by the last test case).
//
//Every loop is driven by the pointers and the countdown n -- no indices.
//Each function takes const char * for the source it only reads, so the
//compiler stops it from ever writing through that pointer.
char *my_strncpy(char *s, const char *ct, size_t n)
{
    char *start = s;       //s itself will move; remember where it began

    while (n > 0 && *ct) { //copy real characters
        *s++ = *ct++;
        n--;
    }
    while (n > 0) {        //ct ran out first: pad with '\0'
        *s++ = '\0';
        n--;
    }
    return start;
}

char *my_strncat(char *s, const char *ct, size_t n)
{
    char *start = s;

    while (*s)             //find end of s
        s++;
    while (n > 0 && *ct) { //append at most n characters
        *s++ = *ct++;
        n--;
    }
    *s = '\0';             //always terminate, even when n == 0
    return start;
}

int my_strncmp(const char *cs, const char *ct, size_t n)
{
    for (; n > 0; cs++, ct++, n--) {
        if ((unsigned char)*cs != (unsigned char)*ct)
            return (unsigned char)*cs - (unsigned char)*ct;
        if (*cs == '\0')   //both ended together, equal so far
            return 0;
    }
    return 0;              //n characters compared, all equal (or n == 0)
}

static void show(const char *b, int len)   //'\0' shown as '.' so padding is visible
{
    int i;

    putchar('[');
    for (i = 0; i < len; i++)
        putchar(b[i] ? b[i] : '.');
    putchar(']');
}

static int sign(int x)
{
    return (x > 0) - (x < 0);
}

int main(void)
{
    size_t ns[] = {0, 3, 5, 8};
    int nn = sizeof(ns) / sizeof(ns[0]);
    int i;

    printf("--- strncpy(s, \"hello\", n) into a buffer pre-filled with X ---\n");
    for (i = 0; i < nn; i++) {
        char mine[12], lib[12];
        char *r;

        memset(mine, 'X', sizeof(mine));
        memset(lib, 'X', sizeof(lib));
        r = my_strncpy(mine, "hello", ns[i]);
        strncpy(lib, "hello", ns[i]);
        printf("n=%zu  ", ns[i]);
        show(mine, 12);
        printf("  %s\n", (r == mine && memcmp(mine, lib, 12) == 0) ? "ok" : "FAIL");
    }

    printf("\n--- strncat(\"ab\", \"cdefgh\", n) ---\n");
    for (i = 0; i < nn; i++) {
        char mine[20] = "ab";
        char lib[20] = "ab";
        char *r;

        r = my_strncat(mine, "cdefgh", ns[i]);
        strncat(lib, "cdefgh", ns[i]);
        printf("n=%zu  ", ns[i]);
        show(mine, 12);
        printf("  %s\n", (r == mine && memcmp(mine, lib, 20) == 0) ? "ok" : "FAIL");
    }

    printf("\n--- strncmp(a, b, n): sign of result, mine vs library ---\n");
    {
        char *a[] = {"abc", "abc", "abc", "", "abc", "a", "\xe9"};
        char *b[] = {"abd", "abd", "ab",  "", "abc", "b", "a"};
        size_t cn[] = {2,     3,     3,    5,  100,   0,   1};
        int nc = sizeof(cn) / sizeof(cn[0]);

        for (i = 0; i < nc; i++) {
            int m = sign(my_strncmp(a[i], b[i], cn[i]));
            int l = sign(strncmp(a[i], b[i], cn[i]));

            printf("n=%-3zu mine=%2d lib=%2d  %s\n", cn[i], m, l, m == l ? "ok" : "FAIL");
        }
    }

    return 0;
}

*/

/*

#include <stdio.h>
#include <string.h>   //for strlen()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 5-4: write the function strend(s, t), which returns 1 if
//the string t occurs at the end of the string s, and zero otherwise.
//
//Idea: if t is longer than s it can't fit, so the answer is 0. Otherwise
//t can only match if it lines up with the LAST strlen(t) characters of
//s, so skip s forward by (strlen(s) - strlen(t)) -- after that, s and t
//have exactly the same number of characters left, and the match is a
//plain character-by-character comparison, stopping at the first
//difference. No indices anywhere: s and t are advanced directly, and
//`*t` is the loop condition because it is zero exactly when t has been
//fully consumed.
//
//Edge case worth stating on purpose: an empty t returns 1. The empty
//string is (vacuously) at the end of every string, the same convention
//the library's strstr/strcmp-style functions follow.
int strend(char *s, char *t)
{
    size_t ls = strlen(s);
    size_t lt = strlen(t);

    if (lt > ls)
        return 0;          //t is longer than s -- can't fit
    s += ls - lt;          //skip to where t would have to start
    while (*t)
        if (*s++ != *t++)
            return 0;      //first mismatch
    return 1;
}

int main(void)
{
    char *tests[][2] = {
        {"hello world", "world"},   //1: normal match
        {"hello world", "hello"},   //0: t is at the START, not the end
        {"abc", "xabc"},            //0: t longer than s
        {"same", "same"},           //1: t equals s
        {"anything", ""},           //1: empty t
        {"", "x"},                  //0: empty s, non-empty t
        {"", ""},                   //1: both empty
        {"abcabc", "bc"},           //1: repeated text, matches at the end
        {"abcabc", "ab"},           //0: occurs, but not at the end
        {"xxabc", "yabc"},          //0: only the first character differs
    };
    int n = sizeof(tests) / sizeof(tests[0]);
    int i;

    for (i = 0; i < n; i++)
        printf("strend(\"%s\", \"%s\") = %d\n",
               tests[i][0], tests[i][1], strend(tests[i][0], tests[i][1]));

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 5-3: write a pointer version of the function strcat
//shown in Chapter 2 -- strcat(s, t) copies the string t to the end of s.
//
//Chapter 2's array version, for comparison:
//
//    void strcat(char s[], char t[])
//    {
//        int i, j;
//        i = j = 0;
//        while (s[i] != '\0')       //find end of s
//            i++;
//        while ((s[i++] = t[j++]) != '\0')   //copy t
//            ;
//    }
//
//It needs two integer indices because s and t each have their own
//position. With pointers, the position IS the pointer -- s and t
//themselves walk forward, so both indices disappear.
//
//`while (*s) s++;`  -- *s is the character s currently points at, which
//is zero ('\0') only at the end of the string, so the loop stops with s
//pointing AT the terminating '\0' (exactly where t's first character
//needs to land).
//
//`while ((*s++ = *t++)) ;`  -- ++ binds tighter than *, so *s++ means
//"the character s points at, then advance s". The assignment copies one
//character from t to s and the assignment expression's own value is
//the character just copied -- so the loop ends right after copying the
//'\0', the copy of the terminator is part of the job, not a separate
//step. The extra pair of parentheses only silences the compiler's "did
//you mean ==?" warning; the = is intentional.
//
//The caller's own s (in main) is never moved: C passes s by value, so
//my_strcat is advancing a private COPY of the pointer -- the same
//pass-by-value fact from the swap discussion, working in our favor here.
//
//Named my_strcat so it can't clash with the library's strcat.
void my_strcat(char *s, char *t)
{
    while (*s)         //find end of s
        s++;
    while ((*s++ = *t++))   //copy t, including its '\0'
        ;
}

int main(void)
{
    char a[50] = "hello, ";
    char b[50] = "";
    char c[50] = "unchanged";
    char d[50] = "";

    my_strcat(a, "world");    //normal case
    my_strcat(b, "into empty");   //s is empty
    my_strcat(c, "");         //t is empty
    my_strcat(d, "");         //both empty

    printf("[%s]\n[%s]\n[%s]\n[%s]\n", a, b, c, d);

    return 0;
}

*/

/*

#include <stdio.h>
#include <ctype.h>

//K&R2 exercise 5-2: write getfloat, the floating-point analog of
//getint. What type does getfloat return as its function value?
//
//Answer: int -- same reason as getint. getfloat's own return value is
//STATUS (EOF / 0-not-a-number / last character read), never the parsed
//number itself; the parsed number travels back through the double *pn
//pointer parameter instead. EOF is an int constant, so if getfloat
//returned double directly there'd be no safe sentinel value to signal
//end-of-input with -- any double value it picked could collide with a
//legitimate number someone typed. Splitting "the answer" (via pointer)
//from "how it went" (via return value) is the only way to hand back
//both without that ambiguity, same design getint already uses.
//
//Structure mirrors getint almost exactly: skip whitespace, reject
//anything that isn't a possible number start (now including '.', since
//".5" is a valid float getint never had to worry about), handle an
//optional sign, then accumulate digits. The only new part is the
//fractional half: after an optional '.', digits keep accumulating into
//the SAME running total (as if the decimal point weren't there), while
//`power` tracks 10^(number of fractional digits seen) so the final
//division puts the point back in the right place -- "3.14" accumulates
//as 314 with power=100, then 314/100 = 3.14.
//
//Note: this is deliberately the ORIGINAL, not-yet-hardened getint
//pattern for the sign check (matching what the exercise asks -- the
//"analog of getint" as first presented, before exercise 5-1's fix) --
//so getfloat inherits that same +/- edge case for now, on purpose.
#define BUFSIZE 100

char buf[BUFSIZE];   //buffer for ungetch
int bufp = 0;        //next free position in buf

int getch(void)      //get a (possibly pushed-back) character
{
    return (bufp > 0) ? buf[--bufp] : getchar();
}

void ungetch(int c)  //push character back on input
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters\n");
    else
        buf[bufp++] = c;
}

//getfloat:  get next floating-point number from input into *pn
int getfloat(double *pn)
{
    int c, sign;
    double power;

    while (isspace(c = getch()))   //skip white space
        ;
    if (!isdigit(c) && c != EOF && c != '+' && c != '-' && c != '.') {
        ungetch(c);   //it is not a number
        return 0;
    }
    sign = (c == '-') ? -1 : 1;
    if (c == '+' || c == '-')
        c = getch();
    for (*pn = 0.0; isdigit(c); c = getch())   //integer part
        *pn = 10.0 * *pn + (c - '0');
    if (c == '.')
        c = getch();
    for (power = 1.0; isdigit(c); c = getch()) {   //fractional part
        *pn = 10.0 * *pn + (c - '0');
        power *= 10.0;
    }
    *pn = sign * *pn / power;
    if (c != EOF)
        ungetch(c);
    return c;
}

int main(void)
{
    double n;
    int ret;

    while ((ret = getfloat(&n)) != EOF) {
        if (ret == 0) {
            int bad = getch();   //not a number -- see what was really there
            printf("getfloat returned 0 (not a number) -- pushed-back "
                   "char is '%c' (%d)\n", isprint(bad) ? bad : '?', bad);
        } else {
            printf("getfloat returned %-4d  n = %g\n", ret, n);
        }
    }

    return 0;
}

*/

/*

#include <stdio.h>
#include <ctype.h>

//K&R2 exercise 5-1: as written, getint treats a + or - not followed by
//a digit as a valid representation of zero. Fix it to push such a
//character back on the input.
//
//The bug: after seeing '+' or '-', the old code unconditionally did
//`c = getch()` and assumed the result was a digit. If it wasn't, the
//for loop's isdigit(c) failed on the FIRST check, so *pn stayed 0 and
//the function returned as if "0" had legitimately been typed -- while
//silently swallowing the sign character forever (it was already
//consumed by the getch() above and never pushed back).
//
//The fix: check isdigit(c) right after that getch(). If it fails, push
//the non-digit character back (so the next read still sees it), THEN
//push the sign character back too, and return 0 -- same "not a number"
//signal getint already uses elsewhere, but now the input stream is
//left exactly as if getint had never touched it.
//
//Order matters for the double push-back: ungetch's buffer is LIFO (last
//pushed is first read back), so to make '+' come out again BEFORE the
//character after it, the non-digit has to be pushed FIRST and the sign
//pushed SECOND -- pushing sign last means it's popped first.
#define BUFSIZE 100

char buf[BUFSIZE];   //buffer for ungetch
int bufp = 0;        //next free position in buf

int getch(void)      //get a (possibly pushed-back) character
{
    return (bufp > 0) ? buf[--bufp] : getchar();
}

void ungetch(int c)  //push character back on input
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters\n");
    else
        buf[bufp++] = c;
}

//getint:  get next integer from input into *pn
int getint(int *pn)
{
    int c, sign;

    while (isspace(c = getch()))   //skip white space
        ;
    if (!isdigit(c) && c != EOF && c != '+' && c != '-') {
        ungetch(c);   //it is not a number
        return 0;
    }
    sign = (c == '-') ? -1 : 1;
    if (c == '+' || c == '-') {
        c = getch();
        if (!isdigit(c)) {              //sign wasn't followed by a digit
            if (c != EOF)
                ungetch(c);              //push back what came after the sign
            ungetch(sign == -1 ? '-' : '+');  //then push back the sign itself
            return 0;
        }
    }
    for (*pn = 0; isdigit(c); c = getch())
        *pn = 10 * *pn + (c - '0');
    *pn *= sign;
    if (c != EOF)
        ungetch(c);
    return c;
}

int main(void)
{
    int n, ret;

    while ((ret = getint(&n)) != EOF) {
        if (ret == 0) {
            //not a number -- pull the pushed-back character back off to
            //show it really is intact (the old buggy version would have
            //silently reported n=0 here instead of exposing this)
            int bad = getch();
            printf("getint returned 0 (not a number) -- pushed-back "
                   "char is '%c' (%d)\n", isprint(bad) ? bad : '?', bad);
        } else {
            printf("getint returned %-4d  n = %d\n", ret, n);
        }
    }

    return 0;
}

*/

/*

#include <stdio.h>
#include <ctype.h>

//K&R2 section 5.2: getint, the pointer-argument counterpart to getch's
//getfloat sibling -- reads the next integer from input into *pn, and
//returns EOF at end of input, or otherwise the last character read
//(non-digit, whitespace-terminator, or a sign that turned out not to
//lead a number).
//
//getint NEEDS to take a pointer here, for the exact reason covered
//earlier this week: it has to hand back TWO things -- the parsed value,
//AND whether/how parsing ended -- and a C function can only `return`
//one. Taking int *pn lets it write the parsed value through the
//pointer (into the CALLER's variable) while still using its actual
//return value for status, the same pattern as scanf.
//
//getch/ungetch are K&R2's one-character-pushback pair (section 4.3),
//needed here because getint has to peek one character ahead to decide
//"is this actually a number" before it knows whether to consume it.
#define BUFSIZE 100

char buf[BUFSIZE];   //buffer for ungetch
int bufp = 0;        //next free position in buf

int getch(void)      //get a (possibly pushed-back) character
{
    return (bufp > 0) ? buf[--bufp] : getchar();
}

void ungetch(int c)  //push character back on input
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters\n");
    else
        buf[bufp++] = c;
}

//getint:  get next integer from input into *pn
int getint(int *pn)
{
    int c, sign;

    while (isspace(c = getch()))   //skip white space
        ;
    if (!isdigit(c) && c != EOF && c != '+' && c != '-') {
        ungetch(c);   //it is not a number
        return 0;
    }
    sign = (c == '-') ? -1 : 1;
    if (c == '+' || c == '-')
        c = getch();
    for (*pn = 0; isdigit(c); c = getch())   //corrected from the pasted
        *pn = 10 * *pn + (c - '0');           //text's ", " -- see note
                                                //at the top of this block
    *pn *= sign;
    if (c != EOF)
        ungetch(c);
    return c;
}

int main(void)
{
    int n, ret;

    while ((ret = getint(&n)) != EOF)
        printf("getint returned %-4d  n = %d\n", ret, n);

    return 0;
}

*/

/*

#include <stdio.h>

//K&R2 exercise 4-14: define a macro swap(t,x,y) that interchanges two
//arguments of type t. (Block structure will help.)
//
//"Block structure will help" points at wrapping the temp variable in
//its own { } scope -- that way swap's tmp can't collide with a real
//variable named tmp at the call site, and each expansion gets its own
//fresh tmp of whatever type t is, so the same macro works for int,
//double, char, or any other type without tmp being declared just once
//at some fixed type.
#define swap(t, x, y) { t tmp; tmp = x; x = y; y = tmp; }

int main(void)
{
    int a = 3, b = 7;
    double p = 1.5, q = 9.25;
    char c1 = 'A', c2 = 'Z';

    printf("before: a=%d b=%d\n", a, b);
    swap(int, a, b);
    printf("after:  a=%d b=%d\n\n", a, b);

    printf("before: p=%g q=%g\n", p, q);
    swap(double, p, q);
    printf("after:  p=%g q=%g\n\n", p, q);

    printf("before: c1=%c c2=%c\n", c1, c2);
    swap(char, c1, c2);
    printf("after:  c1=%c c2=%c\n", c1, c2);

    return 0;
}

*/

/*

#include <stdio.h>
#define FOCUS 1
#define SQUARE(x) ((x) * (x))

int main() {
    int a = 5;
    #ifdef FOCUS
        printf("Focus mode is ON. Square of %d is %d.\n", a,
SQUARE(a));
    #else
        printf("Focus mode is OFF.\n");
    #endif
    return 0;
}

*/

/*

#include <stdio.h>
#include <string.h>   //for strlen()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 4-13: write a recursive version of reverse(s), which
//reverses the string s in place.
//
//"In place" rules out building a second string and copying it back --
//the classic in-place swap technique is two indices closing in from
//opposite ends, swapping and stepping inward until they meet or cross.
//Recursion replaces the loop that would normally drive that stepping:
//each call handles one swap, then recurses with left+1/right-1, exactly
//like my_qsort's recursive calls narrow the [left, right] range each
//time instead of looping.
//
//reverse() itself takes just the string, same signature the exercise
//names -- it calls the length-and-bounds-aware helper once with the
//full range, since the base recursive step needs both ends' indices,
//not just the array.
void reverse_rec(char s[], int left, int right);

void reverse(char s[])
{
    reverse_rec(s, 0, strlen(s) - 1);
}

//reverse_rec: swap s[left] and s[right], then recurse inward
//base case: left >= right means the range has 0 or 1 characters left,
//nothing left to swap (odd-length strings naturally leave one character
//untouched in the middle -- swapping it with itself would be a no-op
//anyway, so left == right doesn't need separate handling)
void reverse_rec(char s[], int left, int right)
{
    char temp;

    if (left >= right)
        return;
    temp = s[left];
    s[left] = s[right];
    s[right] = temp;
    reverse_rec(s, left + 1, right - 1);
}

int main(void)
{
    char tests[][20] = {"", "a", "ab", "abc", "abcd", "hello, world"};
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;

    for (i = 0; i < ntests; i++) {
        printf("\"%s\" -> ", tests[i]);
        reverse(tests[i]);
        printf("\"%s\"\n", tests[i]);
    }
    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 4-12: adapt the ideas of printd (recursive digit
//printing) to write a recursive itoa -- convert an int to a string by
//calling a recursive routine.
//
//printd's own structure: peel off the sign and negate n if needed, then
//recurse on n/10 BEFORE emitting n%10 -- so the *last* thing printd does
//is print the least-significant digit, meaning digits come out
//most-significant-first purely because recursion unwinds outermost-last.
//That's exactly the trick this reuses: itoa_rec recurses on n/10 before
//writing n%10 into s[i], so the string ends up in the correct left-to-
//right order with no separate reverse() step -- unlike section 3.6's
//iterative itoa, which builds digits least-significant-first and has to
//reverse the whole string afterward as a second pass.
//
//itoa_rec threads the write position forward as a return value (the
//index just past the last character written) instead of a global/static
//counter, since each recursive call needs to know where the call below
//it left off before it can write its own digit after that point.
static int itoa_rec(int n, char s[], int i)
{
    if (n < 0) {
        s[i++] = '-';
        n = -n;      //same simplification printd itself makes -- this
                       //doesn't hold for INT_MIN, whose negation
                       //overflows int; not tested below for that reason
    }
    if (n / 10)                    //more digits above this one?
        i = itoa_rec(n / 10, s, i);  //emit those first (most significant)
    s[i++] = n % 10 + '0';         //then this digit, last -- placed
                                     //AFTER the recursive call returns,
                                     //same ordering trick as printd's
                                     //putchar(n % 10 + '0') coming after
                                     //its own recursive printd(n / 10)
    return i;
}

//my_itoa: convert n to its string representation, stored in s
//(s must be large enough -- no bound is passed, same as K&R2's own itoa)
void my_itoa(int n, char s[])
{
    s[itoa_rec(n, s, 0)] = '\0';
}

int main(void)
{
    int tests[] = {0, 7, -7, 123, -123, 8400, -8400, 2147483647};
    int ntests = sizeof(tests) / sizeof(tests[0]);
    char s[20];
    int i;

    for (i = 0; i < ntests; i++) {
        my_itoa(tests[i], s);
        printf("%d -> \"%s\"\n", tests[i], s);
    }
    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 5.1: the quicksort example as printed in the book, using
//array-subscript notation throughout -- the "before" version, ahead of
//the pointer rewrite the chapter builds to.
//
//Renamed qsort -> my_qsort because <stdlib.h> already declares a
//standard-library qsort() with a different signature -- same reason
//my_getline exists further down in this file instead of getline.
void my_qsort(int v[], int left, int right);
void swap(int v[], int i, int j);

int main(void)
{
    int v[] = {5, 2, 9, 1, 5, 6, 3, 8, 7, 4};
    int n = sizeof(v) / sizeof(v[0]);
    int i;

    printf("before: ");
    for (i = 0; i < n; i++)
        printf("%d ", v[i]);
    printf("\n");

    my_qsort(v, 0, n - 1);

    printf("after:  ");
    for (i = 0; i < n; i++)
        printf("%d ", v[i]);
    printf("\n");

    return 0;
}

//my_qsort:  sort v[left]...v[right] into increasing order
void my_qsort(int v[], int left, int right)
{
    int i, last;

    if (left >= right)      //do nothing if array contains
        return;             //fewer than two elements
    swap(v, left, (left + right)/2);  //move partition elem
    last = left;                       //to v[0]
    for (i = left + 1; i <= right; i++)  //partition
        if (v[i] < v[left])
            swap(v, ++last, i);
    swap(v, left, last);    //restore partition elem
    my_qsort(v, left, last-1);
    my_qsort(v, last+1, right);
}

//swap:  interchange v[i] and v[j]
void swap(int v[], int i, int j)
{
    int temp;
    temp = v[i];
    v[i] = v[j];
    v[j] = temp;
}

*/

/*

#include <stdio.h>
#include <stdlib.h>   //for atof()
#include <string.h>   //for strcmp()
#include <ctype.h>
#include <math.h>     //for fmod() and the whole WORD dispatch's functions
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c -lm

#define MAXOP    100  //max size of operand or operator
#define NUMBER   '0'  //signal that a number was found
#define WORD     'W'  //signal that an alphabetic word was found

int getop(char []);
void push(double);
double pop(void);
extern int sp;
extern double val[];

//K&R2 exercise 4-11: modify getop so it doesn't need ungetch at all --
//hint given by the book: use an internal static variable.
//
//This is a DIFFERENT answer to "how do we stop needing pushback" than
//exercise 4-10's (archived just below): 4-10 solved it by changing WHERE
//getop reads from -- a whole line sitting in an array, where "peek ahead"
//is just indexing and nothing is ever truly consumed. This exercise
//keeps reading one character at a time from getchar(), exactly like the
//original getch()/ungetch() design (archived further below, from
//exercise 4-6/4-9) -- what changes is WHO remembers the peeked-ahead
//character.
//
//getch()/ungetch() needed a whole separate facility (buf[]/bufp, or one
//int in exercise 4-8's version) because pushback had to work for ANY
//caller, generically -- ungetch() had no idea who would call getch()
//next or why. But getop() is the ONLY function in this program that ever
//peeks ahead. There's no other caller to support. So instead of routing
//the deferred character through a general-purpose external mechanism,
//getop() just keeps ONE int of its own state between calls, via `static
//int lastc` -- a variable that's local to getop() (nothing outside this
//function can see or touch it, same privacy any local variable has) but,
//being static, PERSISTS its value across separate calls instead of
//resetting to garbage every time getop() is entered (exactly what
//"static" buys a local variable -- the same reason variables[] was
//static two exercises ago in main(): persistence between calls, not
//global visibility).
//
//The sentinel is EOF, not 0 -- the exact same design already proven in
//exercise 4-8's one-slot getch/ungetch (archived further below): EOF is
//never a real character that legitimately needs deferring (getop never
//saves it into lastc in the first place -- see every "if (c != EOF)"
//guard below), so "lastc == EOF" safely means "nothing pending, read a
//fresh character," with no separate flag needed. Using 0 instead would
//have been the wrong sentinel: '\0'/0 IS a value getchar() can
//legitimately return from real input, so it can't double as "empty."
//
//Net effect: getch() and ungetch() are gone completely -- not
//simplified, GONE -- along with buf[]/bufp/BUFSIZE. Every place that
//used to call ungetch(c) now just does `lastc = c` (deferring, exactly
//like before) instead of handing it to an external facility; every place
//that used to call getch() now checks lastc first, same idea as
//getch()'s own "pushback slot first, getchar() otherwise" logic, just
//folded directly into getop() since it's the only one who needs it.
//
//Only getop() changes. main(), push/pop, and the whole WORD dispatch
//below are byte-for-byte identical to exercise 4-6 -- same as 4-10,
//proof that BOTH exercises are isolated to HOW tokens are read, just via
//two structurally different mechanisms.
int main(void)
{
    int type, lastvar = -1;   //index (0-25) of the most recently
                               //referenced variable letter, for '=' to
                               //know its target; -1 means "none yet"
    double op2, result, lastprint = 0.0;
    char s[MAXOP];
    static double variables[26];  //static, not just local -- guarantees
                                   //automatic zero-init (a plain local
                                   //array would start with garbage);
                                   //only main() ever touches this, so
                                   //it doesn't need to be a true global

    while ((type = getop(s)) != EOF) {
        switch (type) {
        case NUMBER:
            push(atof(s));
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
        case '%':
            op2 = pop();
            if (op2 != 0.0)
                push(fmod(pop(), op2));
            else
                printf("error: zero divisor\n");
            break;
        case WORD:
            if (s[1] == '\0' && islower((unsigned char) s[0])) {
                lastvar = s[0] - 'a';       //remember for a following '='
                push(variables[lastvar]);   //read: push its current value
            }
            else if (strcmp(s, "sin") == 0)
                push(sin(pop()));
            else if (strcmp(s, "cos") == 0)
                push(cos(pop()));
            else if (strcmp(s, "tan") == 0)
                push(tan(pop()));
            else if (strcmp(s, "asin") == 0)
                push(asin(pop()));
            else if (strcmp(s, "acos") == 0)
                push(acos(pop()));
            else if (strcmp(s, "atan") == 0)
                push(atan(pop()));
            else if (strcmp(s, "exp") == 0)
                push(exp(pop()));
            else if (strcmp(s, "log") == 0)
                push(log(pop()));
            else if (strcmp(s, "log10") == 0)
                push(log10(pop()));
            else if (strcmp(s, "sqrt") == 0)
                push(sqrt(pop()));
            else if (strcmp(s, "cbrt") == 0)
                push(cbrt(pop()));
            else if (strcmp(s, "floor") == 0)
                push(floor(pop()));
            else if (strcmp(s, "ceil") == 0)
                push(ceil(pop()));
            else if (strcmp(s, "fabs") == 0)
                push(fabs(pop()));
            else if (strcmp(s, "pow") == 0) {
                op2 = pop();               //exponent, popped first --
                push(pow(pop(), op2));     //same convention as '-'/'/'
            } else if (strcmp(s, "print") == 0) {   //print top, don't remove
                if (sp > 0)
                    printf("\t%.8g\n", val[sp-1]);
                else
                    printf("error: stack empty\n");
            } else if (strcmp(s, "dup") == 0) {     //duplicate top
                if (sp > 0)
                    push(val[sp-1]);
                else
                    printf("error: stack empty\n");
            } else if (strcmp(s, "swap") == 0) {    //swap top two
                if (sp >= 2) {
                    double tmp = val[sp-1];
                    val[sp-1] = val[sp-2];
                    val[sp-2] = tmp;
                } else
                    printf("error: need two elements to swap\n");
            } else if (strcmp(s, "clear") == 0) {   //clear the stack
                sp = 0;
            } else
                printf("error: unknown word %s\n", s);
            break;
        case '=':                    //assign: "value letter ="
            if (lastvar < 0)
                printf("error: no variable named before '='\n");
            else {
                pop();                          //discard the value the
                                                 //letter itself just
                                                 //pushed when it was read
                variables[lastvar] = pop();     //the value to store
            }
            break;
        case '$':                    //push the most recently PRINTED value
            push(lastprint);
            break;
        case '\n':
            result = pop();
            lastprint = result;
            printf("\t%.8g\n", result);
            break;
        default:
            printf("error: unknown command %s\n", s);
            break;
        }
    }
    return 0;
}

#define MAXVAL  100   //maximum depth of val stack

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

//getop:  get next character, numeric operand, or alphabetic word -- no
//getch()/ungetch() anywhere; a single static int (lastc) remembers one
//character of lookahead between calls, entirely private to this function
int getop(char s[])
{
    int i, c;
    static int lastc = EOF;   //one character of lookahead saved from the
                               //PREVIOUS call to getop, or EOF if none is
                               //pending -- persists across calls because
                               //it's static, but no other function can
                               //see or touch it, because it's still local

    if (lastc != EOF) {       //a previous call left a character for us
        c = lastc;
        lastc = EOF;           //slot is empty again
    } else {
        c = getchar();
    }
    while (c == ' ' || c == '\t')
        c = getchar();         //blanks/tabs are simply never saved back
    s[0] = c;
    s[1] = '\0';
    i = 0;

    if (c == '-') {
        c = getchar();
        if (!isdigit(c) && c != '.') {
            if (c != EOF)
                lastc = c;      //defer it for the NEXT getop() call --
                                 //this replaces every old ungetch(c)
            return s[0];        //just the '-' operator
        }
        s[++i] = c;             //fold the first digit/'.' in after the sign
    } else if (isalpha(c)) {    //a function name or single-letter command
        while (isalnum(s[++i] = c = getchar()))
            ;
        s[i] = '\0';
        if (c != EOF)
            lastc = c;
        return WORD;
    } else if (!isdigit(c) && c != '.') {
        return c;               //not a number, not a word
    }

    if (isdigit(c))  //collect integer part
        while (isdigit(s[++i] = c = getchar()))
            ;
    if (c == '.')    //collect fraction part
        while (isdigit(s[++i] = c = getchar()))
            ;
    s[i] = '\0';
    if (c != EOF)
        lastc = c;
    return NUMBER;
}

*/

/*

#include <stdio.h>
#include <stdlib.h>   //for atof()
#include <string.h>   //for strcmp()
#include <ctype.h>
#include <math.h>     //for fmod() and the whole WORD dispatch's functions
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c -lm

#define MAXOP    100  //max size of operand or operator
#define NUMBER   '0'  //signal that a number was found
#define WORD     'W'  //signal that an alphabetic word was found
#define MAXLINE 1000  //maximum input line length

int getop(char []);
void push(double);
double pop(void);
int my_getline(char [], int);
extern int sp;
extern double val[];

char line[MAXLINE];   //the current input line, fetched a whole line at
                       //a time instead of one getch() at a time
int lineindex = 0;    //index of the next character in line[] that
                       //getop hasn't consumed yet
int linelen = 0;        //how many real characters my_getline actually
                         //put into line[] (its return value)

//K&R2 exercise 4-10: read a whole line at a time with my_getline
//(the SAME function from section 4.1's pattern-search example, unchanged)
//instead of one character at a time with getch -- which, per the
//exercise, makes getch/ungetch/buf/bufp completely unnecessary.
//
//Why unnecessary, concretely: getch/ungetch existed for exactly one
//reason -- to let getop READ one character ahead to see where a number
//or word ends, then GIVE THAT CHARACTER BACK so the next getop() call
//sees it fresh. That "giving back" was only hard because each
//character, once read via getchar(), was gone from the input stream
//forever unless explicitly saved somewhere (buf[]) for next time.
//
//With the whole line sitting in line[] as an array, that problem
//doesn't exist in the first place: "reading ahead" is just looking at
//line[lineindex+1] without touching lineindex, and "giving a character
//back" is just... not advancing lineindex past it. Nothing was ever
//consumed or discarded, only walked past -- there's no separate buffer
//to manage because the data was never removed from where it already
//was. That's the actual lesson here, not just "fewer functions": a
//pushback mechanism is only needed when reading is inherently
//destructive (one-shot, like getchar()); an in-memory array was never
//destructive to begin with.
//
//Only getop() changes. main(), push/pop, and the whole WORD dispatch
//below are byte-for-byte identical to exercise 4-6 -- proof that this
//redesign is entirely isolated to HOW tokens are read, not what they
//mean once read.
int main(void)
{
    int type, lastvar = -1;   //index (0-25) of the most recently
                               //referenced variable letter, for '=' to
                               //know its target; -1 means "none yet"
    double op2, result, lastprint = 0.0;
    char s[MAXOP];
    static double variables[26];  //static, not just local -- guarantees
                                   //automatic zero-init (a plain local
                                   //array would start with garbage);
                                   //only main() ever touches this, so
                                   //it doesn't need to be a true global

    while ((type = getop(s)) != EOF) {
        switch (type) {
        case NUMBER:
            push(atof(s));
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
        case '%':
            op2 = pop();
            if (op2 != 0.0)
                push(fmod(pop(), op2));
            else
                printf("error: zero divisor\n");
            break;
        case WORD:
            if (s[1] == '\0' && islower((unsigned char) s[0])) {
                lastvar = s[0] - 'a';       //remember for a following '='
                push(variables[lastvar]);   //read: push its current value
            }
            else if (strcmp(s, "sin") == 0)
                push(sin(pop()));
            else if (strcmp(s, "cos") == 0)
                push(cos(pop()));
            else if (strcmp(s, "tan") == 0)
                push(tan(pop()));
            else if (strcmp(s, "asin") == 0)
                push(asin(pop()));
            else if (strcmp(s, "acos") == 0)
                push(acos(pop()));
            else if (strcmp(s, "atan") == 0)
                push(atan(pop()));
            else if (strcmp(s, "exp") == 0)
                push(exp(pop()));
            else if (strcmp(s, "log") == 0)
                push(log(pop()));
            else if (strcmp(s, "log10") == 0)
                push(log10(pop()));
            else if (strcmp(s, "sqrt") == 0)
                push(sqrt(pop()));
            else if (strcmp(s, "cbrt") == 0)
                push(cbrt(pop()));
            else if (strcmp(s, "floor") == 0)
                push(floor(pop()));
            else if (strcmp(s, "ceil") == 0)
                push(ceil(pop()));
            else if (strcmp(s, "fabs") == 0)
                push(fabs(pop()));
            else if (strcmp(s, "pow") == 0) {
                op2 = pop();               //exponent, popped first --
                push(pow(pop(), op2));     //same convention as '-'/'/'
            } else if (strcmp(s, "print") == 0) {   //print top, don't remove
                if (sp > 0)
                    printf("\t%.8g\n", val[sp-1]);
                else
                    printf("error: stack empty\n");
            } else if (strcmp(s, "dup") == 0) {     //duplicate top
                if (sp > 0)
                    push(val[sp-1]);
                else
                    printf("error: stack empty\n");
            } else if (strcmp(s, "swap") == 0) {    //swap top two
                if (sp >= 2) {
                    double tmp = val[sp-1];
                    val[sp-1] = val[sp-2];
                    val[sp-2] = tmp;
                } else
                    printf("error: need two elements to swap\n");
            } else if (strcmp(s, "clear") == 0) {   //clear the stack
                sp = 0;
            } else
                printf("error: unknown word %s\n", s);
            break;
        case '=':                    //assign: "value letter ="
            if (lastvar < 0)
                printf("error: no variable named before '='\n");
            else {
                pop();                          //discard the value the
                                                 //letter itself just
                                                 //pushed when it was read
                variables[lastvar] = pop();     //the value to store
            }
            break;
        case '$':                    //push the most recently PRINTED value
            push(lastprint);
            break;
        case '\n':
            result = pop();
            lastprint = result;
            printf("\t%.8g\n", result);
            break;
        default:
            printf("error: unknown command %s\n", s);
            break;
        }
    }
    return 0;
}

#define MAXVAL  100   //maximum depth of val stack

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

//my_getline:  get line into s, return length -- unchanged from section
//4.1's example; renamed to avoid colliding with glibc's own getline()
int my_getline(char s[], int lim)
{
    int c, i;

    i = 0;
    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        s[i++] = c;
    if (c == '\n')
        s[i++] = c;
    s[i] = '\0';
    return i;
}

//getop:  get next character, numeric operand, or alphabetic word --
//reads from the in-memory line[] buffer via lineindex, refilling it a
//whole line at a time via my_getline whenever it runs out
int getop(char s[])
{
    int i;

    while (lineindex >= linelen) {   //current line exhausted
        linelen = my_getline(line, MAXLINE);
        lineindex = 0;
        if (linelen == 0)
            return EOF;               //true end of input
    }

    while (line[lineindex] == ' ' || line[lineindex] == '\t')
        lineindex++;

    //negative-number lookahead: peek at line[lineindex+1] directly --
    //no getch()/ungetch() needed, it's just array indexing, and it's
    //always safe because my_getline guarantees a '\0' right after the
    //last real character, so the peek never reads past valid memory
    if (line[lineindex] == '-' &&
        !(isdigit((unsigned char) line[lineindex+1]) || line[lineindex+1] == '.')) {
        s[0] = line[lineindex++];
        s[1] = '\0';
        return s[0];                   //just the '-' operator
    }

    if (isalpha((unsigned char) line[lineindex])) {
        i = 0;
        while (isalnum((unsigned char) line[lineindex]))
            s[i++] = line[lineindex++];
        s[i] = '\0';
        return WORD;
    }

    if (!isdigit((unsigned char) line[lineindex]) &&
        line[lineindex] != '.' && line[lineindex] != '-') {
        s[0] = line[lineindex++];
        s[1] = '\0';
        return s[0];                   //some other single-char operator
    }

    //a number, possibly negative, possibly with a fractional part
    i = 0;
    if (line[lineindex] == '-')
        s[i++] = line[lineindex++];
    while (isdigit((unsigned char) line[lineindex]))
        s[i++] = line[lineindex++];
    if (line[lineindex] == '.') {
        s[i++] = line[lineindex++];
        while (isdigit((unsigned char) line[lineindex]))
            s[i++] = line[lineindex++];
    }
    s[i] = '\0';
    return NUMBER;
}

*/

/*

#include <stdio.h>

#define BUFSIZE 100

int buf[BUFSIZE];   //FIXED type: int, not char (see below) -- must be
                     //able to hold every value getchar() can return,
                     //EOF included, without truncation
int bufp = 0;

int getch(void);
void ungetch(int);

//K&R2 exercise 4-9: getch/ungetch don't handle a pushed-back EOF
//correctly. Two separate decisions, going back to the multi-slot design
//from exercise 4-7 (this doesn't apply to 4-8's one-int version at all
//-- that design already uses EOF itself as the "buffer is empty"
//sentinel, so it can NEVER tell a genuinely pushed-back EOF apart from
//an empty slot; that incompatibility is inherent to 4-8's design, not
//fixable without changing it back to something like this):
//
//(1) THE ACTUAL BUG: the old buffer was "char buf[BUFSIZE]". EOF is
//typically -1, and getchar()/getch() return it as an int specifically
//so it's distinguishable from every real character (0-255). Storing it
//into a plain char loses that guarantee: whether "char" is signed or
//unsigned is implementation-defined by the C standard -- on THIS
//machine (x86-64, gcc), plain char defaults to signed, so -1 happens
//to survive intact and the bug doesn't actually surface here. But on a
//platform where char is unsigned (common on ARM), storing -1 into it
//silently wraps to 255 -- and reading 255 back out as an int is NOT
//EOF, so "while ((c = getch()) != EOF)" would never see EOF arrive
//through the pushback path and could loop forever on it. Demonstrated
//concretely below with an explicit unsigned char, so the failure isn't
//just asserted -- it's forced to happen, on this same machine, on
//purpose.
//
//(2) THE DESIGN DECISION: should ungetch(EOF) even queue anything?
//Chosen answer: no -- make it a silent no-op. EOF isn't a real
//character being deferred for later, it's a signal that input ran out;
//there's nothing to "give back." If input is genuinely exhausted, the
//next getch() will fall through to getchar() and correctly hit EOF on
//its own anyway -- so refusing to buffer it costs nothing and avoids
//wasting a slot (or, worse, ambiguity) on a value that was never a
//real character to begin with.
int main(void)
{
    unsigned char broken_buf[1];   //deliberately the WRONG type, just
                                    //to force and show the failure mode
    int stored, read_back;

    printf("part 1 -- concrete proof of the char-truncation bug:\n");
    broken_buf[0] = (unsigned char) EOF;
    stored = EOF;
    read_back = broken_buf[0];
    printf("  EOF is %d; stored into unsigned char, read back as %d\n",
           stored, read_back);
    printf("  %s\n\n", (read_back == EOF)
           ? "(would still equal EOF -- no corruption)"
           : "(does NOT equal EOF anymore -- exactly the bug 4-9 warns about)");

    printf("part 2 -- fixed getch/ungetch, explicit ungetch(EOF):\n");
    printf("  ungetch(EOF) should be a silent no-op, not queue anything:\n");
    ungetch(EOF);
    ungetch('z');
    read_back = getch();
    printf("  getch() returns: '%c' (expected 'z' -- proves EOF from the\n"
           "  first ungetch call was correctly discarded, not queued\n"
           "  ahead of 'z')\n", read_back);

    return 0;
}

//getch:  get a (possibly pushed back) character
int getch(void)
{
    return (bufp > 0) ? buf[--bufp] : getchar();
}

//ungetch:  push character back on input -- EOF is refused outright,
//see the design note above
void ungetch(int c)
{
    if (c == EOF)
        return;      //nothing to queue -- see the design note above
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters pushed back\n");
    else
        buf[bufp++] = c;
}

*/

/*

#include <stdio.h>

int buf = EOF;   //ONE character of pushback -- EOF doubles as "empty",
                  //since EOF is never a real character you'd legitimately
                  //push back (getop already guards against ever calling
                  //ungetch(EOF) itself, so this sentinel is always safe)

int getch(void);
void ungetch(int);

//K&R2 exercise 4-8: assume AT MOST ONE character of pushback is ever
//needed, and simplify getch/ungetch accordingly -- the whole array +
//index (buf[BUFSIZE]/bufp) collapses into a single int.
//
//This is a genuinely different assumption than exercise 4-7's ungets(),
//which needs to push back an ENTIRE STRING at once -- that only worked
//because the old buf[]/bufp was a real multi-slot stack. With this
//one-slot version, ungets() would break the instant a string longer
//than one character came through: the second ungetch() call in its
//loop would immediately overwrite (or, as written below, get rejected
//outright by) the first. K&R poses 4-7 and 4-8 as separate exercises on
//purpose -- they explore two different, mutually exclusive designs for
//the same interface, not two features meant to be combined.
int main(void)
{
    printf("test 1: push back 'x', then read it -- should print x:\n  ");
    ungetch('x');
    putchar(getch());
    printf("\n\n");

    printf("test 2: push back 'a', then try to push back 'b' too, BEFORE\n"
           "reading 'a' -- only one slot exists now, so the second\n"
           "ungetch should be rejected, and getch() should still return\n"
           "the original 'a', not 'b':\n  ");
    ungetch('a');
    ungetch('b');   //should print the overflow message, and NOT
                     //overwrite the pending 'a'
    putchar(getch());
    printf("\n");

    return 0;
}

//getch:  get a (possibly pushed back) character -- now just checking
//one int instead of indexing into an array
int getch(void)
{
    int c;

    if (buf != EOF) {
        c = buf;
        buf = EOF;   //slot is empty again
        return c;
    }
    return getchar();
}

//ungetch:  push character back on input -- the slot is either empty
//(buf == EOF) or full; there's no "how many are in there" to track
void ungetch(int c)
{
    if (buf != EOF)
        printf("ungetch: too many characters pushed back\n");
    else
        buf = c;
}

*/

/*

#include <stdio.h>
#include <string.h>

#define BUFSIZE 100

char buf[BUFSIZE];   //buffer for ungetch/ungets
int bufp = 0;         //next free position in buf

int getch(void);
void ungetch(int);
void ungets(char []);

//K&R2 exercise 4-7: ungets(s) -- push an entire string back onto the
//input, so the next getch() calls read it back out again, whole and in
//the right order.
//
//The exercise's actual question -- "should ungets know about buf and
//bufp, or should it just use ungetch?" -- is the real point, more than
//the function itself. Answer: it should ONLY use ungetch(), the same
//way main() only ever uses push()/pop() for the arithmetic operators,
//rather than poking
//at val[]/sp directly (see exercise 4-4's p/d/s/c for the one case
//where that abstraction genuinely didn't fit and got bypassed on
//purpose). Here there's no such justification -- ungetch() already
//does exactly what's needed ("push back one character," with its own
//BUFSIZE overflow check already built in), so ungets just needs to
//call it once per character. Reaching past it to touch buf[]/bufp
//directly would duplicate that overflow logic for no benefit, and
//worse, couple ungets to buf's internal representation -- if the
//pushback buffer's implementation ever changed, ungets built on
//ungetch wouldn't need to change AT ALL, since it never knew how
//ungetch works internally, only that it works.
//
//The one genuine subtlety: PUSHBACK ORDER. buf[]/bufp is a stack --
//last pushed is first popped. To make getch() read a string back in
//its ORIGINAL order, the characters must be pushed in REVERSE: push
//the LAST character of s first (burying it deepest), and the FIRST
//character of s last (putting it on top, so it's the very next thing
//getch() returns). Pushing forward instead would read the string back
//backwards.
void ungets(char s[])
{
    int n = (int) strlen(s);

    while (n > 0)
        ungetch(s[--n]);
}

//getch:  get a (possibly pushed back) character
int getch(void)
{
    return (bufp > 0) ? buf[--bufp] : getchar();
}

//ungetch:  push character back on input
void ungetch(int c)
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters pushed back\n");
    else
        buf[bufp++] = c;
}

int main(void)
{
    int i;

    printf("test 1: ungets(\"hello\"), then read exactly 5 chars back:\n  ");
    ungets("hello");
    for (i = 0; i < 5; i++)
        putchar(getch());
    printf("\n\n");

    printf("test 2: two ungets() calls, LIFO at the STRING level --\n"
           "ungets(\"world\") first, then ungets(\"hello \") second,\n"
           "so \"hello \" (pushed most recently) reads back FIRST:\n  ");
    ungets("world");
    ungets("hello ");
    for (i = 0; i < 11; i++)   //"hello world" is 11 characters
        putchar(getch());
    printf("\n");

    return 0;
}

*/

/*

#include <stdio.h>
#include <stdlib.h>   //for atof()
#include <string.h>   //for strcmp() -- see the WORD dispatch below
#include <ctype.h>
#include <math.h>     //for fmod() and the whole WORD dispatch's functions
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c -lm

#define MAXOP   100   //max size of operand or operator
#define NUMBER  '0'   //signal that a number was found
#define WORD    'W'   //signal that an alphabetic word was found -- a
                       //function name ("sin"), a command ("swap"), or
                       //(new in exercise 4-6) a single-letter variable

int getop(char []);
void push(double);
double pop(void);
extern int sp;          //declared here so main() can read the stack
extern double val[];    //directly for the dispatch below; still DEFINED
                         //once, further down, exactly where push/pop
                         //already lived -- main() just gets visibility
                         //into state it needs to peek at without popping

//K&R2 exercise 4-6: twenty-six single-letter variables (a-z), plus a
//special variable, '$', holding the most recently PRINTED value (not
//just the most recently computed one -- specifically what a '\n' last
//showed you).
//
//Reading a variable is simple: a bare letter is a WORD token like any
//other (single-character words already worked fine before this --
//that's exactly how "p"/"d"/"s"/"c" behaved in exercise 4-4), and now
//pushes that variable's current value, same as typing a number would.
//
//Assignment is the genuinely new piece: "value letter =" -- e.g.
//"3.14 x =". The tricky part is that reading "x" ALSO pushes its old
//value (per the paragraph above), so by the time '=' runs, the stack
//holds [new_value, old_value_of_x], not just the new value. '=' handles
//this by popping TWICE: the first pop discards that redundant old
//value, the second pop is the actual value to store. It knows WHICH
//variable to store into via lastvar, a piece of state updated every
//time any single-letter word is read -- "the most recent variable
//letter seen," so '=' always knows its target without needing the
//letter and the '=' to be read as one combined token.
//
//One real behavior change from exercise 4-4: the single-letter commands
//'p'/'d'/'s'/'c' are renamed to full words -- "print"/"dup"/"swap"/
//"clear" -- freeing every one of the 26 letters to be a variable
//instead, matching the exercise's literal ask ("twenty-six variables
//with single-letter names") rather than only 22 of them.

//K&R2 exercise 4-5: access to <math.h> library functions. All are
//one-operand (pop one, push the result) except pow, which is two
//(base, then exponent -- same "op2 popped first" convention '-' and
//'/' already use):
//  sin cos tan          -- radians in, same as <math.h>
//  asin acos atan        -- inverse trig, radians out
//  exp log log10 sqrt cbrt
//  floor ceil fabs
//  pow                    -- the one binary function
//
//The real work isn't calling these functions (that part's one line
//each) -- it's that getop() previously had no idea what to do with a
//LETTER. Every token so far was either a digit/'.'/'-' (a number) or a
//single punctuation character (an operator). "sin" is neither: it's
//THREE letters that together mean one thing, the same shape problem as
//reading a multi-digit number, just with isalpha() instead of isdigit().
//
//That collides directly with exercise 4-4's single-letter commands,
//though: 'p'/'d'/'s'/'c' were previously matched as raw single
//characters. If getop() now reads *any* run of letters as one word,
//typing just "s" and typing "sin" both start the same way -- so they
//can't be told apart by token TYPE anymore, only by the word's actual
//text. The fix: getop() returns ONE new signal, WORD, for any
//alphabetic run of any length (one letter or many), and main() decides
//what it means with strcmp() against a list of known names -- "sin",
//"cos", "pow", ..., and now "p"/"d"/"s"/"c" too, unified into the same
//mechanism instead of being a special case.

int main(void)
{
    int type, lastvar = -1;   //index (0-25) of the most recently
                               //referenced variable letter, for '=' to
                               //know its target; -1 means "none yet"
    double op2, result, lastprint = 0.0;
    char s[MAXOP];
    static double variables[26];  //static, not just local -- guarantees
                                   //automatic zero-init (a plain local
                                   //array would start with garbage);
                                   //only main() ever touches this, so
                                   //it doesn't need to be a true global

    while ((type = getop(s)) != EOF) {
        switch (type) {
        case NUMBER:
            push(atof(s));
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
        case '%':
            op2 = pop();
            if (op2 != 0.0)
                push(fmod(pop(), op2));
            else
                printf("error: zero divisor\n");
            break;
        case WORD:
            if (s[1] == '\0' && islower((unsigned char) s[0])) {
                lastvar = s[0] - 'a';       //remember for a following '='
                push(variables[lastvar]);   //read: push its current value
            }
            else if (strcmp(s, "sin") == 0)
                push(sin(pop()));
            else if (strcmp(s, "cos") == 0)
                push(cos(pop()));
            else if (strcmp(s, "tan") == 0)
                push(tan(pop()));
            else if (strcmp(s, "asin") == 0)
                push(asin(pop()));
            else if (strcmp(s, "acos") == 0)
                push(acos(pop()));
            else if (strcmp(s, "atan") == 0)
                push(atan(pop()));
            else if (strcmp(s, "exp") == 0)
                push(exp(pop()));
            else if (strcmp(s, "log") == 0)
                push(log(pop()));
            else if (strcmp(s, "log10") == 0)
                push(log10(pop()));
            else if (strcmp(s, "sqrt") == 0)
                push(sqrt(pop()));
            else if (strcmp(s, "cbrt") == 0)
                push(cbrt(pop()));
            else if (strcmp(s, "floor") == 0)
                push(floor(pop()));
            else if (strcmp(s, "ceil") == 0)
                push(ceil(pop()));
            else if (strcmp(s, "fabs") == 0)
                push(fabs(pop()));
            else if (strcmp(s, "pow") == 0) {
                op2 = pop();               //exponent, popped first --
                push(pow(pop(), op2));     //same convention as '-'/'/'
            } else if (strcmp(s, "print") == 0) {   //print top, don't remove
                if (sp > 0)
                    printf("\t%.8g\n", val[sp-1]);
                else
                    printf("error: stack empty\n");
            } else if (strcmp(s, "dup") == 0) {     //duplicate top
                if (sp > 0)
                    push(val[sp-1]);
                else
                    printf("error: stack empty\n");
            } else if (strcmp(s, "swap") == 0) {    //swap top two
                if (sp >= 2) {
                    double tmp = val[sp-1];
                    val[sp-1] = val[sp-2];
                    val[sp-2] = tmp;
                } else
                    printf("error: need two elements to swap\n");
            } else if (strcmp(s, "clear") == 0) {   //clear the stack
                sp = 0;
            } else
                printf("error: unknown word %s\n", s);
            break;
        case '=':                    //assign: "value letter ="
            if (lastvar < 0)
                printf("error: no variable named before '='\n");
            else {
                pop();                          //discard the value the
                                                 //letter itself just
                                                 //pushed when it was read
                variables[lastvar] = pop();     //the value to store
            }
            break;
        case '$':                    //push the most recently PRINTED value
            push(lastprint);
            break;
        case '\n':
            result = pop();
            lastprint = result;
            printf("\t%.8g\n", result);
            break;
        default:
            printf("error: unknown command %s\n", s);
            break;
        }
    }
    return 0;
}

#define MAXVAL  100   //maximum depth of val stack

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

int getch(void);
void ungetch(int);

//getop:  get next character, numeric operand, or alphabetic word (now
//recognizing an alphabetic run as a WORD token, alongside the existing
//'-' negative-number lookahead)
int getop(char s[])
{
    int i, c;

    while ((s[0] = c = getch()) == ' ' || c == '\t')
        ;
    s[1] = '\0';
    i = 0;

    if (c == '-') {
        c = getch();
        if (!isdigit(c) && c != '.') {
            if (c != EOF)
                ungetch(c);      //wasn't a number after all -- give it back
            return s[0];         //just the '-' operator
        }
        s[++i] = c;              //fold the first digit/'.' in after the sign
    } else if (isalpha(c)) {     //a function name or single-letter command
                                  //-- must START with a letter (that's
                                  //what tells it apart from a number),
                                  //but can CONTINUE with digits too
                                  //(e.g. "log10"), same as a normal
                                  //identifier -- isalnum, not isalpha,
                                  //for every character after the first
        while (isalnum(s[++i] = c = getch()))
            ;
        s[i] = '\0';
        if (c != EOF)
            ungetch(c);
        return WORD;
    } else if (!isdigit(c) && c != '.') {
        return c;    //not a number, not a word
    }

    if (isdigit(c))  //collect integer part
        while (isdigit(s[++i] = c = getch()))
            ;
    if (c == '.')    //collect fraction part
        while (isdigit(s[++i] = c = getch()))
            ;
    s[i] = '\0';
    if (c != EOF)
        ungetch(c);
    return NUMBER;
}

#define BUFSIZE 100

char buf[BUFSIZE];   //buffer for ungetch
int bufp = 0;         //next free position in buf

//getch:  get a (possibly pushed back) character
int getch(void)
{
    return (bufp > 0) ? buf[--bufp] : getchar();
}

//ungetch:  push character back on input
void ungetch(int c)
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters pushed back\n");
    else
        buf[bufp++] = c;
}

*/

/*

//K&R2 exercise 4-4: four new single-letter commands added to the
//switch below, all operating on the SAME val[]/sp stack push/pop
//already use -- nothing about the stack itself changes, only what's
//allowed to touch it:
//  p  print the top value without removing it (pop() always removes;
//     sometimes you just want to look)
//  d  duplicate the top value (push a second copy of whatever's on top)
//  s  swap the top two values -- useful before a non-commutative op
//     like '-' or '/', where operand order matters
//  c  clear the whole stack back to empty (sp = 0)
//
//These read/write val[]/sp DIRECTLY inside main(), unlike the plain
//arithmetic operators, which only ever go through push()/pop(). That's a deliberate exception, not
//sloppiness: push/pop's whole job is enforcing "you may only add/remove
//from the TOP," but 'p' specifically needs to look at the top WITHOUT
//removing it, and 's' needs to touch two slots in the middle of a swap
//at once -- neither fits cleanly into push/pop's one-value-at-a-time
//contract, so this reaches past it to the array directly instead of
//forcing an awkward workaround through it.

//K&R2 exercise 4-3: two additions to the calculator archived below.
//
//(1) modulus, '%' -- the value stack holds DOUBLEs, but C's own %
//operator only works on integers. fmod(a, b) is the floating-point
//equivalent: a - b * trunc(a/b), i.e. "the remainder after dividing
//toward zero" -- so fmod(-5, 3) is -2, not 1 (matches the sign of the
//first operand, same convention as C's own integer %). Implemented via
//<math.h> rather than by hand, unlike the earlier scientific-notation
//atof exercise's deliberate avoidance of pow() -- there the goal was
//staying self-contained with the same building blocks K&R had already
//used; here, reimplementing fmod by hand would just be re-deriving the
//standard library function with no real lesson left in it.
//
//(2) negative number literals -- until now, getop() treated EVERY '-'
//as the subtraction operator, because it only checked isdigit()/'.' to
//decide "is this a number." Typing "-5" actually tokenized as two
//separate things: operator '-', then NUMBER "5" -- there was no way to
//push a literal negative value directly (only reach one via
//subtraction, e.g. "0 5 -"). The fix: when getop sees a '-', peek ONE
//character further. If that next character is a digit or '.', the '-'
//is the start of a negative number, so it gets folded into s[] and
//reading continues normally. If not, ungetch() hands the peeked
//character back and '-' is reported as the operator, exactly as before.

//K&R2 sections 4.3-4.4: the full reverse Polish notation calculator --
//four pieces working together, all needed for this to link/run, not
//just the switch statement on its own:
//  main()  -- reads tokens, dispatches on operator vs. NUMBER
//  push/pop -- the value stack itself (a plain array + top-of-stack index)
//  getop   -- reads one token: a full number into s[], or a single
//             operator character, skipping blanks/tabs along the way
//  getch/ungetch -- a one-character pushback buffer, which is what lets
//             getop peek one character past the end of a number (to see
//             it's NOT a digit anymore) and then hand that character
//             back to be read again as the next token, instead of losing it
int main(void)
{
    int type;
    double op2;
    char s[MAXOP];

    while ((type = getop(s)) != EOF) {
        switch (type) {
        case NUMBER:
            push(atof(s));
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
        case '%':
            op2 = pop();
            if (op2 != 0.0)
                push(fmod(pop(), op2));
            else
                printf("error: zero divisor\n");
            break;
        case 'p':                  //print top of stack, don't remove it
            if (sp > 0)
                printf("\t%.8g\n", val[sp-1]);
            else
                printf("error: stack empty\n");
            break;
        case 'd':                  //duplicate top of stack
            if (sp > 0)
                push(val[sp-1]);
            else
                printf("error: stack empty\n");
            break;
        case 's':                  //swap top two elements
            if (sp >= 2) {
                double tmp = val[sp-1];
                val[sp-1] = val[sp-2];
                val[sp-2] = tmp;
            } else
                printf("error: need two elements to swap\n");
            break;
        case 'c':                  //clear the stack
            sp = 0;
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

#define MAXVAL  100   //maximum depth of val stack

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

int getch(void);
void ungetch(int);

//getop:  get next character or numeric operand (now recognizing a
//leading '-' as a negative sign when a digit/'.' immediately follows,
//instead of always treating '-' as the subtraction operator)
int getop(char s[])
{
    int i, c;

    while ((s[0] = c = getch()) == ' ' || c == '\t')
        ;
    s[1] = '\0';
    i = 0;

    if (c == '-') {
        c = getch();
        if (!isdigit(c) && c != '.') {
            if (c != EOF)
                ungetch(c);      //wasn't a number after all -- give it back
            return s[0];         //just the '-' operator
        }
        s[++i] = c;              //fold the first digit/'.' in after the sign
    } else if (!isdigit(c) && c != '.') {
        return c;    //not a number
    }

    if (isdigit(c))  //collect integer part
        while (isdigit(s[++i] = c = getch()))
            ;
    if (c == '.')    //collect fraction part
        while (isdigit(s[++i] = c = getch()))
            ;
    s[i] = '\0';
    if (c != EOF)
        ungetch(c);
    return NUMBER;
}

#define BUFSIZE 100

char buf[BUFSIZE];   //buffer for ungetch
int bufp = 0;         //next free position in buf

//getch:  get a (possibly pushed back) character
int getch(void)
{
    return (bufp > 0) ? buf[--bufp] : getchar();
}

//ungetch:  push character back on input
void ungetch(int c)
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters pushed back\n");
    else
        buf[bufp++] = c;
}

*/

/*

#include <stdio.h>
#include <ctype.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 4-2: extend atof to handle scientific notation --
//123.45e-6, an optional 'e'/'E' followed by an optionally-signed
//integer exponent. The mantissa parsing (sign, integer part, '.',
//fractional part) is completely unchanged from section 4.2's version;
//it's finished into "val" exactly as before FIRST, and only THEN does
//the function look for an 'e'/'E' to adjust it.
//
//The exponent itself is parsed the same shape as the sign/digit-loop
//pattern already used twice above (mantissa sign, now exponent sign),
//then applied by repeated multiplication/division rather than a pow()
//call -- multiply by 10 once per positive exponent, divide by 10 once
//per negative exponent. That's a deliberate choice, not an oversight:
//pow() lives in <math.h> and needs -lm at link time, while this stays
//self-contained with nothing beyond what K&R's own version already used.
double atof(char s[])
{
    double val, power;
    int i, sign, exp, esign;

    for (i = 0; isspace(s[i]); i++)   //skip white space
        ;
    sign = (s[i] == '-') ? -1 : 1;
    if (s[i] == '+' || s[i] == '-')
        i++;
    for (val = 0.0; isdigit(s[i]); i++)
        val = 10.0 * val + (s[i] - '0');
    if (s[i] == '.')
        i++;
    for (power = 1.0; isdigit(s[i]); i++) {
        val = 10.0 * val + (s[i] - '0');
        power *= 10;
    }
    val = sign * val / power;

    if (s[i] == 'e' || s[i] == 'E') {
        i++;
        esign = (s[i] == '-') ? -1 : 1;
        if (s[i] == '+' || s[i] == '-')
            i++;
        for (exp = 0; isdigit(s[i]); i++)
            exp = 10 * exp + (s[i] - '0');
        exp *= esign;
        while (exp > 0) {
            val *= 10.0;
            exp--;
        }
        while (exp < 0) {
            val /= 10.0;
            exp++;
        }
    }

    return val;
}

int main(void)
{
    char *tests[] = {
        "123.45e-6",
        "1e10",
        "1.5E3",
        "2.5e+2",
        "-3.2e-2",
        "6.022e23",     //no exponent overflow at double precision
        "5",            //no exponent at all -- must still work
        "5.5",
        "1e0",
        "-1.5e-0",
    };
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;

    for (i = 0; i < ntests; i++)
        printf("atof(\"%s\") = %g\n", tests[i], atof(tests[i]));

    return 0;
}

*/

/*

#include <stdio.h>
#include <ctype.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

#define MAXLINE 100

double atof(char s[]);
int my_getline(char line[], int max);   //renamed for the same reason as
                                         //section 4.1's example, below

//K&R2 section 4.2's rudimentary calculator: read one number per line,
//print the running sum after each. Reuses this same atof (just above,
//archived below alongside this program once you move to the next
//exercise) and my_getline from section 4.1's example (also archived
//further down) -- both were already written and verified working, so
//this program is really just gluing two already-proven pieces together
//with a running total, nothing new to debug in atof or my_getline
//themselves.
int main(void)
{
    double sum;
    char line[MAXLINE];

    sum = 0;
    while (my_getline(line, MAXLINE) > 0)
        printf("\t%g\n", sum += atof(line));
    return 0;
}

//K&R2 section 4.2: atof(s) -- convert string s to double, in one pass:
//optional leading whitespace, an optional sign, an integer part, an
//optional '.', then a fractional part. "power" only grows during the
//fractional-digit loop (multiplying by 10 each digit), so a string with
//no '.' or no digits after it leaves power at its initial 1.0 -- a
//no-op divisor, which is exactly why the final "val / power" correctly
//handles both integer-only and decimal input with the same formula.
//
//Same landmine as the plain atoi archived further below: a space
//between the sign and the digits ("-  7.5") isn't handled -- once the
//sign is consumed, the very next isdigit() check fails on the space,
//so both digit-collecting loops never run at all, silently returning
//0.0 instead of -7.5. Demonstrated below rather than avoided.
double atof(char s[])
{
    double val, power;
    int i, sign;

    for (i = 0; isspace(s[i]); i++)   //skip white space
        ;
    sign = (s[i] == '-') ? -1 : 1;
    if (s[i] == '+' || s[i] == '-')
        i++;
    for (val = 0.0; isdigit(s[i]); i++)
        val = 10.0 * val + (s[i] - '0');
    if (s[i] == '.')
        i++;
    for (power = 1.0; isdigit(s[i]); i++) {
        val = 10.0 * val + (s[i] - '0');
        power *= 10;
    }
    return sign * val / power;
}

//my_getline:  get line into s, return length -- renamed for the same
//reason as section 4.1's example: glibc's own <stdio.h> already declares
//a getline() with a totally different signature, so plain "getline"
//would collide with it under this file's GNU-dialect compile.
int my_getline(char s[], int lim)
{
    int c, i;

    i = 0;
    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        s[i++] = c;
    if (c == '\n')
        s[i++] = c;
    s[i] = '\0';
    return i;
}

*/

/*

#include <stdio.h>
#include <ctype.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

int main(void)
{
    char *tests[] = {
        "3.14159",
        "-2.5",
        "+42",
        "  123.456",
        "0.001",
        "-0.5",
        "100",
        "  -  7.5",     //space between sign and digits -- watch this one
        "abc",
        "",
    };
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;

    for (i = 0; i < ntests; i++)
        printf("atof(\"%s\") = %g\n", tests[i], atof(tests[i]));

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 4-1: strrindex(s, t) -- like section 4.1's strindex, but
//returns the RIGHTMOST occurrence of t in s instead of the leftmost (the
//book itself names this function strrindex, not strindex -- reusing
//strindex's name would just shadow the leftmost-match version archived
//below, since only one is ever active in this file at a time, but the
//book's own naming is worth keeping so both could coexist if you ever
//wanted them side by side).
//
//Same substring-match core as strindex, just scanning ALL of s instead
//of returning at the first hit: every time a match is found at position
//i, save i into "last" and keep going. Whatever "last" holds once the
//outer loop finishes is necessarily the rightmost one, because nothing
//later in the string can un-happen -- the final assignment to "last"
//naturally IS the last (highest-index) match seen.
int strrindex(char s[], char t[])
{
    int i, j, k, last;

    last = -1;
    for (i = 0; s[i] != '\0'; i++) {
        for (j = i, k = 0; t[k] != '\0' && s[j] == t[k]; j++, k++)
            ;
        if (k > 0 && t[k] == '\0')
            last = i;
    }
    return last;
}

int main(void)
{
    struct { char *s, *t; } tests[] = {
        {"abcabcabc", "abc"},
        {"ababab",    "ab"},
        {"hello world", "o"},
        {"mississippi", "iss"},
        {"no match here", "xyz"},
        {"abc", "abc"},
        {"short", "muchlongerthanshort"},
    };
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;

    for (i = 0; i < ntests; i++)
        printf("strrindex(\"%s\", \"%s\") = %d\n",
               tests[i].s, tests[i].t, strrindex(tests[i].s, tests[i].t));

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

#define MAXLINE 1000   //maximum input line length

int my_getline(char line[], int maxline);
int strindex(char source[], char searchfor[]);

char pattern[] = "ould";   //pattern to search for

//K&R2 section 4.1's opening example program: read every line of input,
//print the ones containing "ould". Renamed getline -> my_getline for one
//specific reason, confirmed by actually trying the original name first:
//glibc's own <stdio.h> already declares a function called getline (the
//POSIX/GNU extension ssize_t getline(char **lineptr, size_t *n, FILE
//pointer), used for dynamically-growing line reads) -- a completely
//different signature from K&R's. Since this file compiles with plain
//gcc (GNU dialect, not strict ISO C), that declaration is visible by
//default, so redeclaring "int getline(char[], int)" collides with it
//("conflicting types for 'getline'"). Exact same reason my_strcat was
//named that way earlier in this file, to dodge <string.h>'s own strcat.

//find all lines matching pattern
int main(void)
{
    char line[MAXLINE];
    int found = 0;

    while (my_getline(line, MAXLINE) > 0)
        if (strindex(line, pattern) >= 0) {
            printf("%s", line);
            found++;
        }
    return found;
}

//my_getline:  get line into s, return length
int my_getline(char s[], int lim)
{
    int c, i;

    i = 0;
    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        s[i++] = c;
    if (c == '\n')
        s[i++] = c;
    s[i] = '\0';
    return i;
}

//strindex:  return index of t in s, -1 if none
int strindex(char s[], char t[])
{
    int i, j, k;

    for (i = 0; s[i] != '\0'; i++) {
        for (j = i, k = 0; t[k] != '\0' && s[j] == t[k]; j++, k++)
            ;
        if (k > 0 && t[k] == '\0')
            return i;
    }
    return -1;
}

*/

/*

#include <stdio.h>
#include <string.h>
#include <limits.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

// reverse:  reverse string s in place
void reverse(char s[])
{
    int c, i, j;

    for (i = 0, j = strlen(s)-1; i < j; i++, j--) {
        c = s[i];
        s[i] = s[j];
        s[j] = c;
    }
}

//trim: remove trailing blanks, tabs, newlines from s, and return the
//index of the new last character (or -1 if the whole string was blank).
//
//One thing worth watching: for an EMPTY input string, strlen(s)-1 is
//computed in size_t (unsigned) arithmetic, so 0 - 1 wraps around to
//SIZE_MAX, not -1 -- and only THEN does that huge unsigned value get
//assigned into the (signed) int n. Converting an out-of-range unsigned
//value to a signed type is implementation-defined in C, not guaranteed
//-1 by the standard -- but on every real two's-complement machine (this
//one included) the bit pattern for SIZE_MAX reinterprets as exactly -1,
//so the for loop's "n >= 0" is false immediately and trim behaves
//correctly by accident of representation, not by the code's own logic
//explicitly guarding for it. Tested below rather than just asserted.
int trim(char s[])
{
    int n;

    for (n = strlen(s)-1; n >= 0; n--)
        if (s[n] != ' ' && s[n] != '\t' && s[n] != '\n')
            break;
    s[n+1] = '\0';
    return n;
}

int main(void)
{
    char tests[][40] = {
        "hello   ",
        "hello\t\t",
        "hello\n",
        "no trailing space",
        "   ",
        "",
        "a \t b \n",
    };
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i, result;

    for (i = 0; i < ntests; i++) {
        result = trim(tests[i]);
        printf("trim() -> index %2d, result: \"%s\"\n", result, tests[i]);
    }

    return 0;
}

*/

/*

//K&R2 exercise 3-6: itoa(n, s, w) -- same INT_MIN-safe digit extraction
//as exercise 3-4, but now with a third argument: minimum field width w.
//The number is built into s exactly as before, then reverse()d -- at that
//point i (renamed len here) IS the digit-plus-sign count, since it's the
//same index that s[i]='\0' just used. If w is wider than that, the digits
//need to move w-len slots to the right to make room, so the shift runs
//RIGHT TO LEFT (from the '\0' backward down to index 0) -- shifting
//left-to-right would overwrite characters before they'd been copied.
//Once the digits are out of the way, the freed low slots become blanks.
//If w <= len, the number is already at least as wide as asked -- K&R's
//own wording only requires padding "if necessary", so nothing is
//truncated or changed.
void itoa(int n, char s[], int w)
{
    int i, sign, len, pad;

    sign = n;
    if (n > 0)
        n = -n;
    i = 0;
    do {
        s[i++] = '0' - n % 10;
    } while ((n /= 10) != 0);
    if (sign < 0)
        s[i++] = '-';
    s[i] = '\0';
    len = i;
    reverse(s);

    pad = w - len;
    if (pad > 0) {
        for (i = len; i >= 0; i--)   //shift digits AND the '\0', right to left
            s[i + pad] = s[i];
        for (i = 0; i < pad; i++)    //fill the space just freed up with blanks
            s[i] = ' ';
    }
}

int main(void)
{
    struct { int n, w; } tests[] = {
        {123,        8},
        {-123,       8},
        {0,          5},
        {123456,     3},    //width narrower than the number -- no padding
        {2147483647, 15},
        {INT_MIN,    15},
        {7,          1},    //width == length already
    };
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;
    char s[40];

    for (i = 0; i < ntests; i++) {
        itoa(tests[i].n, s, tests[i].w);
        printf("itoa(%12d, w=%2d) = [%s]\n", tests[i].n, tests[i].w, s);
    }

    return 0;
}

*/

/*

#include <stdio.h>
#include <string.h>
#include <limits.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//reverse:  reverse string s in place
void reverse(char s[])
{
    int c, i, j;

    for (i = 0, j = strlen(s)-1; i < j; i++, j--) {
        c = s[i];
        s[i] = s[j];
        s[j] = c;
    }
}

//K&R2 exercise 3-5: itob(n, s, b) -- convert n to its base-b character
//representation in s, for any base b in [2, 16]. Same INT_MIN-safe idea
//as the fixed itoa (exercise 3-4, archived below): never negate n toward
//positive. If n started positive, flip it toward NEGATIVE instead, then
//peel digits off while n stays <= 0 for the whole loop. n % b on a
//non-positive n is itself in (-b, 0], so -(n % b) is always a valid
//index into digits[] no matter how negative n is -- INT_MIN included,
//and regardless of b.
void itob(int n, char s[], int b)
{
    static char digits[] = "0123456789abcdef";
    int i, sign, digit;

    sign = n;
    if (n > 0)
        n = -n;
    i = 0;
    do {
        digit = -(n % b);    //n <= 0, so n%b is in (-b, 0]
        s[i++] = digits[digit];
    } while ((n /= b) != 0);
    if (sign < 0)
        s[i++] = '-';
    s[i] = '\0';
    reverse(s);
}

int main(void)
{
    struct { int n, b; } tests[] = {
        {0,          10},
        {255,        16},
        {-255,       16},
        {10,          2},
        {-10,         2},
        {64,          8},
        {-64,         8},
        {2147483647, 16},
        {INT_MIN,    16},
        {INT_MIN,     2},
    };
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;
    char s[40];

    for (i = 0; i < ntests; i++) {
        itob(tests[i].n, s, tests[i].b);
        printf("itob(%12d, base %2d) = \"%s\"\n", tests[i].n, tests[i].b, s);
    }

    return 0;
}

*/

/*

#include <stdio.h>
#include <string.h>
#include <limits.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//reverse:  reverse string s in place
void reverse(char s[])
{
    int c, i, j;

    for (i = 0, j = strlen(s)-1; i < j; i++, j--) {
        c = s[i];
        s[i] = s[j];
        s[j] = c;
    }
}

//K&R2 exercise 3-4: fixed itoa -- the book's version breaks on
//n == INT_MIN (== -(2^(wordsize-1))) because two's complement is
//asymmetric: it has one MORE negative value than positive values, since
//0 itself eats one of the nonnegative slots. Concretely for a 32-bit int,
//the range is -2147483648..2147483647 -- there are 2147483648 negative
//values but only 2147483647 positive ones. That means INT_MIN's magnitude
//(2147483648) has no representation as a positive int at all, so
//"n = -n" silently overflows -- undefined behavior, which is exactly why
//the un-fixed version above printed garbage ("-(") for it instead of
//erroring loudly.
//
//The fix: never negate n at all. If n started positive, flip it to
//NEGATIVE instead ("n = -n" when n > 0 is always safe -- a positive
//int's magnitude always fits in the negative range, since that range is
//the bigger one). Then peel digits off while n stays <= 0 the whole
//time: n % 10 on a non-positive n is itself <= 0 (C99+ truncates toward
//zero), so '0' - n % 10 recovers the correct digit character. This way
//INT_MIN is handled the exact same way as every other negative number --
//no special case, no value ever needs negating out of its representable
//range, on ANY machine/wordsize (that's what "regardless of the machine"
//in the exercise is asking for: this reasoning depends only on two's
//complement asymmetry, not on int being 32 bits specifically).
void itoa(int n, char s[])
{
    int i, sign;

    sign = n;         //record sign before n is touched
    if (n > 0)
        n = -n;       //make n <= 0 -- safe in both directions now
    i = 0;
    do {                          //generate digits in reverse order
        s[i++] = '0' - n % 10;    //n <= 0, so n%10 is in [-9, 0]
    } while ((n /= 10) != 0);     //delete it; stays <= 0
    if (sign < 0)
        s[i++] = '-';
    s[i] = '\0';
    reverse(s);
}

int main(void)
{
    int tests[] = {0, 7, -7, 123, -123, 2147483647, -2147483647, INT_MIN};
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;
    char s[20];

    for (i = 0; i < ntests; i++) {
        itoa(tests[i], s);
        printf("itoa(%12d) = \"%s\"\n", tests[i], s);
    }

    return 0;
}

*/

/*

#include <stdio.h>
#include <ctype.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 3-3: expands(s1, s2) -- expand shorthand ranges like a-z in
//s1 into the full list (abc...xyz) in s2. A '-' only starts a range when
//it sits directly between two letters of the SAME case, or two digits
//(never letter-to-digit, never lower-to-upper), and the left endpoint is
//<= the right one -- is_range() below is that whole rule in one place.
//Any '-' that doesn't satisfy it is copied through literally, and that
//single fallback is what handles every one of the tricky cases at once:
//  -a-z    leading '-' has no letter before it            -> stays literal
//  a-z-    trailing '-' has no letter after it             -> stays literal
//  z-a     'z' > 'a', a backwards range                    -> stays literal,
//          both chars and the dash copied one at a time
//  a-b-c   'a-b' expands normally (i jumps past it to the second '-');
//          that second '-' is now the CURRENT character being examined,
//          and the character in front of it was already consumed as the
//          end of the previous range, so it can't be reused as a new left
//          endpoint -- the second '-' is therefore literal too, giving
//          "ab-c" rather than "abc". This is a deliberate reading of an
//          inherently ambiguous input (the exercise only asks to handle
//          it without breaking, not to guess a "smarter" chained meaning).
int is_range(int lo, int hi)
{
    if (isdigit(lo) && isdigit(hi))
        return lo <= hi;
    if (islower(lo) && islower(hi))
        return lo <= hi;
    if (isupper(lo) && isupper(hi))
        return lo <= hi;
    return 0;
}

void expands(char s1[], char s2[])
{
    int i, j, k;

    i = j = 0;
    while (s1[i] != '\0') {
        if (s1[i+1] == '-' && s1[i+2] != '\0' &&
            is_range((unsigned char) s1[i], (unsigned char) s1[i+2])) {
            for (k = s1[i]; k <= s1[i+2]; k++)
                s2[j++] = k;
            i += 3;   //past both endpoints and the dash between them
        } else {
            s2[j++] = s1[i++];
        }
    }
    s2[j] = '\0';
}

int main(void)
{
    char *tests[] = {
        "a-z",
        "A-Z",
        "a-z0-9",
        "A-Fa-f0-9",
        "-a-z",
        "a-z-",
        "a-b-c",
        "z-a",
        "xyz",
    };
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;
    char out[200];

    for (i = 0; i < ntests; i++) {
        expands(tests[i], out);
        printf("expands(\"%-10s\") = \"%s\"\n", tests[i], out);
    }

    return 0;
}

*/

/*

#include <stdio.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 3.5: reverse(s) -- reverse string s in place
void reverse(char s[])
{
    int c, i, j;

    for (i = 0, j = strlen(s)-1; i < j; i++, j--) {
        c = s[i], s[i] = s[j], s[j] = c;
    }
}

int main(void)
{
    char tests[][20] = {"hello", "a", "", "ab", "racecar", "K&R2"};
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;

    for (i = 0; i < ntests; i++) {
        printf("before: \"%s\"\n", tests[i]);
        reverse(tests[i]);
        printf("after:  \"%s\"\n\n", tests[i]);
    }

    return 0;
}

*/

/*
#include <stdio.h>
#include <unistd.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//infinite loop, as generated by Groq (openai/gpt-oss-120b) -- "while (1)"
//never becomes false on its own, so nothing inside ever breaks out; the
//only way to stop it is Ctrl+C (SIGINT) in the terminal it's running in
int main(void)
{
    int i = 0;

    while (1) {
        printf("(integrity + compounding) ++... (%d)\n", i++);
        fflush(stdout);
        sleep(1);
    }

    return 0;
}

*/

/*
#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2: shellsort -- sort v[0]...v[n-1] into increasing order using
//diminishing gaps (n/2, n/4, ..., 1); each pass is an insertion sort
//on elements gap apart, so early passes move far-out-of-place values
//a long way in one step instead of one slot at a time
void shellsort(int v[], int n)
{
    int gap, i, j, temp;

    for (gap = n/2; gap > 0; gap /= 2)
        for (i = gap; i < n; i++)
            for (j = i-gap; j >= 0 && v[j] > v[j+gap]; j -= gap) {
                temp = v[j];
                v[j] = v[j+gap];
                v[j+gap] = temp;
            }
}

void printv(int v[], int n)
{
    int i;

    for (i = 0; i < n; i++)
        printf("%d ", v[i]);
    printf("\n");
}

int main(void)
{
    int v[] = { 9, 3, 7, 1, 8, 2, 5, 0, 6, 4 };
    int n = sizeof(v) / sizeof(v[0]);

    printf("before: ");
    printv(v, n);

    shellsort(v, n);

    printf("after:  ");
    printv(v, n);

    return 0;
}

*/

/*

#include <stdio.h>
#include <ctype.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 4.9: atoi, version 2 -- skips leading white space, then an
//optional sign, then converts the leading run of digits to int
int atoi(char s[])
{
    int i, n, sign;

    for (i = 0; isspace(s[i]); i++)  //skip white space
        ;
    sign = (s[i] == '-') ? -1 : 1;
    if (s[i] == '+' || s[i] == '-')  //skip sign
        i++;
    for (n = 0; isdigit(s[i]); i++)
        n = 10 * n + (s[i] - '0');
    return sign * n;
}

int main(void)
{
    char *tests[] = {
        "  123",
        "  -456",
        "+789",
        "   0",
        "42abc",
        "-  7",     //space between sign and digits -- watch this one
    };
    int ntests = sizeof(tests) / sizeof(tests[0]);
    int i;

    for (i = 0; i < ntests; i++)
        printf("atoi(\"%s\") = %d\n", tests[i], atoi(tests[i]));

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//skip-whitespace warm-up: read and discard chars until the first
//non-whitespace one (or EOF), then report what stopped the loop
int main(void)
{
    int c;

    while ((c = getchar()) == ' ' || c == '\n' || c == '\t')
        ;   //skip white space characters

    printf("first non-whitespace char: ");
    if (c == EOF)
        printf("EOF\n");
    else
        printf("'%c' (%d)\n", c, c);

    return 0;
}

*/

/*

#include <stdio.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 3-2: escape(s, t) converts characters like newline and tab
//into visible two-character escape sequences (\n, \t, ...) as it copies t
//into s; unescape(s, t) does the reverse, turning those sequences back
//into the real control characters. a literal backslash in t must ALSO be
//escaped to \\ by escape() -- otherwise unescape() can't tell an escaped
//backslash apart from a real one that just happens to be followed by,
//say, 'n', and the round trip through both functions would break.
void escape(char s[], char t[])
{
    int i, j;

    for (i = j = 0; t[i] != '\0'; i++) {
        switch (t[i]) {
        case '\n': s[j++] = '\\'; s[j++] = 'n';  break;
        case '\t': s[j++] = '\\'; s[j++] = 't';  break;
        case '\\': s[j++] = '\\'; s[j++] = '\\'; break;
        case '\"': s[j++] = '\\'; s[j++] = '\"'; break;
        case '\b': s[j++] = '\\'; s[j++] = 'b';  break;
        case '\f': s[j++] = '\\'; s[j++] = 'f';  break;
        case '\r': s[j++] = '\\'; s[j++] = 'r';  break;
        case '\a': s[j++] = '\\'; s[j++] = 'a';  break;
        case '\v': s[j++] = '\\'; s[j++] = 'v';  break;
        default:
            s[j++] = t[i];
            break;
        }
    }
    s[j] = '\0';
}

//unescape: reverse of escape() -- turns two-character sequences like \n
//back into the single real character they represent. a backslash not
//followed by a recognized letter is copied through as-is (including the
//backslash itself) rather than silently dropped, so unrecognized input
//doesn't lose data.
void unescape(char s[], char t[])
{
    int i, j;

    for (i = j = 0; t[i] != '\0'; i++) {
        if (t[i] != '\\') {
            s[j++] = t[i];
            continue;
        }
        switch (t[i + 1]) {
        case 'n':  s[j++] = '\n'; i++; break;
        case 't':  s[j++] = '\t'; i++; break;
        case '\\': s[j++] = '\\'; i++; break;
        case '\"': s[j++] = '\"'; i++; break;
        case 'b':  s[j++] = '\b'; i++; break;
        case 'f':  s[j++] = '\f'; i++; break;
        case 'r':  s[j++] = '\r'; i++; break;
        case 'a':  s[j++] = '\a'; i++; break;
        case 'v':  s[j++] = '\v'; i++; break;
        default:
            s[j++] = t[i];   //unrecognized escape: keep the backslash literally
            break;
        }
    }
    s[j] = '\0';
}

int main(void)
{
    char original[] = "line1\nline2\ttabbed\\backslash\"quoted\"end";
    char escaped[200], restored[200];

    escape(escaped, original);
    printf("original: \"%s\"\n", original);
    printf("escaped:  \"%s\"\n", escaped);

    unescape(restored, escaped);
    printf("restored: \"%s\"\n", restored);
    printf("round trip %s\n", strcmp(original, restored) == 0 ? "matches" : "DIFFERS -- bug!");

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//count digits, white space, others

int main()
{
    int c, i, nwhite, nother, ndigit[10];

    nwhite = nother = 0;
    for (i = 0; i < 10; i++)
        ndigit[i] = 0;

    while ((c = getchar()) != EOF) {
        switch (c) {
        case '0': case '1': case '2': case '3': case '4':
        case '5': case '6': case '7': case '8': case '9':
            ndigit[c-'0']++;
            break;
        case ' ':
        case '\n':
        case '\t':
            nwhite++;
            break;
        default:
            nother++;
            break;
        }
    }

    printf("digits =");
    for (i = 0; i < 10; i++)
        printf(" %d", ndigit[i]);
    printf(", white space = %d, other = %d\n",
        nwhite, nother);
    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//exercise: implement score_to_grade(int score) using a switch statement.
//score is meant to be 0-100. grade boundaries:
//    90-100 -> 'A'      70-79 -> 'C'      below 60 -> 'F'
//    80-89  -> 'B'      60-69 -> 'D'
//anything outside 0-100 -> '?'
//
//switch can't test a range directly ("case 90...100" isn't standard C),
//so switch on score/10 instead -- that collapses each ten-point band into
//one small integer. watch out: a score of 100 lands on band 10, while
//90-99 lands on band 9, but both are grade 'A'. handle that with a
//deliberate empty case falling through (same trick as the ndigit example
//further down in the archive), not by writing "return 'A';" twice.
char score_to_grade(int score)
{
    if (score < 0 || score > 100)
        return '?';

    switch (score / 10) {
    case 10:
    case 9:
        return 'A';
    case 8:
        return 'B';
    case 7:
        return 'C';
    case 6:
        return 'D';
    default:
        return 'F';
    }
}

int main(void)
{
    int tests[] = {100, 95, 90, 89, 80, 75, 70, 65, 60, 59, 0, -1, 101};
    int n = (int)(sizeof(tests) / sizeof(tests[0]));
    int i;

    for (i = 0; i < n; i++)
        printf("score_to_grade(%4d) = %c\n", tests[i], score_to_grade(tests[i]));

    return 0;
}

*/

/*

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 3.3 follow-up (the question right after binsearch, also
//exercise 3-1): "our binary search makes two tests inside the loop,
//when one would suffice (at the price of more tests outside.) write a
//version with only one test inside the loop and measure the difference
//in run time." binsearch_twotest is the original: up to two comparisons
//per iteration (x < v[mid], then maybe x > v[mid]) before either
//narrowing the range or returning a match. binsearch_onetest narrows
//with a single comparison per iteration and defers the equality check
//to once, after low and high have converged -- "more tests outside."
//
//measured result: no real speedup (sometimes onetest was marginally
//slower, both unoptimized and at -O2). Reason: onetest gives up
//twotest's ability to return the moment it finds an exact match, so it
//always runs the full ~log2(n) iterations down to low==high; that
//roughly cancels out the savings from doing one comparison per
//iteration instead of two. And on modern out-of-order CPUs integer
//comparisons are close to free anyway -- the real cost of binary search
//is cache misses from jumping around a large array unpredictably, which
//is identical for both versions. K&R2 (1988) assumed instruction count
//tracked runtime much more directly than it does on hardware built
//decades later.
#define ARRAYSIZE 1000000
#define NSEARCHES 5000000

int binsearch_twotest(int x, int v[], int n)
{
    int low, high, mid;

    low = 0;
    high = n - 1;
    while (low <= high) {
        mid = (low + high) / 2;
        if (x < v[mid])
            high = mid - 1;
        else if (x > v[mid])
            low = mid + 1;
        else
            return mid;
    }
    return -1;
}

int binsearch_onetest(int x, int v[], int n)
{
    int low, high, mid;

    low = 0;
    high = n - 1;
    while (low < high) {
        mid = (low + high) / 2;
        if (x > v[mid])
            low = mid + 1;
        else
            high = mid;
    }
    if (n > 0 && v[low] == x)
        return low;
    return -1;
}

int main(void)
{
    static int v[ARRAYSIZE];
    int i, x;
    long sum_two = 0, sum_one = 0;
    clock_t start, end;
    double time_two, time_one;

    for (i = 0; i < ARRAYSIZE; i++)
        v[i] = i * 2;   //even numbers only, so ~half of random queries miss

    srand(1);
    start = clock();
    for (i = 0; i < NSEARCHES; i++) {
        x = rand() % (ARRAYSIZE * 2);
        sum_two += binsearch_twotest(x, v, ARRAYSIZE);
    }
    end = clock();
    time_two = (double)(end - start) / CLOCKS_PER_SEC;

    srand(1);   //same key sequence as above, for a fair comparison
    start = clock();
    for (i = 0; i < NSEARCHES; i++) {
        x = rand() % (ARRAYSIZE * 2);
        sum_one += binsearch_onetest(x, v, ARRAYSIZE);
    }
    end = clock();
    time_one = (double)(end - start) / CLOCKS_PER_SEC;

    printf("array size: %d, searches: %d\n", ARRAYSIZE, NSEARCHES);
    printf("two-test:   %.4f s   (checksum %ld)\n", time_two, sum_two);
    printf("one-test:   %.4f s   (checksum %ld)\n", time_one, sum_one);
    printf("checksums %s\n", sum_two == sum_one ? "match (same results)" : "DIFFER -- bug!");
    printf("speedup:    %.2fx\n", time_two / time_one);

    return 0;
}

*/

/*

#include <stdio.h>
#include <unistd.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//a genuine infinite loop, for practicing how to stop one: "while (1)"
//never becomes false on its own, so nothing inside this loop ever
//breaks or returns out of it. Run it (./cc-c) and it prints one line
//per second forever -- to stop it, press Ctrl+C in the terminal it's
//running in. That sends the process a SIGINT signal, whose default
//action is to terminate the program immediately; without a handler
//installed for it (none is here), the process just dies on the spot.
int main(void)
{
    int i = 0;

    while (1) {
        printf("looping... %d\n", i++);
        fflush(stdout);
        sleep(1);
    }

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2's binsearch, as given, with a real bug (not a style nit like the
//two dangling-else examples above it in the archive): in the x < v[mid]
//branch it sets "high = mid + 1" where it should be "high = mid - 1".
//That moves the wrong end of the search window -- instead of shrinking
//high down below mid to search the LOWER half, it can push high back up
//to (or past) where it already was. Once low and high converge on a mid
//that keeps failing the same way, low never increases and high never
//decreases: the loop condition "low <= high" stays true forever. The
//buggy version below caps itself at 20 iterations and reports the stuck
//state instead of actually hanging, so this file stays safe to run;
//binsearch_fixed alongside it is the one-character fix.
int binsearch_buggy(int x, int v[], int n)
{
    int low, high, mid, iters;

    low = 0;
    high = n - 1;
    iters = 0;
    while (low <= high) {
        if (++iters > 20) {
            printf("    ...bailing out after %d iterations -- infinite loop\n", iters - 1);
            return -2;
        }
        mid = (low+high)/2;
        printf("    iter %2d: low=%d high=%d mid=%d v[mid]=%d\n", iters, low, high, mid, v[mid]);
        if (x < v[mid])
            high = mid + 1;   //BUG: should be mid - 1
        else if (x  > v[mid])
            low = mid + 1;
        else    //found match
            return mid;
    }
    return -1;   //no match
}

int binsearch_fixed(int x, int v[], int n)
{
    int low, high, mid;

    low = 0;
    high = n - 1;
    while (low <= high) {
        mid = (low+high)/2;
        if (x < v[mid])
            high = mid - 1;
        else if (x  > v[mid])
            low = mid + 1;
        else    //found match
            return mid;
    }
    return -1;   //no match
}

int main(void)
{
    int v[] = {1, 3, 5, 7, 9, 11};
    int n = 6;

    printf("searching for x=1 (present, at index 0) -- buggy version:\n");
    printf("  result = %d\n\n", binsearch_buggy(1, v, n));

    printf("searching for x=1 -- fixed version:\n");
    printf("  result = %d\n\n", binsearch_fixed(1, v, n));

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 3.3's own dangling-else example: a for loop sits between
//the outer and inner if, which hides the bug even better than a plain
//nested if would. v1 is exactly what K&R2 shows, marked WRONG --
//indentation suggests the else belongs to "if (n > 0)", but it actually
//binds to the innermost "if (s[i] > 0)". Two consequences fall out of
//that: (1) when n <= 0, the outer if now has no else left at all, so
//the "n is negative" message silently never fires; (2) while the loop
//runs, the else fires on every non-positive element, printing that
//"error" message repeatedly for perfectly ordinary loop iterations.
//v2 wraps the for loop in braces, sealing the inner if off so the else
//is forced back onto the outer if, matching the original intent.
int find_positive_v1(int n, int s[])
{
    int i;

    if (n > 0)
        for (i = 0; i < n; i++)
            if (s[i] > 0) {
                printf("  v1: found positive at i=%d\n", i);
                return i;
            }
    else        //WRONG
        printf("  v1: error -- n is negative\n");
    return -1;
}

int find_positive_v2(int n, int s[])
{
    int i;

    if (n > 0) {
        for (i = 0; i < n; i++)
            if (s[i] > 0) {
                printf("  v2: found positive at i=%d\n", i);
                return i;
            }
    } else
        printf("  v2: error -- n is negative\n");
    return -1;
}

void run(const char *label, int n, int s[])
{
    printf("case: %s (n=%d)\n", label, n);
    find_positive_v1(n, s);
    find_positive_v2(n, s);
    printf("\n");
}

int main(void)
{
    int a[] = {1, 2, 3};
    int b[] = {-1, -2, 5};
    int c[] = {5, -1, -2};
    int d[] = {-1, -2, -3};

    run("n negative", -1, a);
    run("positive found after two non-positives", 3, b);
    run("positive found immediately", 3, c);
    run("no positive at all", 3, d);

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 3.3: the "dangling else" -- else always binds to the
//NEAREST unmatched if, no matter how the source is indented. version1
//below looks like the else belongs to "if (n > 0)" but the compiler
//(gcc warns: -Wdangling-else) actually attaches it to the inner
//"if (a > b)", so when n <= 0 the whole statement is skipped and z is
//left untouched. version2 adds braces around the inner if, which seals
//it off so the else is forced to pair with the outer "if (n > 0)"
//instead -- giving genuinely different behavior, not just different
//style, for the same two inputs.
int version1(int n, int a, int b)
{
    int z = -999;   //sentinel meaning "z was never assigned"

    if (n > 0)
        if (a > b)
            z = a;
        else
            z = b;
    return z;
}

int version2(int n, int a, int b)
{
    int z = -999;

    if (n > 0) {
        if (a > b)
            z = a;
    }
    else
        z = b;
    return z;
}

int main(void)
{
    struct { int n, a, b; } cases[] = {
        {5, 3, 1},    //n>0, a>b
        {5, 1, 3},    //n>0, a<=b
        {-1, 3, 1},   //n<=0 (a,b irrelevant)
        {-1, 1, 3},
    };
    int i;

    for (i = 0; i < 4; i++) {
        int n = cases[i].n, a = cases[i].a, b = cases[i].b;
        printf("n=%3d a=%d b=%d | version1=%-5d version2=%-5d\n",
               n, a, b, version1(n, a, b), version2(n, a, b));
    }

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 3.3: the switch statement -- rewrites the digit/whitespace/
//other counting program from chapter 2 (see the ndigit/nwhite/nother
//version further down in the archive) using switch instead of an
//if-else chain. switch tests one integer expression against a set of
//constant case labels; control falls through from one case into the
//next unless a break stops it -- that fallthrough is switch's one real
//trap, which is exactly why every case below ends with an explicit
//break, and why the ten digit cases are deliberately left to fall
//through each other (no break between them) to share one action.
int main(void)
{
    int c, i, nwhite, nother;
    int ndigit[10];

    nwhite = nother = 0;
    for (i = 0; i < 10; ++i)
        ndigit[i] = 0;

    while ((c = getchar()) != EOF) {
        switch (c) {
        case '0': case '1': case '2': case '3': case '4':
        case '5': case '6': case '7': case '8': case '9':
            ++ndigit[c - '0'];
            break;
        case ' ':
        case '\n':
        case '\t':
            ++nwhite;
            break;
        default:
            ++nother;
            break;
        }
    }

    printf("digits =");
    for (i = 0; i < 10; ++i)
        printf(" %d", ndigit[i]);
    printf(", white space = %d, other = %d\n", nwhite, nother);

    return 0;
}

*/

/*

#include <stdio.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run from webdev-projects so the relative path below resolves

#define MAXLINE     1000
#define MAXOBJLINES   60   //generous margin over the ~41 lines one hexagram object actually spans
#define MAXFIELD     500   //generous margin over the longest single field (judgment_en/lines_en)
#define ZHOUYI_PATH "python-projects/tcm_app/data/zhouyi.json"

int is_valid_toss(int toss)
{
    return toss == 6 || toss == 7 || toss == 8 || toss == 9;
}

//copy the text between a line's FIRST pair of quotes into out -- used
//for array elements like "初九：潜龙勿用。", which have no key, just
//one quoted string
void extract_first_quoted(char *line, char *out, int outlen)
{
    char *p = strchr(line, '"');
    char *q;
    int len;

    out[0] = '\0';
    if (p == NULL)
        return;
    q = strchr(p + 1, '"');
    if (q == NULL)
        return;
    len = (int)(q - (p + 1));
    if (len >= outlen)
        len = outlen - 1;
    strncpy(out, p + 1, len);
    out[len] = '\0';
}

//copy a "key": "value" line's value into out -- skips past the colon
//first so the KEY's own quotes aren't mistaken for the value's
void extract_value(char *line, char *out, int outlen)
{
    char *colon = strchr(line, ':');

    out[0] = '\0';
    if (colon == NULL)
        return;
    extract_first_quoted(colon, out, outlen);
}

//one full hexagram record, parsed out of zhouyi.json
struct Hexagram {
    int number;
    char chinese[MAXFIELD], pinyin[MAXFIELD], title_en[MAXFIELD];
    char judgment_zh[MAXFIELD], judgment_pinyin[MAXFIELD], judgment_en[MAXFIELD];
    char lines_zh[6][MAXFIELD], lines_pinyin[6][MAXFIELD], lines_en[6][MAXFIELD];
};

//scan zhouyi.json object by object; each object is buffered into obj[]
//as it's read, and once its closing brace is found, its "bits_bottom_up"
//array (parsed along the way) is compared to target[]. only a match gets
//picked apart field by field into *h -- the other 63 objects are read
//but discarded. returns 1 if found, 0 otherwise.
int find_hexagram(int target[6], struct Hexagram *h)
{
    FILE *fp;
    char line[MAXLINE];
    char obj[MAXOBJLINES][MAXLINE];
    int objlen, depth, in_object, in_bits, bitcount, bits_found[6];
    int i, val, matched, section, idx;

    fp = fopen(ZHOUYI_PATH, "r");
    if (fp == NULL) {
        fprintf(stderr, "cannot open %s\n", ZHOUYI_PATH);
        return 0;
    }

    depth = 0;
    in_object = 0;
    in_bits = 0;
    bitcount = 0;
    objlen = 0;

    while (fgets(line, MAXLINE, fp) != NULL) {
        if (!in_object) {
            if (strchr(line, '{') != NULL) {
                in_object = 1;
                depth = 1;
                objlen = 0;
                if (objlen < MAXOBJLINES)
                    strcpy(obj[objlen++], line);
                in_bits = 0;
                bitcount = 0;
            }
            continue;
        }

        if (objlen < MAXOBJLINES)
            strcpy(obj[objlen++], line);

        if (strstr(line, "\"bits_bottom_up\"") != NULL) {
            in_bits = 1;
            bitcount = 0;
        } else if (in_bits && bitcount < 6 && sscanf(line, " %d", &val) == 1) {
            bits_found[bitcount++] = val;
        }

        if (strchr(line, '}') != NULL) {
            depth--;
            if (depth == 0) {
                matched = 1;
                for (i = 0; i < 6; i++)
                    if (bits_found[i] != target[i])
                        matched = 0;

                if (matched) {
                    h->number = 0;
                    section = 0;   //0=none, 1=lines_zh, 2=lines_pinyin, 3=lines_en
                    idx = 0;

                    for (i = 0; i < objlen; i++) {
                        char *l = obj[i];

                        if (strstr(l, "\"number\"") != NULL)
                            sscanf(l, " \"number\": %d", &h->number);
                        else if (strstr(l, "\"chinese\"") != NULL)
                            extract_value(l, h->chinese, MAXFIELD);
                        else if (strstr(l, "\"pinyin\"") != NULL)
                            extract_value(l, h->pinyin, MAXFIELD);
                        else if (strstr(l, "\"title_en\"") != NULL)
                            extract_value(l, h->title_en, MAXFIELD);
                        else if (strstr(l, "\"judgment_zh\"") != NULL)
                            extract_value(l, h->judgment_zh, MAXFIELD);
                        else if (strstr(l, "\"judgment_pinyin\"") != NULL)
                            extract_value(l, h->judgment_pinyin, MAXFIELD);
                        else if (strstr(l, "\"judgment_en\"") != NULL)
                            extract_value(l, h->judgment_en, MAXFIELD);
                        else if (strstr(l, "\"lines_zh\"") != NULL)
                            { section = 1; idx = 0; }
                        else if (strstr(l, "\"lines_pinyin\"") != NULL)
                            { section = 2; idx = 0; }
                        else if (strstr(l, "\"lines_en\"") != NULL)
                            { section = 3; idx = 0; }
                        else if (strstr(l, "\"bits_bottom_up\"") != NULL)
                            section = 0;
                        else if (section != 0 && idx < 6 && strchr(l, '"') != NULL) {
                            if (section == 1)
                                extract_first_quoted(l, h->lines_zh[idx], MAXFIELD);
                            else if (section == 2)
                                extract_first_quoted(l, h->lines_pinyin[idx], MAXFIELD);
                            else
                                extract_first_quoted(l, h->lines_en[idx], MAXFIELD);
                            idx++;
                        }
                    }

                    fclose(fp);
                    return 1;
                }
                in_object = 0;
            }
        }
    }

    fclose(fp);
    return 0;
}

void print_hexagram(struct Hexagram *h)
{
    int i;

    printf("Hexagram %d: %s (%s) -- %s\n", h->number, h->chinese, h->pinyin, h->title_en);
    printf("========================================\n\n");
    printf("Judgment:\n  %s\n  %s\n  %s\n\n", h->judgment_zh, h->judgment_pinyin, h->judgment_en);
    printf("Lines (bottom to top):\n\n");
    for (i = 0; i < 6; i++)
        printf("  %d. %s\n     %s\n     %s\n\n",
               i + 1, h->lines_zh[i], h->lines_pinyin[i], h->lines_en[i]);
}

void print_line_text(struct Hexagram *h, int idx, char *label)
{
    printf("%s (line %d):\n  %s\n  %s\n  %s\n\n",
           label, idx + 1, h->lines_zh[idx], h->lines_pinyin[idx], h->lines_en[idx]);
}

int main(void)
{
    int toss_list[6], original[6], changed[6], changing[6];
    int toss, i, nchanging, upper, lower, unchanged;
    struct Hexagram primary, secondary;
    int have_secondary;

    printf("enter 6 coin-toss totals, bottom line first:\n");
    for (i = 0; i < 6; i++) {
        do {
            printf("line %d (6, 7, 8, or 9): ", i + 1);
            scanf("%d", &toss);
        } while (!is_valid_toss(toss));
        toss_list[i] = toss;
        original[i] = toss % 2;                   //odd = yang, even = yin
        changing[i] = (toss == 6 || toss == 9);    //"old" lines are the ones that move
        changed[i] = changing[i] ? 1 - original[i] : original[i];
    }

    nchanging = 0;
    for (i = 0; i < 6; i++)
        if (changing[i])
            nchanging++;

    printf("\ntosses (bottom to top): ");
    for (i = 0; i < 6; i++)
        printf("%d ", toss_list[i]);
    printf("\nchanging lines: %d\n\n", nchanging);

    if (!find_hexagram(original, &primary)) {
        fprintf(stderr, "primary hexagram not found\n");
        return 1;
    }

    have_secondary = (nchanging > 0) && find_hexagram(changed, &secondary);

    print_hexagram(&primary);

    //the traditional (Zhu Xi) rule for which text is the operative
    //reading, depending on how many lines are changing
    printf("----------------------------------------\n");
    printf("Chosen judgment:\n\n");

    if (nchanging == 0) {
        printf("No changing lines -- the hexagram's own judgment above is the reading.\n\n");
    } else if (nchanging == 1) {
        for (i = 0; i < 6; i++)
            if (changing[i])
                print_line_text(&primary, i, "Changing line");
    } else if (nchanging == 2) {
        upper = -1;
        for (i = 5; i >= 0; i--)
            if (changing[i]) { upper = i; break; }
        print_line_text(&primary, upper, "Upper of the two changing lines");
    } else if (nchanging == 3) {
        printf("Three lines changing -- read both judgments together:\n\n");
        printf("Primary judgment:\n  %s\n  %s\n  %s\n\n",
               primary.judgment_zh, primary.judgment_pinyin, primary.judgment_en);
        if (have_secondary)
            printf("Resulting judgment:\n  %s\n  %s\n  %s\n\n",
                   secondary.judgment_zh, secondary.judgment_pinyin, secondary.judgment_en);
    } else if (nchanging == 4) {
        lower = -1;
        for (i = 0; i < 6; i++)
            if (!changing[i]) { lower = i; break; }
        if (have_secondary)
            print_line_text(&secondary, lower, "Lower of the two unchanged lines, read in the resulting hexagram");
    } else if (nchanging == 5) {
        unchanged = -1;
        for (i = 0; i < 6; i++)
            if (!changing[i]) { unchanged = i; break; }
        if (have_secondary)
            print_line_text(&secondary, unchanged, "The one unchanged line, read in the resulting hexagram");
    } else {   //nchanging == 6
        if (have_secondary)
            printf("All six lines changing -- use the resulting hexagram's judgment:\n  %s\n  %s\n  %s\n\n",
                   secondary.judgment_zh, secondary.judgment_pinyin, secondary.judgment_en);
        if (primary.number == 1 || primary.number == 2)
            printf("(note: qian/kun traditionally use a special \"yong jiu\"/\"yong liu\" text\n"
                   "here; this data file only stores it embedded in each one's own line 6\n"
                   "above, not as a separate field.)\n\n");
    }

    if (have_secondary) {
        printf("----------------------------------------\n");
        printf("Resulting hexagram (after the change):\n\n");
        print_hexagram(&secondary);
    }

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 2-10: rewrite lower(), which converts uppercase letters to
//lowercase, using a conditional expression instead of if/else -- both
//branches just produce a value to return, so the whole function body
//collapses to one expression
int lower(int c)
{
    return (c >= 'A' && c <= 'Z') ? c + 'a' - 'A' : c;
}

int main(void)
{
    printf("lower('A') = %c\n", lower('A'));
    printf("lower('Z') = %c\n", lower('Z'));
    printf("lower('a') = %c\n", lower('a'));
    printf("lower('5') = %c\n", lower('5'));
    printf("lower('!') = %c\n", lower('!'));

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 2.11: two more conditional-expression idioms --
//(1) print an array 10 values per line, forcing a break at the array's
//    true end too (i == n-1), even if that last row isn't a full 10
//(2) singular/plural word agreement in one line via ?: instead of if/else
int main(void)
{
    int a[] = {0,1,4,9,16,25,36,49,64,81,100,121,144,169,196,225,256,
               289,324,361,400,441,484,529,576};
    int counts[] = {0, 1, 2, 5};
    int n, ncounts, i;

    n = (int)(sizeof(a) / sizeof(a[0]));
    ncounts = (int)(sizeof(counts) / sizeof(counts[0]));

    for (i = 0; i < n; i++)
        printf("%6d%c", a[i], (i % 10 == 9 || i == n - 1) ? '\n' : ' ');

    printf("\n");
    for (i = 0; i < ncounts; i++)
        printf("You have %d item%s.\n", counts[i], counts[i] == 1 ? "" : "s");

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 2.11: type conversion inside a conditional expression --
//when the second and third operands have different types (float vs int
//here), the WHOLE expression's type is fixed at compile time by C's
//usual arithmetic conversions, no matter which branch actually runs.
//demonstrated with an int too large for float to represent exactly
//(2^24 + 1), so the "n" branch silently loses precision even though
//the float branch (f) is never touched.
int main(void)
{
    int n = -16777217;     //-(2^24 + 1): n > 0 is false, so "n" is selected
    float f = 3.14f;

    printf("n              = %d\n", n);
    printf("(n > 0) ? f : n = %f\n", (n > 0) ? f : n);
    printf("-- n was the branch selected, but the expression's type is\n"
           "float (forced by f's presence), so n was silently converted\n"
           "and lost precision even though f itself was never evaluated\n");

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 2-9: faster bitcount using x &= (x-1), which clears the
//rightmost 1-bit of x each pass -- so the loop runs once per SET bit
//instead of once per bit position, unlike the naive shift-and-test version
int bitcount(unsigned x)
{
    int b;
    for (b = 0; x != 0; x &= (x - 1))
        b++;
    return b;
}

int main(void)
{
    printf("bitcount(0)    = %d\n", bitcount(0));
    printf("bitcount(1)    = %d\n", bitcount(1));
    printf("bitcount(7)    = %d\n", bitcount(7));
    printf("bitcount(0x6A) = %d   -- 0x6A is 01101010, four 1-bits\n", bitcount(0x6A));
    printf("bitcount(0xFF) = %d\n", bitcount(0xFF));
    printf("bitcount(~0u)  = %d   -- all bits set, so this equals the width of unsigned\n", bitcount(~0u));

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//bitcount:  count 1 bits in x
int bitcount(unsigned x)
{
    int b;
    for (b = 0; x != 0; x >>= 1)
        if (x & 01)
            b++;
    return b;
}

int main(void)
{
    printf("bitcount(0)    = %d\n", bitcount(0));
    printf("bitcount(1)    = %d\n", bitcount(1));
    printf("bitcount(7)    = %d\n", bitcount(7));
    printf("bitcount(0x6A) = %d   -- 0x6A is 01101010, four 1-bits\n", bitcount(0x6A));
    printf("bitcount(0xFF) = %d\n", bitcount(0xFF));
    printf("bitcount(~0u)  = %d   -- all bits set, so this equals the width of unsigned\n", bitcount(~0u));

    return 0;
}

*/

/*

#include <stdio.h>
#include <limits.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 2-8: rightrot(x,n) returns x rotated right by n bit
//positions; bits that fall off the low end wrap around to become the
//new high bits (a circular rotation -- no bits are lost, unlike a
//plain shift). width is derived from sizeof(x)*CHAR_BIT rather than
//hardcoded, so this works whatever the actual width of unsigned is on
//a given machine. presumably n is in [0, width); n == 0 is handled
//explicitly since shifting by the full width would otherwise be
//undefined behavior.

//print_bits: print the low nbits bits of x, most significant bit first
void print_bits(unsigned x, int nbits)
{
    int i;
    for (i = nbits - 1; i >= 0; i--)
        putchar((x & (1u << i)) ? '1' : '0');
}

unsigned rightrot(unsigned x, int n)
{
    int bits = (int) sizeof(x) * CHAR_BIT;   //width of unsigned on this machine

    n %= bits;   //rotating by the full width (or a multiple of it) is a no-op
    if (n == 0)  //n == 0 would make x << bits below undefined behavior
        return x;

    return (x >> n) | (x << (bits - n));
}

int main(void)
{
    unsigned x = 0x6A;
    int bits = (int) sizeof(x) * CHAR_BIT;

    printf("             x = "); print_bits(x, bits); printf("   (0x%X)\n", x);
    printf("      --------------\n");

    printf("rightrot(x, 1) = "); print_bits(rightrot(x, 1), bits);
    printf("   -- bit 0 wraps around to become the top bit\n");

    printf("rightrot(x, 3) = "); print_bits(rightrot(x, 3), bits);
    printf("   -- lowest 3 bits wrap around to become the top 3 bits\n");

    printf("rightrot(x, bits) = "); print_bits(rightrot(x, bits), bits);
    printf("   -- rotating by the full width is a no-op\n");

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 2-7: invert(x,p,n) returns x with the n bits that begin
//at position p inverted (1 -> 0, 0 -> 1), leaving the other bits of x
//unchanged. bits are numbered from the right, 0 is the least
//significant bit; the field occupies p, p-1, ..., p-n+1 (same bit
//numbering as K&R's getbits/setbits).

//print_bits: print the low nbits bits of x, most significant bit first
void print_bits(unsigned x, int nbits)
{
    int i;
    for (i = nbits - 1; i >= 0; i--)
        putchar((x & (1u << i)) ? '1' : '0');
}

unsigned invert(unsigned x, int p, int n)
{
    unsigned lowmask = ~(~0u << n);              //n 1-bits, low end
    unsigned fieldmask = lowmask << (p + 1 - n);  //those n bits, shifted into place

    return x ^ fieldmask;
}

int main(void)
{
    unsigned char x = 0x6A;   //0110 1010

    printf("      x = "); print_bits(x, 8); printf("   (0x%02X)\n", x);
    printf("      --------------\n");

    printf("invert(x, 3, 4) = "); print_bits(invert(x, 3, 4), 8);
    printf("   -- low nibble toggled, top nibble unchanged\n");

    printf("invert(x, 5, 3) = "); print_bits(invert(x, 5, 3), 8);
    printf("   -- bits 5-3 toggled, rest unchanged\n");

    printf("invert(x, 7, 8) = "); print_bits(invert(x, 7, 8), 8);
    printf("   -- every bit toggled, i.e. same as ~x\n");

    return 0;
}

*/

/*
#include <stdio.h>
#include <limits.h>

int main(void)
{
    printf("sizeof(int) = %zu bytes = %zu bits\n", sizeof(int), sizeof(int) * CHAR_BIT);
    return 0;
}

*/


/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 2-6: setbits(x,p,n,y) returns x with the n bits that
//begin at position p set to the rightmost n bits of y, leaving the
//other bits of x unchanged. bits are numbered from the right, 0 is
//the least significant bit; the field occupies p, p-1, ..., p-n+1
//(same bit numbering as K&R's own getbits example).

//print_bits: print the low nbits bits of x, most significant bit first
void print_bits(unsigned x, int nbits)
{
    int i;
    for (i = nbits - 1; i >= 0; i--)
        putchar((x & (1u << i)) ? '1' : '0');
}

unsigned setbits(unsigned x, int p, int n, unsigned y)
{
    unsigned lowmask = ~(~0u << n);              //n 1-bits, low end
    unsigned fieldmask = lowmask << (p + 1 - n);  //those n bits, shifted into place

    return (x & ~fieldmask) | ((y & lowmask) << (p + 1 - n));
}

int main(void)
{
    unsigned char x = 0x6A;   //0110 1010
    unsigned char y = 0x0F;   //0000 1111 -- rightmost 4 bits are 1111

    printf("      x = "); print_bits(x, 8); printf("   (0x%02X)\n", x);
    printf("      y = "); print_bits(y, 8); printf("   (0x%02X)\n", y);
    printf("      --------------\n");

    printf("setbits(x, 7, 4, y) = "); print_bits(setbits(x, 7, 4, y), 8);
    printf("   -- top 4 bits of x replaced by rightmost 4 bits of y\n");

    printf("setbits(x, 3, 2, y) = "); print_bits(setbits(x, 3, 2, y), 8);
    printf("   -- bits 3-2 of x replaced by rightmost 2 bits of y\n");

    printf("setbits(x, 7, 8, y) = "); print_bits(setbits(x, 7, 8, y), 8);
    printf("   -- all 8 bits of x replaced by y (field spans the full width)\n");

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 section 2.9: bitwise operators -- demonstrate &, |, ^, ~, <<, >>
//by printing operands and results as aligned binary alongside hex/decimal

//print_bits: print the low nbits bits of x, most significant bit first
void print_bits(unsigned char x, int nbits)
{
    int i;
    for (i = nbits - 1; i >= 0; i--)
        putchar((x & (1 << i)) ? '1' : '0');
}

int main(void)
{
    unsigned char x = 0x6A;
    unsigned char y = 0x53;

    printf("      x = "); print_bits(x, 8); printf("   (0x%02X, %d)\n", x, x);
    printf("      y = "); print_bits(y, 8); printf("   (0x%02X, %d)\n", y, y);
    printf("      --------------\n");
    printf("  x & y = "); print_bits(x & y, 8); printf("   (0x%02X)\n", x & y);
    printf("  x | y = "); print_bits(x | y, 8); printf("   (0x%02X)\n", x | y);
    printf("  x ^ y = "); print_bits(x ^ y, 8); printf("   (0x%02X)\n", x ^ y);
    printf("     ~x = "); print_bits(~x, 8); printf("   (0x%02X)\n", (unsigned char) ~x);

    printf("\n");
    printf("      x      = "); print_bits(x, 8); printf("   (%d)\n", x);
    printf("      x << 2 = "); print_bits((unsigned char) (x << 2), 8);
    printf("   (%d)  -- x*4 would be %d, too big for 8 bits: the top bits\n", (unsigned char) (x << 2), x * 4);
    printf("                       fall off the end and only 168 is left\n");
    printf("      x >> 2 = "); print_bits(x >> 2, 8);
    printf("   (%d)  -- same as x / 4\n", x >> 2);

    printf("\n");
    printf("bit idioms on x, testing/setting/clearing/toggling bit 3:\n");
    printf("  test  x & (1<<3)        : %s\n", (x & (1 << 3)) ? "set" : "clear");
    printf("  set   x | (1<<3)  = ");   print_bits(x | (1 << 3), 8);   putchar('\n');
    printf("  clear x & ~(1<<3) = ");   print_bits(x & ~(1 << 3), 8); putchar('\n');
    printf("  toggle x ^ (1<<3) = ");   print_bits(x ^ (1 << 3), 8);  putchar('\n');

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//any(s1, s2): return the index of the first location in s1 where any
//character from s2 occurs, or -1 if s1 contains none of s2's characters.
//(the standard library's strpbrk does the same job but returns a pointer
//to the location instead of an index)
int any(char s1[], char s2[])
{
    int i, j;

    for (i = 0; s1[i] != '\0'; i++)
        for (j = 0; s2[j] != '\0'; j++)
            if (s1[i] == s2[j])
                return i;
    return -1;
}

int main(void)
{
    printf("any(\"hello world\", \"wor\") = %d\n", any("hello world", "wor"));
    printf("any(\"banana\", \"xyz\")      = %d\n", any("banana", "xyz"));
    printf("any(\"banana\", \"an\")       = %d\n", any("banana", "an"));
    printf("any(\"\", \"abc\")            = %d\n", any("", "abc"));
    printf("any(\"abc\", \"\")            = %d\n", any("abc", ""));

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 2-4: squeeze(s1, s2) -- delete each character in s1 that
//matches any character in the string s2
void squeeze(char s1[], char s2[])
{
    int i, j, k;

    for (i = j = 0; s1[i] != '\0'; i++) {
        for (k = 0; s2[k] != '\0' && s2[k] != s1[i]; k++)
            ;
        if (s2[k] == '\0')     //s1[i] wasn't found anywhere in s2
            s1[j++] = s1[i];
    }
    s1[j] = '\0';
}

int main(void)
{
    char s1[] = "banana";
    char s2[] = "hello world";
    char s3[] = "mississippi";
    char s4[] = "xyzxyz";

    squeeze(s1, "an");
    printf("squeeze(\"banana\", \"an\")       = \"%s\"\n", s1);

    squeeze(s2, "lo");
    printf("squeeze(\"hello world\", \"lo\")  = \"%s\"\n", s2);

    squeeze(s3, "is");
    printf("squeeze(\"mississippi\", \"is\")  = \"%s\"\n", s3);

    squeeze(s4, "xyz");
    printf("squeeze(\"xyzxyz\", \"xyz\")      = \"%s\"\n", s4);

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//my_strcat: concatenate t to end of s; s must be big enough; named to
//avoid clashing with the standard strcat() declared in <string.h>
void my_strcat(char s[], char t[])
{
    int i, j;
    i = j = 0;
    while (s[i] != '\0') //find end of s
        i++;
    while ((s[i++] = t[j++]) != '\0') //copy t
        ;
}

int main(void)
{
    char s1[20] = "hello, ";
    char s2[20] = "foo";
    char s3[20] = "";
    char s4[20] = "x";

    my_strcat(s1, "world");
    printf("my_strcat(\"hello, \", \"world\") = \"%s\"\n", s1);

    my_strcat(s2, "bar");
    printf("my_strcat(\"foo\", \"bar\")       = \"%s\"\n", s2);

    my_strcat(s3, "abc");
    printf("my_strcat(\"\", \"abc\")          = \"%s\"\n", s3);

    my_strcat(s4, "");
    printf("my_strcat(\"x\", \"\")            = \"%s\"\n", s4);

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//squeeze: delete all occurrences of c from s
void squeeze(char s[], int c)
{
    int i, j;

    //equivalent compact form: s[j++] = s[i];
    for (i = j = 0; s[i] != '\0'; i++)
        if (s[i] != c) {
            s[j] = s[i];
            j++;
        }
    s[j] = '\0';
}

int main(void)
{
    char s1[] = "banana";
    char s2[] = "mississippi";
    char s3[] = "hello world";
    char s4[] = "xxxxx";

    squeeze(s1, 'a');
    printf("squeeze(\"banana\", 'a')       = \"%s\"\n", s1);

    squeeze(s2, 's');
    printf("squeeze(\"mississippi\", 's')  = \"%s\"\n", s2);

    squeeze(s3, 'l');
    printf("squeeze(\"hello world\", 'l')  = \"%s\"\n", s3);

    squeeze(s4, 'x');
    printf("squeeze(\"xxxxx\", 'x')        = \"%s\"\n", s4);

    return 0;
}

*/

/*

#include <stdio.h>
#include <ctype.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//K&R2 exercise 2-7: htoi(s) -- convert a hex string (with optional
//leading 0x/0X) to its integer value; stops at the first character
//that isn't a valid hex digit
int htoi(char s[])
{
    int i, n, hexdigit;

    i = 0;
    if (s[i] == '0' && (s[i+1] == 'x' || s[i+1] == 'X'))
        i += 2;

    n = 0;
    for ( ; s[i] != '\0'; ++i) {
        if (isdigit((unsigned char) s[i]))
            hexdigit = s[i] - '0';
        else if (s[i] >= 'a' && s[i] <= 'f')
            hexdigit = s[i] - 'a' + 10;
        else if (s[i] >= 'A' && s[i] <= 'F')
            hexdigit = s[i] - 'A' + 10;
        else
            break;
        n = 16 * n + hexdigit;
    }
    return n;
}

int main(void)
{
    printf("htoi(\"0x1A2b\")     = %d\n", htoi("0x1A2b"));
    printf("htoi(\"0X10\")       = %d\n", htoi("0X10"));
    printf("htoi(\"FF\")         = %d\n", htoi("FF"));
    printf("htoi(\"ff\")         = %d\n", htoi("ff"));
    printf("htoi(\"1234\")       = %d\n", htoi("1234"));
    printf("htoi(\"0x\")         = %d\n", htoi("0x"));
    printf("htoi(\"\")           = %d\n", htoi(""));
    printf("htoi(\"123g\")       = %d  (stops before 'g')\n", htoi("123g"));
    printf("htoi(\"0x7fffFFFF\") = %d  (INT_MAX)\n", htoi("0x7fffFFFF"));

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

unsigned long int next = 1;

//rand: return pseudo-random integer on 0..32767
int rand(void)
{
    next = next * 1103515245 + 12345;
    return (unsigned int)(next/65536) % 32768;
}

//srand: set seed for rand()
void srand(unsigned int seed)
{
    next = seed;
}

int main(void)
{
    int i;

    srand(1);
    for (i = 0; i < 5; ++i)
        printf("seed 1: %d\n", rand());

    srand(1);
    for (i = 0; i < 5; ++i)
        printf("seed 1 again: %d\n", rand());

    srand(42);
    for (i = 0; i < 5; ++i)
        printf("seed 42: %d\n", rand());

    return 0;
}

*/

/*

#include <stdio.h>
//compile with: gcc -Wall -Wextra -Wconversion -Wsign-compare cc-c.c -o cc-c

//K&R2 section 2.7: type conversions -- four classic pitfalls, with
//-Wconversion/-Wsign-compare flagging each one at compile time
int main(void)
{
    //1. narrowing: double -> int truncates toward zero, does NOT round
    double d = 3.9;
    int i = d;
    printf("(int) 3.9        = %d\n", i);

    //2. narrowing: int -> char just discards the high-order bits
    int big = 300;
    char c = big;
    printf("(char) 300       = %d\n", c);

    //3. char vs int for getchar()/EOF: the bug depends on whether plain
    //char is signed or unsigned on this platform, so force both cases
    //explicitly to see the failure mode either way
    signed char sc = -1;
    unsigned char uc = (unsigned char) -1;
    printf("signed char -1   == EOF? %d\n", sc == EOF);
    printf("unsigned char -1 == EOF? %d\n", uc == EOF);

    //4. signed/unsigned comparison: the signed side gets converted to
    //unsigned, so a negative number can look "bigger" than a positive one
    int x = -1;
    unsigned int y = 1;
    printf("(-1 < 1u)        = %d\n", x < y);

    return 0;
}

*/

/*

#include <stdio.h>

//lower: convert c to lower case; ASCII only
int lower(int c)
{
    if (c >= 'A' && c <= 'Z')
        return c + 'a' - 'A';
    else
        return c;
}

int main(void)
{
    printf("lower('A') = %c\n", lower('A'));
    printf("lower('Z') = %c\n", lower('Z'));
    printf("lower('a') = %c\n", lower('a'));
    printf("lower('5') = %c\n", lower('5'));
    printf("lower('!') = %c\n", lower('!'));

    return 0;
}

*/

/*

#include <stdio.h>

//atoi: convert s to integer
int atoi(char s[])
{
    int i, n;
    n = 0;
    for (i = 0; s[i] >= '0' && s[i] <= '9'; ++i)
        n = 10 * n + (s[i] - '0');
    return n;
}

int main(void)
{
    printf("atoi(\"123\")  = %d\n", atoi("123"));
    printf("atoi(\"0\")    = %d\n", atoi("0"));
    printf("atoi(\"7\")    = %d\n", atoi("7"));
    printf("atoi(\"12a3\") = %d\n", atoi("12a3"));
    printf("atoi(\"\")     = %d\n", atoi(""));
    printf("atoi(\"-5\")   = %d\n", atoi("-5"));

    return 0;
}

*/

/*

#include <stdio.h>

#define MAXLINE 1000

//K&R2 exercise 2-2: rewrite the for loop
//    for (i=0; i < lim-1 && (c=getchar()) != '\n' && c != EOF; ++i)
//        s[i] = c;
//without using && or ||
int main(void)
{
    char s[MAXLINE];
    int c, i, lim;

    lim = MAXLINE;

    for (i = 0; i < lim - 1; ++i) {
        c = getchar();
        if (c == '\n')
            break;
        if (c == EOF)
            break;
        s[i] = c;
    }
    s[i] = '\0';

    printf("read %d characters: \"%s\"\n", i, s);

    return 0;
}

*/

/*

#include <stdio.h>
#include <limits.h>
#include <float.h>
#include <math.h>
//compile with: cc cc-c.c -lm -o cc-c

//largest value of unsigned type T, found by flipping every bit of zero --
//well-defined for unsigned types, unlike doing the same to a signed one
#define UMAX(T) ((T)~(T)0)

//largest value of the signed type paired with unsigned type UT of the same
//width, found by clearing UT's top (sign) bit; assumes two's complement,
//which every real machine uses and C23 now requires outright
#define SMAX(T, UT) ((T)(UMAX(UT) >> 1))

void print_signed(const char *name, long hdrmin, long hdrmax, long compmin, long compmax);
void print_unsigned(const char *name, unsigned long hdrmax, unsigned long compmax);
float  float_max(void);
double double_max(void);
float  float_smallest_positive(void);
double double_smallest_positive(void);

//K&R2 exercise 2-1: determine the ranges of the integer and floating-point
//types both by reading standard headers and by direct computation
int main(void)
{
    printf("integer types: header (limits.h) vs. computed\n");
    printf("%-14s %14s %14s   %14s %14s\n",
           "type", "hdr min", "hdr max", "comp min", "comp max");

    print_signed("char", CHAR_MIN, CHAR_MAX,
                 CHAR_MIN < 0 ? -SMAX(signed char, unsigned char) - 1 : 0,
                 CHAR_MIN < 0 ? SMAX(signed char, unsigned char) : UMAX(unsigned char));
    print_signed("signed char", SCHAR_MIN, SCHAR_MAX,
                 -SMAX(signed char, unsigned char) - 1, SMAX(signed char, unsigned char));
    print_unsigned("unsigned char", UCHAR_MAX, UMAX(unsigned char));

    print_signed("short", SHRT_MIN, SHRT_MAX,
                 -SMAX(short, unsigned short) - 1, SMAX(short, unsigned short));
    print_unsigned("unsigned short", USHRT_MAX, UMAX(unsigned short));

    print_signed("int", INT_MIN, INT_MAX,
                 -SMAX(int, unsigned int) - 1, SMAX(int, unsigned int));
    print_unsigned("unsigned int", UINT_MAX, UMAX(unsigned int));

    print_signed("long", LONG_MIN, LONG_MAX,
                 -SMAX(long, unsigned long) - 1, SMAX(long, unsigned long));
    print_unsigned("unsigned long", ULONG_MAX, UMAX(unsigned long));

    printf("\nfloating-point types: header (float.h) vs. computed\n");
    printf("%-14s %16s %16s   %16s %16s\n",
           "type", "hdr min(norm)", "hdr max", "comp min(any)", "comp max");
    printf("%-14s %16.6e %16.6e   %16.6e %16.6e\n",
           "float", (double)FLT_MIN, (double)FLT_MAX,
           (double)float_smallest_positive(), (double)float_max());
    printf("%-14s %16.6e %16.6e   %16.6e %16.6e\n",
           "double", (double)DBL_MIN, (double)DBL_MAX,
           double_smallest_positive(), double_max());

    printf("\n(computed float/double min is the smallest positive value at\n"
           "all -- a subnormal -- not the smallest *normalized* value the\n"
           "header names; long double is left out of the computed columns\n"
           "since its width/precision varies too much across platforms to\n"
           "reason about generically here)\n");

    return 0;
}

void print_signed(const char *name, long hdrmin, long hdrmax, long compmin, long compmax)
{
    printf("%-14s %14ld %14ld   %14ld %14ld\n", name, hdrmin, hdrmax, compmin, compmax);
}

void print_unsigned(const char *name, unsigned long hdrmax, unsigned long compmax)
{
    printf("%-14s %14s %14lu   %14s %14lu\n", name, "-", hdrmax, "-", compmax);
}

//largest power of two that's still finite, then refined upward toward the
//true max by binary search in halving steps
float float_max(void)
{
    float f = 1, step;

    while (!isinf(f * 2))
        f *= 2;
    for (step = f; step > 0; step /= 2)
        if (!isinf(f + step))
            f += step;
    return f;
}

double double_max(void)
{
    double f = 1, step;

    while (!isinf(f * 2))
        f *= 2;
    for (step = f; step > 0; step /= 2)
        if (!isinf(f + step))
            f += step;
    return f;
}

//smallest positive value representable at all, found by halving until the
//next halving would underflow all the way to 0
float float_smallest_positive(void)
{
    float f = 1, half;

    while ((half = f / 2) != 0)
        f = half;
    return f;
}

double double_smallest_positive(void)
{
    double f = 1, half;

    while ((half = f / 2) != 0)
        f = half;
    return f;
}

*/


/*

#include <stdio.h>
#define NORMAL        0   //ordinary code
#define INSTRING      1   //between an opening and closing "
#define INCHAR        2   //between an opening and closing '
#define INCOMMENT     3   //between 
#define INLINECOMMENT 4   //between // and the end of the line
#define MAXSTACK    100   //deepest bracket nesting supported; rudimentary, per the exercise

char stack[MAXSTACK];      //open bracket characters, in nesting order
int  stackline[MAXSTACK];  //the line each one was opened on, for error messages
int  top;                  //stack[0..top-1] is in use
int  lineno;
int  errors;

void push(int c);              //prototype: lets main() call these before their definitions below
void checkclose(int c);
int  bracket_match(int open, int close);

//check a C program on stdin for unmatched (), [], {}, skipping over the//a bracket character inside any of those isn't mistaken for real program
//structure. Uses a stack rather than three independent counters, so a
//wrong-order case like "([)]" is correctly flagged rather than passing
//just because each bracket type's count happens to balance.
int main(void)
{
    int c, c2, state;

    state = NORMAL;
    lineno = 1;
    top = 0;
    errors = 0;

    while ((c = getchar()) != EOF) {
        if (c == '\n')
            ++lineno;

        if (state == NORMAL) {
            if (c == '(' || c == '[' || c == '{') {
                push(c);
            } else if (c == ')' || c == ']' || c == '}') {
                checkclose(c);
            } else if (c == '/') {
                c2 = getchar();
                if (c2 == '\n')
                    ++lineno;
                if (c2 == '*')
                    state = INCOMMENT;
                else if (c2 == '/')
                    state = INLINECOMMENT;
                else if (c2 != EOF)
                    ungetc(c2, stdin);
            } else if (c == '"') {
                state = INSTRING;
            } else if (c == '\'') {
                state = INCHAR;
            }
        } else if (state == INSTRING || state == INCHAR) {
            if (c == '\\') {                 //escape: next char is literal, skip it untouched
                if ((c2 = getchar()) == '\n')
                    ++lineno;
            } else if ((state == INSTRING && c == '"') ||
                       (state == INCHAR   && c == '\'')) {
                state = NORMAL;
            }
        } else if (state == INLINECOMMENT) {
            if (c == '\n')
                state = NORMAL;
        } else {   //INCOMMENT
            if (c == '*') {
                c2 = getchar();
                if (c2 == '\n')
                    ++lineno;
                if (c2 == '/')
                    state = NORMAL;
                else if (c2 != EOF)
                    ungetc(c2, stdin);
            }
        }
    }

    while (top > 0) {           //anything still open at EOF was never closed
        --top;
        printf("line %d: unmatched opening '%c'\n", stackline[top], stack[top]);
        ++errors;
    }

    if (errors == 0)
        printf("no bracket errors found\n");

    return 0;
}

void push(int c)
{
    if (top >= MAXSTACK) {
        printf("line %d: nesting too deep, stopped checking\n", lineno);
        ++errors;
        return;
    }
    stack[top] = c;
    stackline[top] = lineno;
    ++top;
}

int bracket_match(int open, int close)
{
    return (open == '(' && close == ')') ||
           (open == '[' && close == ']') ||
           (open == '{' && close == '}');
}

void checkclose(int c)
{
    if (top == 0) {
        printf("line %d: unmatched closing '%c'\n", lineno, c);
        ++errors;
        return;
    }
    --top;
    if (!bracket_match(stack[top], c)) {
        printf("line %d: '%c' does not match '%c' opened on line %d\n",
               lineno, c, stack[top], stackline[top]);
        ++errors;
    }
}

*/

/*
#include <stdio.h>
#define NORMAL       0   //ordinary code
#define INSTRING     1   //between an opening and closing "
#define INCHAR       2   //between an opening and closing '
#define INCOMMENT    3   //between a block comment's open and close markers
#define INLINECOMMENT 4  //between // and the end of the line

//remove all block and // comments from a C program on stdin, without
//touching the contents of string/char literals even if they contain
//comment-like text. A backslash inside a string/char literal escapes the
//next character, so an escaped quote can't be mistaken for the literal's
//closing delimiter -- this is also what stops a stray apostrophe inside a
//// comment (e.g. "K&R2's") from being misread as opening a char constant.
int main()
{
    int c, c2, state;

    state = NORMAL;
    while ((c = getchar()) != EOF) {
        if (state == NORMAL) {
            if (c == '/') {
                c2 = getchar();
                if (c2 == '*') {
                    state = INCOMMENT;
                } else if (c2 == '/') {
                    state = INLINECOMMENT;
                } else {
                    putchar(c);
                    if (c2 != EOF)
                        ungetc(c2, stdin);   //wasn't a comment start; give it back
                }
            } else if (c == '"') {
                putchar(c);
                state = INSTRING;
            } else if (c == '\'') {
                putchar(c);
                state = INCHAR;
            } else {
                putchar(c);
            }
        } else if (state == INSTRING || state == INCHAR) {
            putchar(c);
            if (c == '\\') {                 //escape: next char is literal, don't interpret it
                if ((c2 = getchar()) != EOF)
                    putchar(c2);
            } else if ((state == INSTRING && c == '"') ||
                       (state == INCHAR   && c == '\'')) {
                state = NORMAL;
            }
        } else if (state == INLINECOMMENT) {   //discard everything up to the newline
            if (c == '\n') {
                putchar(c);                    //keep the line break itself
                state = NORMAL;
            }
        } else {   
            if (c == '*') {
                if ((c2 = getchar()) == '/')
                    state = NORMAL;
                else if (c2 != EOF)
                    ungetc(c2, stdin);
            }
        }
    }

    return 0;
}
*/

/*

#include <stdio.h>
#define MAXCOL  80    //fold lines longer than this many characters
#define MAXLINE 1000  //buffer size; must be comfortably >= MAXCOL

char line[MAXLINE];   //buffered text of the current (possibly folded) line

//fold long lines after the last blank/tab before column MAXCOL. If no
//blank/tab appears before MAXCOL at all, force a break there anyway --
//otherwise one unbroken long "word" would just grow the buffer forever.
int main()
{
    int c, len, lastblank, i, rem;

    len = 0;
    lastblank = -1;
    while ((c = getchar()) != EOF) {
        if (c == '\n') {
            line[len] = '\0';
            printf("%s\n", line);
            len = 0;
            lastblank = -1;
            continue;
        }

        if (len < MAXLINE - 1)
            line[len] = c;
        if (c == ' ' || c == '\t')
            lastblank = len;
        ++len;

        if (len >= MAXCOL) {
            if (lastblank >= 0) {
                line[lastblank] = '\0';
                printf("%s\n", line);
                rem = len - (lastblank + 1);          //chars after the blank carry over
                for (i = 0; i < rem; ++i)
                    line[i] = line[lastblank + 1 + i];
                len = rem;
                lastblank = -1;                        //re-scan the carried-over remainder
                for (i = 0; i < len; ++i)
                    if (line[i] == ' ' || line[i] == '\t')
                        lastblank = i;
            } else {                                   //no blank/tab before MAXCOL: force it
                line[len] = '\0';
                printf("%s\n", line);
                len = 0;
                lastblank = -1;
            }
        }
    }
    if (len > 0) {
        line[len] = '\0';
        printf("%s\n", line);
    }

    return 0;
}
*/


/*
#include <stdio.h>

#define MAXLINE 1000   //maximum input line length

int max;                //maximum line length seen so far
char line[MAXLINE];   //current input line
char longest[MAXLINE];   //longest line saved here

int my_getline(void);   //prototype: lets main() call my_getline() before its definition below
void copy(void);   //prototype: lets main() call copy() before its definition below 


// print longest input line; specialized version of K&R2 1-16
int main()
{   
    int len;   //current line length
    extern int max;   //maximum length seen so far
    extern char longest[];   //longest line saved here

    max = 0;
    while ((len = my_getline()) > 0)
        if (len > max) {
            max = len;
            copy();
        }
    if (max > 0)   //there was a line
        printf("%s", longest);

    return 0;   

}

// my_getline: specialized version of K&R2 1-16; reads one line into line[] (up to
// MAXLINE-1 chars kept); returns the line's true length even if it's longer than
// line[] could hold, so an overlong line doesn't desync the next call
int my_getline(void)
{
    int c, i;
    extern char line[];

    i = 0;
    while ((c = getchar()) != EOF && c != '\n') {
        if (i < MAXLINE - 1)
            line[i] = c;
        ++i;
    }
    if (c == '\n') {
        if (i < MAXLINE - 1)
            line[i] = c;
        ++i;
    }
    line[(i < MAXLINE - 1) ? i : MAXLINE - 1] = '\0';
    return i;
}   

// copy : specialized version of K&R2 1-16; copies line[] into longest[]
void copy(void)
{
    int i;
    extern char line[], longest[];      

    i = 0;
    while ((longest[i] = line[i]) != '\0')
        ++i;            

}

*/



/*

#include <stdio.h>
#define MAXLINE 1000   //maximum input line length

int my_getline(char line[], int maxline);   //prototype: lets main() call my_getline() before its definition below
void reverse(char s[]);   //prototype: lets main() call reverse() before its definition below

//reverse each line of input in place, one line at a time
int main()
{
    char line[MAXLINE];
    int len;

    while ((len = my_getline(line, MAXLINE)) > 0) {
        if (len > 0 && line[len - 1] == '\n')
            line[len - 1] = '\0';   //drop the trailing newline so reverse() doesn't put it first
        reverse(line);
        printf("%s\n", line);
    }

    return 0;
}

//reads one line into s (up to lim-1 chars kept); returns the line's true
//length even if it's longer than s[] could hold
int my_getline(char s[], int lim)
{
    int c, i;

    i = 0;
    while ((c = getchar()) != EOF && c != '\n') {
        if (i < lim - 1)
            s[i] = c;
        ++i;
    }
    if (c == '\n') {
        if (i < lim - 1)
            s[i] = c;
        ++i;
    }
    s[(i < lim - 1) ? i : lim - 1] = '\0';
    return i;
}

//reverse the character string s in place
void reverse(char s[])
{
    int i, j, len;
    char c;

    len = 0;
    while (s[len] != '\0')   //find the end of the string
        ++len;

    for (i = 0, j = len - 1; i < j; ++i, --j) {
        c = s[i];
        s[i] = s[j];
        s[j] = c;
    }
}
*/


/*
#include <stdio.h>
#define MAXLINE 1000   //maximum input line length

int my_getline(char line[], int maxline);   //prototype: lets main() call my_getline() before its definition below

//remove trailing blanks and tabs from each line; drop lines that end up entirely blank
int main()
{
    char line[MAXLINE];
    int len, i;

    while ((len = my_getline(line, MAXLINE)) > 0) {
        i = 0;
        while (line[i] != '\0')   //walk to the end of what's actually stored
            ++i;
        --i;   //step onto the last real character (-1 if the line is empty)
        while (i >= 0 && (line[i] == ' ' || line[i] == '\t' || line[i] == '\n'))
            --i;
        line[i + 1] = '\0';   //cut the string off right after the last non-blank char
        if (i >= 0)   //something other than blanks/tabs/newline survived
            printf("%s\n", line);
    }

    return 0;
}

//reads one line into s (up to lim-1 chars kept); returns the line's true
//length even if it's longer than s[] could hold
int my_getline(char s[], int lim)
{
    int c, i;

    i = 0;
    while ((c = getchar()) != EOF && c != '\n') {
        if (i < lim - 1)
            s[i] = c;
        ++i;
    }
    if (c == '\n') {
        if (i < lim - 1)
            s[i] = c;
        ++i;
    }
    s[(i < lim - 1) ? i : lim - 1] = '\0';
    return i;
}
*/

/*
#include <stdio.h>
#define MAXLINE 1000   //maximum input line length

int my_getline(char line[], int maxline);   //prototype: lets main() call my_getline() before its definition below; named to avoid clashing with POSIX getline() in stdio.h
void copy(char to[], char from[]);   //prototype: lets main() call copy() before its definition below

int main()
{
    int len;   //current line length
    int max;   //maximum length seen so far
    char line[MAXLINE];   //current input line
    char longest[MAXLINE];   //longest line saved here

    max = 0;
    while ((len = my_getline(line, MAXLINE)) > 0)
        if (len > max) {
            max = len;
            copy(longest, line);
        }
    if (max > 0) {   //there was a line
        int i = 0;
        while (longest[i] != '\0')   //find how much text actually made it into the buffer
            ++i;
        printf("%d: %s", max, longest);
        if (i > 0 && longest[i - 1] != '\n')   //buffer got truncated before the real newline
            putchar('\n');
    }

    return 0;
}

int my_getline(char s[], int lim)
{
    int c, i;

    i = 0;
    while ((c = getchar()) != EOF && c != '\n') {
        if (i < lim - 1)   //keep counting past capacity, but stop storing
            s[i] = c;
        ++i;
    }
    if (c == '\n') {
        if (i < lim - 1)
            s[i] = c;
        ++i;
    }
    s[(i < lim - 1) ? i : lim - 1] = '\0';
    return i;   //true length of the line, even if longer than s[] could hold
}

void copy(char to[], char from[])
{
    int i = 0;
    while ((to[i] = from[i]) != '\0')
        ++i;
}
*/

/*
#include <stdio.h>
#define MAXLINE 1000   //maximum input line length

int my_getline(char line[], int maxline);   //prototype: lets main() call my_getline() before its definition below

//print all input lines longer than 80 characters
int main()
{
    char line[MAXLINE];
    int len;

    while ((len = my_getline(line, MAXLINE)) > 0)
        if (len > 80)
            printf("%s", line);

    return 0;
}

//reads one line into s (up to lim-1 chars kept); returns the line's true
//length even if it's longer than s[] could hold, so long lines are still
//correctly detected as > 80 chars
int my_getline(char s[], int lim)
{
    int c, i;

    i = 0;
    while ((c = getchar()) != EOF && c != '\n') {
        if (i < lim - 1)
            s[i] = c;
        ++i;
    }
    if (c == '\n') {
        if (i < lim - 1)
            s[i] = c;
        ++i;
    }
    s[(i < lim - 1) ? i : lim - 1] = '\0';
    return i;
}
*/


/*
float fahr_to_celsius(float fahr);   //prototype: lets main() call fahr_to_celsius() before its definition below

#include <stdio.h>

int main()
{
    float fahr, lower, upper, step;

    lower = 0;
    upper = 300;
    step = -20;

    for (fahr = upper; fahr >= lower; fahr = fahr + step)
        printf("%3.0f %6.1f\n", fahr, fahr_to_celsius(fahr));

    return 0;
}

float fahr_to_celsius(float fahr)
{
    return (5.0 / 9.0) * (fahr - 32.0);
}
*/



/*
#include <stdio.h>
int power(int base, int n);   //prototype: lets main() call power() before its definition below

//print base^i for i = 0..9, using both 2 and -3 as bases
int main()
{
    int i;
    for (i = 0; i < 10; ++i)
        printf("%d %d %d\n", i, power(2, i), power(-3, i));
    return 0;
}

int power(int base, int n)
{
    int p;

    for (p = 1; n > 0; --n)
        p = p * base;
    return p;
}
*/

/*
#include <stdio.h>
 // K&R2 section 1.7 - functions
 //power(base, n) raises base to the n-th power (n >= 0)


int power(int base, int n);   //prototype: lets main() call power() before its definition below

//print base^i for i = 0..9, using both 2 and -3 as bases
int main()
{
    int i;
    for (i = 0; i < 10; ++i)
        printf("%d %d %d\n", i, power(2, i), power(-3, i));
    return 0;
}

//raise base to the n-th power (n assumed >= 0); returns 1 when n == 0
int power(int base, int n)
//power(base, n)
//int base, n;
{
    int i, p;

    p = 1;
    for (i = 1; i <= n; ++i)
        p = p * base;
    return p;
}
 
*/

/*
#include <stdio.h>
#define NCHARS 128   //ASCII value range tracked

//print a horizontal histogram of character frequencies in the input
int main()
{
    int c, i;
    int freq[NCHARS];

    for (i = 0; i < NCHARS; ++i)
        freq[i] = 0;

    while ((c = getchar()) != EOF)
        if (c >= 0 && c < NCHARS)
            ++freq[c];

    for (i = 0; i < NCHARS; ++i) {
        if (freq[i] == 0)
            continue;
        if (i == '\n')
            printf("'\\n': ");
        else if (i == '\t')
            printf("'\\t': ");
        else if (i == ' ')
            printf("' ' : ");
        else if (i < ' ')
            continue;               //skip other non-printable control characters
        else
            printf("'%c' : ", i);
        for (c = 0; c < freq[i]; ++c)
            putchar('*');
        putchar('\n');
    }

    return 0;
}

*/



/*
#include <stdio.h>
#define IN  1       //inside a word
#define OUT 0       //outside a word
#define MAXLEN 20   //longest word length tracked individually; 
                    //longer words fall in the last bucket

//print a vertical histogram of word lengths in the input
int main()
{
    int c, i, row, state, len, maxcount;
    int lenhist[MAXLEN + 1];

    for (i = 0; i <= MAXLEN; ++i)
        lenhist[i] = 0;

    state = OUT;
    len = 0;
    while ((c = getchar()) != EOF) {
        if (c == ' ' || c == '\n' || c == '\t') {
            if (state == IN) {
                if (len > MAXLEN)
                    len = MAXLEN;
                ++lenhist[len];
            }
            state = OUT;
            len = 0;
        } else {
            state = IN;
            ++len;
        }
    }
    if (state == IN) {
        if (len > MAXLEN)
            len = MAXLEN;
        ++lenhist[len];
    }

    //find the tallest bar so we know how many rows to draw
    maxcount = 0;
    for (i = 1; i <= MAXLEN; ++i)
        if (lenhist[i] > maxcount)
            maxcount = lenhist[i];

    //draw from the top row down to row 1
    for (row = maxcount; row >= 1; --row) {
        for (i = 1; i <= MAXLEN; ++i)
            if (lenhist[i] >= row)
                printf("  *");
            else
                printf("   ");
        putchar('\n');
    }

    //baseline under the bars
    for (i = 1; i <= MAXLEN; ++i)
        printf("---");
    putchar('\n');

    //length labels below the baseline: tens digit row, 
    // then ones digit row
    for (i = 1; i <= MAXLEN; ++i) {
        if (i >= 10)
            printf("%3d", i / 10);
        else
            printf("   ");
    }
    putchar('\n');
    for (i = 1; i <= MAXLEN; ++i)
        printf("%3d", i % 10);
    putchar('\n');

    return 0;
}
*/



/*
#include <stdio.h>
#define IN  1       //inside a word
#define OUT 0       //outside a word
#define MAXLEN 20   //longest word length tracked individually; 
                    // longer words fall in the last bucket

//print a horizontal histogram of word lengths in the input
int main()
{
    int c, i, state, len;
    int lenhist[MAXLEN + 1];

    for (i = 0; i <= MAXLEN; ++i)
        lenhist[i] = 0;

    state = OUT;
    len = 0;
    while ((c = getchar()) != EOF) {
        if (c == ' ' || c == '\n' || c == '\t') {
            if (state == IN) {
                if (len > MAXLEN)
                    len = MAXLEN;
                ++lenhist[len];
            }
            state = OUT;
            len = 0;
        } else {
            state = IN;
            ++len;
        }
    }
    if (state == IN) {
        if (len > MAXLEN)
            len = MAXLEN;
        ++lenhist[len];
    }

    for (i = 1; i <= MAXLEN; ++i) {
        printf("%2d: ", i);
        for (c = 0; c < lenhist[i]; ++c)
            putchar('*');
        putchar('\n');
    }

    return 0;
}


*/





/*
#include <stdio.h>
int main()
{
    int c, i, nwhite, nother;
    int ndigit[10];

    nwhite = nother = 0;
    for (i = 0; i < 10; ++i)
        ndigit[i] = 0;

    while ((c = getchar()) != EOF) 
        if (c >= '0' && c <= '9')
            ++ndigit[c - '0'];
        else if (c == ' ' || c == '\n' || c == '\t')
            ++nwhite;
        else
            ++nother;
    printf("digits =");
    for (i = 0; i < 10; ++i)
        printf(" %d", ndigit[i]);
    printf(", white space = %d, other = %d\n", nwhite, nother);    
    
    return 0;
}

*/

/*
#include <stdio.h>
#define IN  1   //inside a word
#define OUT 0   //outside a word

//print input one word per line, using printf instead of putchar
int main()
{
    int c, state;

    state = OUT;
    while ((c = getchar()) != EOF) {
        if (c == ' ' || c == '\n' || c == '\t') {
            if (state == IN)
                printf("\n");
            state = OUT;
        } else {
            printf("%c", c);
            state = IN;
        }
    }
    if (state == IN)
        printf("\n");

    return 0;
}
*/


/*
#include <stdio.h>
#define IN  1   //inside a word
#define OUT 0   //outside a word

//print input one word per line
int main()
{
    int c, state;

    state = OUT;
    while ((c = getchar()) != EOF) {
        if (c == ' ' || c == '\n' || c == '\t') {
            if (state == IN)
                putchar('\n');
            state = OUT;
        } else {
            putchar(c);
            state = IN;
        }
    }
    if (state == IN)
        putchar('\n');

    return 0;
}
*/


/*
#include <stdio.h>
//wc: word count; count lines, words, and characters in input
//wc cc-c.txt magic

#define IN  1   //inside a word
#define OUT 0   //outside a word

//count lines, words, and characters in one open stream
void count(FILE *fp, long *nl, long *nw, long *nc)
{
    int c, state;

    state = OUT;
    *nl = *nw = *nc = 0;
    while ((c = getc(fp)) != EOF) {
        ++(*nc);
        if (c == '\n')
            ++(*nl);
        if (c == ' ' || c == '\n' || c == '\t')
            state = OUT;
        else if (state == OUT) {
            state = IN;
            ++(*nw);
        }
    }
}

//print one counts line, UNIX wc style; omits the name for stdin
void print_counts(long nl, long nw, long nc, char *name)
{
    if (name[0] != '\0')
        printf("%7ld %7ld %7ld %s\n", nl, nw, nc, name);
    else
        printf("%7ld %7ld %7ld\n", nl, nw, nc);
}

//behaves like UNIX wc: reads named files, or stdin if none given;
//prints a totals line when more than one file is given
int main(int argc, char *argv[])
{
    FILE *fp;
    long nl, nw, nc;
    long total_nl, total_nw, total_nc;
    int i, nfiles;

    total_nl = total_nw = total_nc = 0;
    nfiles = argc - 1;

    if (nfiles == 0) {
        count(stdin, &nl, &nw, &nc);
        print_counts(nl, nw, nc, "");
        return 0;
    }

    for (i = 1; i < argc; i++) {
        if ((fp = fopen(argv[i], "r")) == NULL) {
            fprintf(stderr, "wc: cannot open %s\n", argv[i]);
            continue;
        }
        count(fp, &nl, &nw, &nc);
        fclose(fp);
        print_counts(nl, nw, nc, argv[i]);
        total_nl += nl;
        total_nw += nw;
        total_nc += nc;
    }

    if (nfiles > 1)
        print_counts(total_nl, total_nw, total_nc, "total");

    return 0;
}
*/

/*
#include <stdio.h>
#define IN  1   //inside a word
#define OUT 0   //outside a word

//count lines, words, and characters in input

int main()
{
    int c, nl, nw, nc, state;

    state = OUT;
    nl = nw = nc = 0;
    while ((c = getchar() ) !=EOF) {
        ++nc;
        if (c == '\n')
            ++nl;
        if (c == ' ' || c == '\n' || c == '\t')
            state = OUT;
        else if (state == OUT) {
            state = IN;
            ++nw;
        }
    }
    printf("%d %d %d\n", nl, nw, nc);
   
    return 0;
}
*/


/*
#include <stdio.h>
int main()
{
    int c;
    while ((c = getchar()) != EOF) {
        if (c == '\t')
            printf("\\t");
        else if (c == '\b')
            printf("\\b");
        else if (c == '\\')
            printf("\\\\");
        else
            putchar(c);
    }
    return 0;
}

*/



/*
#include <stdio.h>
int main()
{
    int c, blank;
    blank = 0;
    while ((c = getchar()) != EOF) {
        if (c == ' ') {
            if (!blank)
                putchar(c);
            blank = 1;
        } else {
            putchar(c);
            blank = 0;
        }
    }
    return 0;
}
*/

/*
#include <stdio.h>
int main()
{
    int c, nb, nt, nl;
    nb = nt = nl = 0;
    while ((c = getchar()) != EOF) {
        if (c == ' ')
            ++nb;
        else if (c == '\t')
            ++nt;
        else if (c == '\n')
            ++nl;
    }
    printf("blanks = %d, tabs = %d, newlines = %d\n", nb, nt, nl);
    return 0;
}

*/


/*
#include <stdio.h>
int main()
{
    int c, nl;
    nl = 0;
    while ((c = getchar()) != EOF)
        if (c == '\n')
            ++nl;
    printf("%d\n", nl);
    return 0;
}
*/

/*
#include <stdio.h>
int main()
{
    double nc;  
    for(nc = 0; getchar() != EOF; ++nc)
        ;
    printf("%.0f\n", nc);
    return 0;
}
*/




/*
#include <stdio.h>
int main()
{
    long nc = 0;
    while (getchar() != EOF)
        ++nc;
    printf("%ld\n", nc);
    return 0;
}
*/

/*
#include <stdio.h>
int main()
{
    printf("%d\n", EOF);
    return 0;
}
*/

/*
#include <stdio.h>
int main()
{
    int c;
    while ((c = getchar()) != EOF)
         putchar(c);

    return 0;
}
*/


/*
#include <stdio.h>
// copy input to output; 1st version 
 int main()
 {
    int c;
    c = getchar();

    while (c != EOF) {
    putchar(c);
    c = getchar();
    }
    return 0;

 }
*/

/*
#include <stdio.h>
 #define LOWER 0 //lower limit of table 
 #define UPPER 300 // upper limit 
 #define STEP 20 // step size 

 //print Fahrenheit-Celsius table 
int main()
 {
    {int fahr;
    for (fahr = LOWER; fahr <= UPPER; fahr = fahr + STEP)
    printf("%3d %6.1f\n", fahr, (5.0/9.0)*(fahr-32));
    }
    return 0;
 } 

*/



/*
#include <stdio.h>
int main()
{
    int fathr;

    for (fathr = 300; fathr >= 0; fathr = fathr - 20) {
        printf("%3d %6.1f\n", fathr, (5.0/9.0) * (fathr-32));
    }   
    return 0;
}

*/


/*
#include <stdio.h>
int main()
 {
    float fahr, celsius;
    float lower, upper, step;
    lower = 0; // lower limit of temperatuire scale 
    upper = 300; // upper limit
    step = -20; // step size
    fahr = upper;
    while (fahr >= lower) {
        celsius = (5.0/9.0) * (fahr-32.0);
        printf("%3.0f %6.1f\n", fahr, celsius);
        fahr = fahr + step;
    //%d print as decimal integer
    //%6d print as decimal integer, at least 6 characters wide
    //%f print as floating point
    //%6f print as floating point, at least 6 characters wide
    //%.2f print as floating point, 2 characters after decimal point
    //%6.2f print as floating point, at least 6 wide and 2 after decimal point
 }
    return 0;
}
*/


/*
#include <stdio.h>

int main()
{
    printf("Hello, World!\n");
    return 0;
}
*/

/*
#include <stdio.h>
int main()
{
    if (integrity && compounding)
        go_ahead();
    else
        pass();

    return 0;
}

*/
```
