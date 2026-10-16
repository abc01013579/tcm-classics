---
title: K&R2 exercise 7-9: isupper written to save space, and to save time
date: 2026-10-16
---

```c
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <time.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c                                   # all four agree, the gotcha, sizes, timing
//              nm --size-sort -S cc-c | grep -w -e isupper_f -e _ctab   # sizes in hex: code 0x25, table 0x101
//              gcc -Wall -Wextra -O2 cc-c.c -o cc-c && ./cc-c   # optimized: the function's call disappears
//              echo '#include <ctype.h>' | gcc -E -dM -x c - | grep -w isupper   # glibc's own isupper: a macro
//              gcc -Wall -Wextra cc-c.c -o cc-c         # back to the normal build afterwards

//K&R2 exercise 7-9: isupper written to save space, and to save time.
//
//  save space:  a function, two comparisons.
//               code exists once; no table. Each call costs a jump
//               there and back, plus passing c and the result.
//  save time:   a macro that indexes a table: one memory read, one AND.
//               no call at all, and c is used once -- but the table
//               costs 257 bytes (every char value, plus EOF).
//
//Two more points the exercise leads to:
//  - a comparison MACRO, ((c) >= 'A' && (c) <= 'Z'), also has no call
//    and no table, but uses c twice: isupper_m(*p++) moves p twice.
//    The table macro uses its argument once, so it's safe there --
//    the reason real libraries chose the table.
//  - one table holds a bit per class (upper, lower, digit, space), so
//    the 257 bytes pay for isupper, islower, isdigit, isspace all at
//    once. glibc does this: its isupper is
//        ((*__ctype_b_loc())[(int)(c)] & (unsigned short int) _ISupper)
//    -- 384 unsigned shorts (-128..255), bits for every class, and the
//    pointer is per-locale, so the same macro works in any language.
//
//What -O2 changes (measured here): gcc inlines isupper_f, so it stops
//costing a call, and turns the two comparisons into one unsigned
//compare it can run on 16-32 chars at once (SIMD instructions). A
//table lookup can't be spread across chars that way, so with the
//optimizer on, the plain comparison beats the table. "Save time" in
//1988 meant "avoid the call"; today the compiler does that for you.

//--- save space: a function ------------------------------------------
//isupper_f:  1 if c is an upper case letter (ASCII), else 0
int isupper_f(int c)
{
    return c >= 'A' && c <= 'Z';
}

//--- no call, no table: a comparison macro -----------------------------
//IDIOM: parenthesize every use of a macro argument -- (c), not c --
//so isupper_m(x + 1) expands to ((x + 1) >= 'A' ...), not x + 1 >= ...
#define isupper_m(c)  ((c) >= 'A' && (c) <= 'Z')

//--- save time: a table and a macro --------------------------------------
#define U   01      //upper case
#define L   02      //lower case
#define D   04      //digit
#define S   010     //white space

//IDIOM: one slot per value from EOF (-1) to 255; (_ctab + 1) shifts the
//index by one, so _ctab[0] is EOF and c = -1 is still a legal index
unsigned char _ctab[1 + 256];

#define isupper_t(c)  ((_ctab + 1)[c] & U)
#define islower_t(c)  ((_ctab + 1)[c] & L)
#define isdigit_t(c)  ((_ctab + 1)[c] & D)
#define isspace_t(c)  ((_ctab + 1)[c] & S)

//init_ctab:  fill the table once, at startup. A real library writes
//the table out as a 257-value initializer instead, so it costs no
//time at all -- just the space in the program file.
void init_ctab(void)
{
    int c;

    for (c = 'A'; c <= 'Z'; c++)
        //IDIOM: |= sets a bit and leaves the others as they are
        (_ctab + 1)[c] |= U;
    for (c = 'a'; c <= 'z'; c++)
        (_ctab + 1)[c] |= L;
    for (c = '0'; c <= '9'; c++)
        (_ctab + 1)[c] |= D;
    for (c = '\t'; c <= '\r'; c++)  //\t \n \v \f \r are 9..13
        (_ctab + 1)[c] |= S;
    (_ctab + 1)[' '] |= S;
}

#define BUFSIZE (1 << 20)   //1 MB of test text
#define PASSES  200         //200 passes over it: about 210 million calls

unsigned char buf[BUFSIZE];

int main(void)
{
    int c, bad = 0, n, i, pass;
    long count;
    clock_t t;
    FILE *fp;

    init_ctab();

    //--- 1. all four agree on every input: EOF and 0..255 ---
    for (c = EOF; c <= 255; c++) {
        //!! turns any nonzero (the table gives 1; glibc gives 256) into 1
        int f = isupper_f(c), m = !!isupper_m(c), t = !!isupper_t(c),
            lib = !!isupper(c);
        if (f != m || f != t || f != lib) {
            printf("disagree at %d: f %d m %d t %d lib %d\n", c, f, m, t, lib);
            bad++;
        }
    }
    printf("1. function, macro, table, <ctype.h>: %s on EOF..255\n",
           bad ? "DISAGREE" : "all agree");
    printf("   the other table classes: islower_t('q') %d, isdigit_t('7') %d,"
           " isspace_t('\\n') %d, isupper_t('q') %d\n\n",
           !!islower_t('q'), !!isdigit_t('7'), !!isspace_t('\n'), !!isupper_t('q'));

    //--- 2. the comparison macro's gotcha: c used twice ---
    //"abCd" has 1 upper. Even length on purpose: each test moves p by
    //2, so an odd length would step over the '\0' and read past the end
    char word[] = "abCd";
    char *p = word;
    n = 0;
    while (*p)
        if (isupper_m(*p++))    //looks like one step per test...
            n++;
    printf("2. isupper_m(*p++) over \"abCd\": found %d upper, p moved %d chars\n",
           n, (int)(p - word));
    printf("   (each test checks one char >= 'A' and the NEXT char <= 'Z':\n"
           "    pairs a,b and C,d -- 'C' is never tested on its own)\n");
    p = word;
    n = 0;
    while (*p)
        //IDIOM: (unsigned char) before a table index -- char is signed
        //here, so a UTF-8 byte like 0xE9 would be -23: an index before
        //the table's start. <ctype.h> has the same rule: pass it an
        //unsigned char value or EOF, nothing else.
        if (isupper_t((unsigned char) *p++))    //c used once: correct
            n++;
    printf("   isupper_t(*p++) over \"abCd\": found %d upper, p moved %d chars\n\n",
           n, (int)(p - word));

    //--- 3. space ---
    printf("3. space: function -- no data, its code once (see nm below)\n"
           "          table    -- %zu bytes of data, shared by 4 classes\n"
           "          glibc    -- 384 unsigned shorts = %zu bytes, all classes\n"
           "   nm --size-sort -S cc-c | grep -w -e isupper_f -e _ctab   # sizes in hex\n\n",
           sizeof _ctab, 384 * sizeof(unsigned short));

    //--- 4. time ---
    //IDIOM: assign-in-test -- open and check for NULL in one expression
    if ((fp = fopen("zhouyi.txt", "r")) == NULL) {
        fprintf(stderr, "can't open zhouyi.txt\n");
        return 1;
    }
    n = fread(buf, 1, BUFSIZE, fp);     //264 KB of text
    fclose(fp);
    for (i = n; i < BUFSIZE; i++)       //repeat it to fill the 1 MB
        buf[i] = buf[i - n];

    printf("4. time: %d passes over 1 MB (%ld calls each)\n",
           PASSES, (long) PASSES * BUFSIZE);

    t = clock();
    count = 0;
    for (pass = 0; pass < PASSES; pass++)
        for (i = 0; i < BUFSIZE; i++)
            if (isupper_f(buf[i]))
                count++;
    printf("   function   %.3f s  (%ld upper)\n",
           (double)(clock() - t) / CLOCKS_PER_SEC, count);

    t = clock();
    count = 0;
    for (pass = 0; pass < PASSES; pass++)
        for (i = 0; i < BUFSIZE; i++)
            if (isupper_m(buf[i]))
                count++;
    printf("   cmp macro  %.3f s  (%ld upper)\n",
           (double)(clock() - t) / CLOCKS_PER_SEC, count);

    t = clock();
    count = 0;
    for (pass = 0; pass < PASSES; pass++)
        for (i = 0; i < BUFSIZE; i++)
            if (isupper_t(buf[i]))
                count++;
    printf("   table      %.3f s  (%ld upper)\n",
           (double)(clock() - t) / CLOCKS_PER_SEC, count);

    t = clock();
    count = 0;
    for (pass = 0; pass < PASSES; pass++)
        for (i = 0; i < BUFSIZE; i++)
            if (isupper(buf[i]))
                count++;
    printf("   <ctype.h>  %.3f s  (%ld upper)\n",
           (double)(clock() - t) / CLOCKS_PER_SEC, count);
    return 0;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
1. function, macro, table, <ctype.h>: all agree on EOF..255
   the other table classes: islower_t('q') 1, isdigit_t('7') 1, isspace_t('\n') 1, isupper_t('q') 0

2. isupper_m(*p++) over "abCd": found 0 upper, p moved 4 chars
   (each test checks one char >= 'A' and the NEXT char <= 'Z':
    pairs a,b and C,d -- 'C' is never tested on its own)
   isupper_t(*p++) over "abCd": found 1 upper, p moved 4 chars

3. space: function -- no data, its code once (see nm below)
          table    -- 257 bytes of data, shared by 4 classes
          glibc    -- 384 unsigned shorts = 768 bytes, all classes
   nm --size-sort -S cc-c | grep -w -e isupper_f -e _ctab   # sizes in hex

4. time: 200 passes over 1 MB (209715200 calls each)
   function   1.081 s  (4821600 upper)
   cmp macro  0.671 s  (4821600 upper)
   table      0.369 s  (4821600 upper)
   <ctype.h>  0.499 s  (4821600 upper)
win@DESKTOP-MEIH88T:~/webdev-projects$ nm --size-sort -S cc-c | grep -w -e isupper_f -e _ctab   # sizes in hex: code 0x25, table 0x101
0000000000001249 0000000000000025 T isupper_f
0000000000004040 0000000000000101 B _ctab
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra -O2 cc-c.c -o cc-c && ./cc-c
1. function, macro, table, <ctype.h>: all agree on EOF..255
   the other table classes: islower_t('q') 1, isdigit_t('7') 1, isspace_t('\n') 1, isupper_t('q') 0

2. isupper_m(*p++) over "abCd": found 0 upper, p moved 4 chars
   (each test checks one char >= 'A' and the NEXT char <= 'Z':
    pairs a,b and C,d -- 'C' is never tested on its own)
   isupper_t(*p++) over "abCd": found 1 upper, p moved 4 chars

3. space: function -- no data, its code once (see nm below)
          table    -- 257 bytes of data, shared by 4 classes
          glibc    -- 384 unsigned shorts = 768 bytes, all classes
   nm --size-sort -S cc-c | grep -w -e isupper_f -e _ctab   # sizes in hex

4. time: 200 passes over 1 MB (209715200 calls each)
   function   0.060 s  (4821600 upper)
   cmp macro  0.059 s  (4821600 upper)
   table      0.086 s  (4821600 upper)
   <ctype.h>  0.100 s  (4821600 upper)
win@DESKTOP-MEIH88T:~/webdev-projects$ echo '#include <ctype.h>' | gcc -E -dM -x c - | grep -w isupper
#define isupper(c) __isctype((c), _ISupper)
```
