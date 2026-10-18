---
title: bird-eye view
date: 2026-10-18
---

```c
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/stat.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'hello\nworld\n' | ./cc-c                        # copies stdin
//              ./cc-c < zhouyi.txt | cmp - zhouyi.txt && echo same      # Chinese text intact
//              ./cc-c time < zhouyi.txt     # 34 read() calls, counted; unbuffered needs 264390
//              ./cc-c eof < zhouyi.txt      # after EOF, more calls give EOF with no read()
//              printf 'hello\nzhouyi\n' | ./cc-c show   # look inside: buf, n, bufp on every call

//K&R2 8.2: getchar, simple buffered version -- one read() fetches a
//whole buffer, then the characters are handed out one at a time.
//Typed from the book, with these changes:
//  - "syscalls.h" is the book's own header: <unistd.h> has read,
//    <stdio.h> has BUFSIZ and EOF
//  - renamed my_getchar, since <stdio.h> already declares getchar
//  - a counter, reads, added after the read() line, so main can print
//    exactly how many system calls were made
//  - main added below
//
//The three static variables are the whole trick: static locals keep
//their values between calls, so the buffer, the position in it, and
//the count of bytes left all survive from one my_getchar to the next.
//  buf    the bytes from the last read()
//  bufp   the next byte to hand out
//  n      how many bytes are left in buf
//
//BUFSIZ is 8192: 264389 bytes / 8192 = 33 reads, plus the one that
//returns 0 = 34. (glibc's own getchar used 4096 here, so 66.)

long reads = 0;     //read() calls made by my_getchar

//getchar:  simple buffered version
int my_getchar(void)
{
    //IDIOM: static locals -- set up once, before the first call, and
    //keep their values between calls: the function's private memory
    static char buf[BUFSIZ];
    static char *bufp = buf;
    static int n = 0;

    if (n == 0) {   //buffer is empty
        //IDIOM: sizeof buf -- the array's size in bytes, so this line
        //stays right if BUFSIZ or buf's type ever changes
        n = read(0, buf, sizeof buf);
        reads++;
        bufp = buf;
    }
    //IDIOM: (--n >= 0) ? *bufp++ : EOF -- count one byte off, and if
    //there was one, hand it out and step past it. At end of file read
    //gives 0, --n makes it -1, and EOF comes back.
    return (--n >= 0) ? (unsigned char) *bufp++ : EOF;
}

#define SHOWSIZ 4   //a tiny buffer, so the refills happen often

//show_getchar:  my_getchar with a 4-byte buffer, printing what's inside
//it on every call -- buf's 4 slots, n, and where bufp points
int show_getchar(void)
{
    static char buf[SHOWSIZ];
    static char *bufp = buf;
    static int n = 0;
    int i;

    if (n == 0) {
        n = read(0, buf, sizeof buf);
        bufp = buf;
        printf("   read() -> %d bytes\n", n);
    }
    //print the state BEFORE handing out the next byte
    printf("   buf [");
    for (i = 0; i < SHOWSIZ; i++)
        if (n <= 0 || i < bufp - buf || i >= (bufp - buf) + n)
            printf("  .");          //handed out already, or not filled
        else if (buf[i] == '\n')
            printf(" \\n");
        else
            printf("  %c", buf[i]);
    //IDIOM: bufp - buf -- pointer minus pointer = how many elements
    //apart they are: here, bufp's index in buf
    printf(" ]  n = %2d  bufp = buf + %d", n, (int)(bufp - buf));
    if (n <= 0)
        printf("  -> EOF\n");
    else if (*bufp == '\n')
        printf("  -> '\\n'\n");
    else
        printf("  -> '%c'\n", *bufp);
    return (--n >= 0) ? (unsigned char) *bufp++ : EOF;
}

//ub_getchar:  the unbuffered version, from the block before, to compare
int ub_getchar(void)
{
    char c;

    return (read(0, &c, 1) == 1) ? (unsigned char) c : EOF;
}

int main(int argc, char *argv[])
{
    int c;
    long n;
    clock_t t;
    struct stat st;

    //IDIOM: argc > 1 && ... -- the && guard: read argv[1] only if it exists
    if (argc > 1 && strcmp(argv[1], "time") == 0) {
        t = clock();
        n = 0;
        while (my_getchar() != EOF)
            n++;
        printf("buffered my_getchar: %ld bytes, %ld read() calls, %.3f s\n",
               n, reads, (double)(clock() - t) / CLOCKS_PER_SEC);

        lseek(0, 0L, SEEK_SET);     //back to the start of the file
        t = clock();
        n = 0;
        while (ub_getchar() != EOF)
            n++;
        printf("unbuffered:          %ld bytes, %ld read() calls, %.3f s\n",
               n, n + 1, (double)(clock() - t) / CLOCKS_PER_SEC);

        lseek(0, 0L, SEEK_SET);
        t = clock();
        n = 0;
        while (getchar() != EOF)
            n++;
        //glibc's buffer is the file's block size (see the block before)
        fstat(0, &st);
        printf("library getchar:     %ld bytes, %ld read() calls, %.3f s\n",
               n, (n + (long) st.st_blksize - 1) / st.st_blksize + 1,
               (double)(clock() - t) / CLOCKS_PER_SEC);
    } else if (argc > 1 && strcmp(argv[1], "eof") == 0) {
        while (my_getchar() != EOF)
            ;
        printf("first EOF after %ld read() calls\n", reads);
        //n is now -1, not 0, so "if (n == 0)" never reads again: each
        //call just takes n lower and returns EOF. End of file sticks.
        printf("three more calls: %d %d %d, read() calls now %ld\n",
               my_getchar(), my_getchar(), my_getchar(), reads);
        printf("(from a terminal this means: after one Ctrl-D, the\n"
               " program never asks for input again)\n");
    } else if (argc > 1 && strcmp(argv[1], "show") == 0) {
        printf("buf has %d slots; '.' = handed out already, or not filled\n",
               SHOWSIZ);
        while (show_getchar() != EOF)
            ;
    } else
        //IDIOM: while ((c = getchar()) != EOF) -- chapter 1's copy loop
        while ((c = my_getchar()) != EOF)
            putchar(c);
    return 0;
}

/*
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/stat.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'hello\nworld\n' | ./cc-c                         # copies stdin, one read() per char
//              ./cc-c < zhouyi.txt | cmp - zhouyi.txt && echo same       # Chinese text intact
//              printf 'ab\xffcd\n' | ./cc-c | od -c                      # with the cast: all 6 bytes
//              printf 'ab\xffcd\n' | ./cc-c nocast | od -c               # without it: stops at 0xff
//              ./cc-c time < zhouyi.txt                                 # 264390 read() calls vs 66

//K&R2 8.2: getchar written with read -- unbuffered single character
//input. Typed from the book, with these changes:
//  - "syscalls.h" is the book's own header: <unistd.h> has read,
//    <stdio.h> has EOF
//  - renamed my_getchar, since <stdio.h> already declares getchar
//  - main added below, to show the cast and the cost
//
//"Unbuffered": every my_getchar call is one read() system call for one
//byte -- a trip into the kernel and back per character. The library
//getchar reads a whole buffer per trip and hands it out a byte at a
//time. The book's next version (buffered getchar) does the same thing.
//
//How big is glibc's buffer? Not BUFSIZ (8192): glibc asks the system
//for the file's block size, st_blksize, and uses that -- 4096 here.
//main gets the same number with fstat, so the count it prints is the
//real one: 264389 bytes / 4096 = 65 reads, plus the final one = 66.

//getchar:  unbuffered single character input
int my_getchar(void)
{
    char c;

    //IDIOM: (unsigned char) c before returning a char as int -- char is
    //signed here, so the byte 0xff would come back as -1, which IS EOF.
    //The cast makes every byte 0..255, so only a real end of file is -1.
    return (read(0, &c, 1) == 1) ? (unsigned char) c : EOF;
}

//nocast_getchar:  the same without the cast -- the bug the cast prevents
int nocast_getchar(void)
{
    char c;

    return (read(0, &c, 1) == 1) ? c : EOF;
}

int main(int argc, char *argv[])
{
    int c;
    long n;
    clock_t t;
    struct stat st;

    //IDIOM: argc > 1 && ... -- the && guard: read argv[1] only if it exists
    if (argc > 1 && strcmp(argv[1], "nocast") == 0) {
        //0xff arrives as -1, equal to EOF: the loop ends mid-input
        while ((c = nocast_getchar()) != EOF)
            putchar(c);
    } else if (argc > 1 && strcmp(argv[1], "time") == 0) {
        t = clock();
        n = 0;
        while (my_getchar() != EOF)
            n++;
        printf("my_getchar:  %ld bytes, %ld read() calls, %.3f s\n",
               n, n + 1, (double)(clock() - t) / CLOCKS_PER_SEC);
        //back to the start of the file, and do it again with stdio
        lseek(0, 0L, SEEK_SET);
        t = clock();
        n = 0;
        while (getchar() != EOF)
            n++;
        //fstat fills st with facts about fd 0's file, among them the
        //block size glibc chose as stdin's buffer size
        fstat(0, &st);
        //IDIOM: (n + size - 1) / size -- integer division rounded up:
        //how many size-byte chunks it takes to hold n bytes
        printf("getchar:     %ld bytes, %ld read() calls, %.3f s"
               "  (buffer %ld bytes)\n",
               n, (n + (long) st.st_blksize - 1) / st.st_blksize + 1,
               (double)(clock() - t) / CLOCKS_PER_SEC, (long) st.st_blksize);
        printf("(the +1 in each count is the final read() that returns 0)\n");
    } else
        //IDIOM: while ((c = getchar()) != EOF) -- chapter 1's copy loop,
        //now on our own getchar
        while ((c = my_getchar()) != EOF)
            putchar(c);
    return 0;
}
*/

/*
#include <stdio.h>
#include <unistd.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'hello\nworld\n' | ./cc-c                 # copies stdin to stdout
//              ./cc-c < zhouyi.txt | cmp - zhouyi.txt && echo same   # byte for byte identical
//              ./cc-c < zhouyi.txt | wc -c                      # 264389 bytes, in 33 reads of up to 8192
//              ./cc-c                                           # type lines; each comes back on Enter; Ctrl-D ends

//K&R2 8.2 Low Level I/O -- Read and Write: copy input to output with
//the system calls themselves, no stdio buffering in between.
//Typed from the book, with these fixes:
//  - "syscalls.h" is the book's own header, not a real file. On Linux
//    read and write are declared in <unistd.h>; BUFSIZ comes from <stdio.h>
//  - int main instead of plain main (modern gcc rejects implicit int)
//  - the book's block comment after main turned into a // comment
//
//  read(fd, buf, n)    asks the kernel for up to n bytes from file
//                      descriptor fd; returns how many it got, 0 at end
//                      of file, -1 on error
//  write(fd, buf, n)   hands n bytes to the kernel for fd
//  fd 0, 1, 2          stdin, stdout, stderr: open before main starts
//  BUFSIZ              8192 in glibc
//
//read returns fewer than BUFSIZ when that's all there is: from a file,
//the last piece (264389 = 32 * 8192 + 2245); from a terminal, one line
//per read, because the terminal driver hands over a line at Enter.
//
//Unix V6's kernel, ~/unix-v6/ken/sys2.c: read() and write() both call
//rdwr(), and its last line is the return value this loop tests:
//      u.u_ar0[R0] = u.u_arg[1]-u.u_count;
//bytes asked for minus bytes left over = bytes actually moved = n.

//copy input to output
int main(void)
{
    char buf[BUFSIZ];
    int n;

    //IDIOM: while ((n = read(0, buf, BUFSIZ)) > 0) -- assign-in-test:
    //read a chunk, stop at 0 (end of file) or -1 (error); write exactly
    //the n bytes that came, not BUFSIZ
    while ((n = read(0, buf, BUFSIZ)) > 0)
        write(1, buf, n);
    return 0;
}
*/

/*
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
*/

/*
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c                  # seed 1: 5 raw 32-bit outputs, then 5 random() floats
//              python3 -c 'import random; random.seed(1); [print(random.getrandbits(32)) for _ in range(5)]; [print("%.17g" % random.random()) for _ in range(5)]'
//              diff <(./cc-c 1) <(python3 -c 'import random; random.seed(1); [print(random.getrandbits(32)) for _ in range(5)]; [print("%.17g" % random.random()) for _ in range(5)]') && echo same
//              diff <(./cc-c 20261016) <(python3 -c 'import random; random.seed(20261016); [print(random.getrandbits(32)) for _ in range(5)]; [print("%.17g" % random.random()) for _ in range(5)]') && echo same
//              diff <(./cc-c 12345678901234) <(python3 -c 'import random; random.seed(12345678901234); [print(random.getrandbits(32)) for _ in range(5)]; [print("%.17g" % random.random()) for _ in range(5)]') && echo same
//              ./cc-c check            # the reference test: seed 5489, first output 3499211612

//The Mersenne Twister, MT19937 (Matsumoto and Nishimura, 1997) -- the
//generator under Python's random module, written out in C the way
//CPython's Modules/_randommodule.c has it, so this prints exactly the
//numbers Python prints for the same seed.
//
//What one random.random() call costs underneath:
//  genrand_uint32  twice -- each one reads a stored word and tempers it
//                  (4 shift/XOR lines); every 624th call it first
//                  regenerates all 624 words (the twist)
//  random_random   keeps 27 bits of one and 26 of the other: 53 bits,
//                  the full precision of a double
//
//How Python's random.seed(n) starts the state, for an int n:
//  n is cut into 32-bit words, lowest first (seed 1 -> {1}), and
//  init_by_array mixes those words into all 624 state words. So
//  random.seed(1) is NOT the same as the C reference init_genrand(1).
//
//The names (mt, mti, N, M, MATRIX_A, the tempering constants) are the
//ones in Matsumoto and Nishimura's original mt19937ar.c.

#define N 624                   //state size, in 32-bit words
#define M 397                   //the twist pairs word i with word i+M
#define MATRIX_A   0x9908b0dfU  //the twist's "multiply" step, as an XOR
#define UPPER_MASK 0x80000000U  //top bit of a word
#define LOWER_MASK 0x7fffffffU  //the other 31 bits

static uint32_t mt[N];          //the state: 624 words = 19968 bits
static int mti = N + 1;         //next word to hand out; N+1 = not seeded

void init_genrand(uint32_t s);
void init_by_array(uint32_t key[], int key_length);
uint32_t genrand_uint32(void);
double random_random(void);

int main(int argc, char *argv[])
{
    unsigned long long n = 1;
    uint32_t key[2];
    int i, keylen;

    //IDIOM: argc > 1 && ... -- the && guard: read argv[1] only if it exists
    if (argc > 1 && argv[1][0] == 'c') {
        //the published check: init_genrand(5489) then the first output.
        //5489 is also C++'s std::mt19937 default seed.
        init_genrand(5489);
        printf("init_genrand(5489), first output: %u  (should be 3499211612)\n",
               genrand_uint32());
        return 0;
    }
    if (argc > 1)
        n = strtoull(argv[1], NULL, 10);

    //cut n into 32-bit words, lowest first -- what Python does with
    //the int you pass to random.seed
    keylen = 0;
    //IDIOM: do-while -- runs once even for n == 0, giving key {0}
    do {
        key[keylen++] = (uint32_t)(n & 0xffffffffU);
        n >>= 32;
    } while (n > 0);
    init_by_array(key, keylen);

    //random.getrandbits(32): one raw output, untouched
    for (i = 0; i < 5; i++)
        printf("%u\n", genrand_uint32());
    //random.random(): two outputs made into one double in [0, 1)
    for (i = 0; i < 5; i++)
        printf("%.17g\n", random_random());
    return 0;
}

//init_genrand:  fill mt[] from one 32-bit seed
void init_genrand(uint32_t s)
{
    mt[0] = s;
    //each word from the one before: XOR its top 2 bits into it, times
    //Knuth's multiplier 1812433253, plus the index so no word repeats
    for (mti = 1; mti < N; mti++)
        mt[mti] = 1812433253U * (mt[mti-1] ^ (mt[mti-1] >> 30)) + mti;
    //uint32_t arithmetic wraps mod 2^32 -- defined for unsigned types,
    //and exactly what the original code wants
}

//init_by_array:  fill mt[] from an array of 32-bit words
void init_by_array(uint32_t key[], int key_length)
{
    int i, j, k;

    init_genrand(19650218U);    //a fixed starting state, then mix the key in
    i = 1;
    j = 0;
    k = (N > key_length ? N : key_length);
    for ( ; k; k--) {
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1664525U))
                + key[j] + j;   //non linear
        i++;
        j++;
        if (i >= N) {           //wrap around, skipping mt[0]
            mt[0] = mt[N-1];
            i = 1;
        }
        if (j >= key_length)    //reuse the key from its start
            j = 0;
    }
    for (k = N - 1; k; k--) {   //a second pass, without the key
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1566083941U))
                - i;            //non linear
        i++;
        if (i >= N) {
            mt[0] = mt[N-1];
            i = 1;
        }
    }
    mt[0] = 0x80000000U;        //MSB is 1, assuring a non-zero initial state
}

//genrand_uint32:  next 32-bit output
uint32_t genrand_uint32(void)
{
    //IDIOM: static const array as a lookup -- mag01[y & 1] picks 0 or
    //MATRIX_A from the low bit, with no if
    static const uint32_t mag01[2] = { 0x0U, MATRIX_A };
    uint32_t y;
    int kk;

    if (mti >= N) {             //all 624 words used: regenerate them
        if (mti == N + 1)       //never seeded: use the default seed
            init_genrand(5489U);
        //the twist: each new word = top bit of word kk + low 31 bits of
        //word kk+1, shifted right, XORed with word kk+M
        for (kk = 0; kk < N - M; kk++) {
            y = (mt[kk] & UPPER_MASK) | (mt[kk+1] & LOWER_MASK);
            mt[kk] = mt[kk+M] ^ (y >> 1) ^ mag01[y & 0x1U];
        }
        //IDIOM: kk+(M-N) -- the same step once kk+M runs past the end:
        //it wraps to the front, to words already regenerated
        for ( ; kk < N - 1; kk++) {
            y = (mt[kk] & UPPER_MASK) | (mt[kk+1] & LOWER_MASK);
            mt[kk] = mt[kk+(M-N)] ^ (y >> 1) ^ mag01[y & 0x1U];
        }
        y = (mt[N-1] & UPPER_MASK) | (mt[0] & LOWER_MASK);
        mt[N-1] = mt[M-1] ^ (y >> 1) ^ mag01[y & 0x1U];
        mti = 0;
    }

    y = mt[mti++];
    //tempering: spread the bits of the stored word, so outputs pass
    //statistical tests the raw state words would fail
    y ^= (y >> 11);
    y ^= (y << 7) & 0x9d2c5680U;
    y ^= (y << 15) & 0xefc60000U;
    y ^= (y >> 18);
    return y;
}

//random_random:  a double in [0, 1) with 53 random bits -- CPython's
//random.random(), line for line
double random_random(void)
{
    uint32_t a = genrand_uint32() >> 5;     //keep the top 27 bits
    uint32_t b = genrand_uint32() >> 6;     //keep the top 26 bits
    //a * 2^26 + b is a 53-bit integer; times 2^-53 puts it in [0, 1)
    return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
}
*/

/*
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <time.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c          # no seed given: rand acts as if srand(1) was called
//              ./cc-c          # run it again: exactly the same numbers
//              ./cc-c 42       # seed 42: a different sequence, the same every time
//              ./cc-c time     # seed from the clock: different on every run

//K&R2 7.8.7 Random Number Generation -- every claim in the section,
//each shown by a line of code and the printf under it:
//  1. rand() gives integers from 0 to RAND_MAX, defined in <stdlib.h>
//  2. frand() = (double) rand() / (RAND_MAX+1.0) is >= 0 and < 1
//     (and why each piece of that macro is there)
//  3. a library float generator is likely better: POSIX drand48
//  4. srand(unsigned) sets the seed
//  5. the portable rand/srand from section 2.7, run next to glibc's
//Plus one use: casting a Zhouyi hexagram with the three-coin method.

//the book's macro, as printed
#define frand() ((double) rand() / (RAND_MAX+1.0))

//section 2.7's portable version, renamed: <stdlib.h> already has rand
unsigned long int next = 1;

//kr_rand: return pseudo-random integer on 0..32767
int kr_rand(void)
{
    next = next * 1103515245 + 12345;
    return (unsigned int)(next/65536) % 32768;
}

//kr_srand: set seed for kr_rand()
void kr_srand(unsigned int seed)
{
    next = seed;
}

int coin(void);

int main(int argc, char *argv[])
{
    int i, r;
    unsigned seed = 1;

    //--- 1. rand: 0 to RAND_MAX --------------------------------------
    printf("1. RAND_MAX = %d", RAND_MAX);
    printf(RAND_MAX == INT_MAX ? "  (= INT_MAX here: glibc uses the whole int range)\n"
                               : "\n");
    printf("   the standard only promises RAND_MAX >= 32767\n");
    //no srand yet: the standard says rand then behaves as if srand(1)
    printf("   first rand() calls, no srand:");
    for (i = 0; i < 3; i++)
        printf(" %d", rand());
    printf("\n");
    srand(1);
    printf("   after srand(1):              ");
    for (i = 0; i < 3; i++)
        printf(" %d", rand());
    printf("   <- same three\n\n");

    //--- 2. frand: >= 0 and < 1 --------------------------------------
    printf("2. frand() five times:");
    for (i = 0; i < 5; i++)
        printf(" %.6f", frand());
    printf("\n");
    //why (double): without it, int / int throws away the fraction
    r = rand();
    printf("   without (double): rand() / RAND_MAX = %d / %d = %d  (int division)\n",
           r, RAND_MAX, r / RAND_MAX);
    //why RAND_MAX+1.0 and not RAND_MAX: the biggest rand() would give 1.0
    printf("   biggest rand() / RAND_MAX       = %.17f  <- 1 is NOT < 1\n",
           (double) RAND_MAX / RAND_MAX);
    printf("   biggest rand() / (RAND_MAX+1.0) = %.17f\n",
           (double) RAND_MAX / (RAND_MAX + 1.0));
    //why +1.0 and not +1: RAND_MAX+1 is int arithmetic, and here
    //RAND_MAX is INT_MAX, so +1 overflows (undefined behaviour; gcc
    //wraps it to INT_MIN). +1.0 makes it double arithmetic first.
    printf("   RAND_MAX+1.0 = %.1f;  RAND_MAX+1 as int would be INT_MAX+1: overflow\n",
           RAND_MAX + 1.0);
    //frand() * n gives a whole number 0..n-1 after (int) cuts the fraction
    printf("   a die, (int)(frand() * 6) + 1:");
    for (i = 0; i < 10; i++)
        printf(" %d", (int)(frand() * 6) + 1);
    printf("\n\n");

    //--- 3. a library float generator ---------------------------------
    //drand48 (POSIX, not ISO C) returns a double in [0, 1) directly,
    //from its own 48-bit state -- the "better statistical properties"
    //the book means: frand's double holds only rand()'s 31 bits
    srand48(1);
    printf("3. drand48() three times:");
    for (i = 0; i < 3; i++)
        printf(" %.17f", drand48());
    printf("\n\n");

    //--- 4. srand(unsigned) sets the seed ------------------------------
    //IDIOM: argc > 1 && ... -- the && guard: read argv[1] only if it exists
    if (argc > 1 && argv[1][0] == 't')
        //IDIOM: srand(time(NULL)) -- the usual seed: the clock in
        //seconds, so each run (a second apart) starts somewhere new
        seed = (unsigned) time(NULL);
    else if (argc > 1)
        seed = (unsigned) atoi(argv[1]);
    srand(seed);
    printf("4. srand(%u) first:", seed);
    for (i = 0; i < 3; i++)
        printf(" %d", rand());
    printf("\n   srand(%u) again:", seed);
    srand(seed);
    for (i = 0; i < 3; i++)
        printf(" %d", rand());
    printf("   <- same seed, same sequence\n\n");

    //--- 5. section 2.7's portable rand --------------------------------
    kr_srand(seed);
    printf("5. kr_rand() after kr_srand(%u):", seed);
    for (i = 0; i < 5; i++)
        printf(" %d", kr_rand());
    printf("\n   range 0..32767 only -- the standard's minimum RAND_MAX;\n"
           "   glibc's rand is a different, bigger generator, so its\n"
           "   numbers above don't match these even with the same seed\n\n");

    //--- a use: casting a hexagram --------------------------------------
    //three coins per line: heads 3, tails 2, so a line sums to 6..9
    //  6 old yin  -x-  (changing)    7 young yang ---
    //  8 young yin - -               9 old yang  -o-  (changing)
    //lines are cast bottom (line 1) to top, and printed top down
    srand(seed);
    int lines[6];
    for (i = 0; i < 6; i++)
        lines[i] = coin() + coin() + coin();
    printf("three-coin cast, seed %u (top line first):\n", seed);
    for (i = 5; i >= 0; i--) {
        const char *draw[] = { "-x-", "---", "- -", "-o-" };
        printf("   line %d: %d  %s\n", i + 1, lines[i], draw[lines[i] - 6]);
    }
    return 0;
}

//coin:  toss one coin with frand: heads 3, tails 2
int coin(void)
{
    //IDIOM: frand() < 0.5 -- a fair yes/no; uses the whole value
    //rather than rand() % 2, which reads only the lowest bit
    return frand() < 0.5 ? 3 : 2;
}
*/

/*
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
*/

/*
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
*/

/*
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c zhouyi.txt zhouyi.txt; echo "exit $?"          # identical, exit 0
//              ./cc-c zhouyi.txt <(sed '272s/\r$/X\r/' zhouyi.txt)   # line 272 is >1000 bytes: fgets gives its tail
//              ./cc-c zhouyi.txt <(sed '334s/吉/凶/' zhouyi.txt)      # differ at line 334
//              ./cc-c <(printf 'a\nb\nc\n') <(printf 'a\nb\n'); echo "exit $?"   # second ends first, exit 1
//              ./cc-c <(printf 'a\nb\n') <(printf 'a\nB\n')          # line 2: b vs B
//              ./cc-c zhouyi.txt nosuchfile; echo "exit $?"          # can't open, exit 2
//              ./cc-c zhouyi.txt; echo "exit $?"                     # wrong arg count, exit 2

//K&R2 exercise 7-6: compare two files, printing the first line where
//they differ. Same exit codes as the Unix cmp and diff:
//  0 same, 1 different, 2 trouble (bad args, can't open a file)
//<(...) in the run lines is bash process substitution: bash runs the
//command and hands the program a file name (/dev/fd/63) to read its
//output from, so no test files need to be made.

#define MAXLINE 1000

int main(int argc, char *argv[])
{
    FILE *fp1, *fp2;
    char line1[MAXLINE], line2[MAXLINE];
    char *r1, *r2;
    long lineno = 1;
    char *prog = argv[0];

    if (argc != 3) {
        fprintf(stderr, "usage: %s file1 file2\n", prog);
        exit(2);
    }
    //IDIOM: assign-in-test -- open and check for NULL in one expression
    if ((fp1 = fopen(argv[1], "r")) == NULL) {
        fprintf(stderr, "%s: can't open %s\n", prog, argv[1]);
        exit(2);
    }
    if ((fp2 = fopen(argv[2], "r")) == NULL) {
        fprintf(stderr, "%s: can't open %s\n", prog, argv[2]);
        exit(2);
    }

    for (;;) {
        r1 = fgets(line1, MAXLINE, fp1);
        r2 = fgets(line2, MAXLINE, fp2);
        //both ended together: no difference anywhere
        if (r1 == NULL && r2 == NULL) {
            fclose(fp1);
            fclose(fp2);
            exit(0);
        }
        //IDIOM: || guard -- if one side is NULL, strcmp is never called,
        //so it never sees a NULL pointer
        if (r1 == NULL || r2 == NULL || strcmp(line1, line2) != 0)
            break;
        //a line longer than MAXLINE comes back from fgets in pieces;
        //count a line only when its '\n' has been read
        //IDIOM: s[strlen(s)-1] -- the last char of a non-empty string
        if (line1[strlen(line1) - 1] == '\n')
            lineno++;
    }

    printf("%s and %s differ at line %ld:\n", argv[1], argv[2], lineno);
    printf("< %s", r1 ? line1 : "(end of file)\n");
    if (r1 && line1[strlen(line1) - 1] != '\n')
        putchar('\n');      //last line had no '\n', or was cut at MAXLINE
    printf("> %s", r2 ? line2 : "(end of file)\n");
    if (r2 && line2[strlen(line2) - 1] != '\n')
        putchar('\n');
    fclose(fp1);
    fclose(fp2);
    exit(1);
}
*/

/*
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'hello\n\nworld\n' | ./cc-c           # getline: lengths 6, 1, 6
//              printf 'hello\nworld' | ./cc-c             # last line has no newline: 6, then 5
//              printf 'abcdefghijkl\nxy\n' | ./cc-c 5     # fgets with n=5: 4 chars at a time
//              printf 'hi\n' | ./cc-c 1                   # n=1: room for the '\0' only
//              ./cc-c full                                # return values: fputs vs ferror

//K&R2 7.7 Line Input and Output: fgets, fputs, and getline built on fgets.
//Typed from the book, with these changes:
//  - renamed my_fgets, my_fputs, my_getline: stdio.h already declares
//    fgets, fputs and (POSIX) getline, so the book's names won't compile
//  - "register" dropped: a hint modern compilers ignore
//  - c starts at 0 in my_fgets: with n == 1 the loop never runs, and the
//    book's return line would read c before it was ever set
//  - extra parentheses in my_fputs: while ((c = *s++)) -- same code, but
//    tells gcc -Wall the = is meant, not a typo for ==
//  - main added below to show each claim in the section

#define MAXLINE 1000

char *my_fgets(char *s, int n, FILE *iop);
int my_fputs(char *s, FILE *iop);
int my_getline(char *line, int max);
void show(char *s);

int main(int argc, char *argv[])
{
    char line[MAXLINE];
    int len, n;

    if (argc == 1) {
        //claim: getline from fgets returns the length, 0 only at end of
        //input -- an empty line is "\n", length 1, so the loop keeps going
        //IDIOM: while ((len = getline(...)) > 0) -- read until 0, chapter 1's loop
        while ((len = my_getline(line, MAXLINE)) > 0) {
            printf("len %2d: ", len);
            show(line);
        }
        printf("my_getline returned 0: end of input\n");
    } else if (strcmp(argv[1], "full") == 0) {
        //claim: "different return values for ferror and fputs"
        FILE *ok = stdout;
        //IDIOM: assign-in-test -- open and check for NULL in one expression
        FILE *bad;
        if ((bad = fopen("/dev/full", "w")) == NULL) {
            fprintf(stderr, "%s: can't open /dev/full\n", argv[0]);
            exit(1);
        }
        //unbuffered, so each putc really writes and fails at once; with
        //the normal buffer the error would only show up at fclose/fflush
        setvbuf(bad, NULL, _IONBF, 0);

        int r1 = my_fputs("to stdout\n", ok);
        printf("good stream: my_fputs = %d, ferror = %d, library fputs = %d\n",
               r1, ferror(ok), fputs("", ok));
        int r2 = my_fputs("to /dev/full\n", bad);
        printf("bad stream:  my_fputs = %d, ferror = %d, EOF = %d\n",
               r2, ferror(bad), EOF);
        clearerr(bad);
        printf("bad stream:  library fputs = %d\n", fputs("again\n", bad));
        printf("so: fputs says error with EOF (negative), ok with >= 0;\n"
               "    ferror says error with nonzero, ok with 0\n");
        fclose(bad);
    } else {
        //claim: fgets reads at most n-1 chars, keeps the '\n', adds '\0'
        n = atoi(argv[1]);
        if (n < 1 || n > MAXLINE) {
            fprintf(stderr, "%s: n must be 1..%d\n", argv[0], MAXLINE);
            exit(1);
        }
        int calls = 0;
        //IDIOM: while (fgets(...) != NULL) -- NULL only when nothing was read
        while (my_fgets(line, n, stdin) != NULL) {
            printf("call %d, strlen %zu: ", ++calls, strlen(line));
            show(line);
            if (n == 1 && calls == 3) {
                printf("(n=1 reads nothing, never hits EOF -- stopping)\n");
                break;
            }
        }
    }
    return 0;
}

//show: print s in brackets, with '\n' spelled out
void show(char *s)
{
    putchar('[');
    for ( ; *s != '\0'; s++)
        if (*s == '\n')
            printf("\\n");
        else
            putchar(*s);
    printf("]\n");
}

//my_fgets:  get at most n chars from iop
char *my_fgets(char *s, int n, FILE *iop)
{
    int c = 0;
    char *cs;

    cs = s;
    //IDIOM: --n > 0 && ... -- the && guard: count first, so getc is never
    //called once the buffer is full; --n saves one slot for the '\0'
    while (--n > 0 && (c = getc(iop)) != EOF)
        //IDIOM: *cs++ = c -- store, then step the pointer, in one expression;
        //the '\n' is stored before the test, so fgets keeps it
        if ((*cs++ = c) == '\n')
            break;
    *cs = '\0';
    //NULL only if EOF came before any char: a last line with no '\n'
    //is still returned
    return (c == EOF && cs == s) ? NULL : s;
}

//my_fputs:  put string s on file iop
int my_fputs(char *s, FILE *iop)
{
    int c;

    //IDIOM: while ((c = *s++)) -- copy until the '\0', which is 0 = false
    while ((c = *s++))
        putc(c, iop);
    //IDIOM: ferror after a run of putc -- putc doesn't stop on error,
    //so ask the stream once at the end
    return ferror(iop) ? EOF : 0;
}

//my_getline:  read a line, return length
int my_getline(char *line, int max)
{
    if (my_fgets(line, max, stdin) == NULL)
        return 0;
    else
        return strlen(line);
}
*/

/*
#include <stdio.h>
#include <stdlib.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'hello\nworld\n' | ./cc-c        # no args: copies stdin
//              ./cc-c cc-c-zh.txt cc-c-zh.txt | wc -l   # two files back to back: 132
//              ./cc-c cc-c-zh.txt nosuchfile | wc -l   # error still on screen, then 66
//              ./cc-c nosuchfile 2>/dev/null; echo "exit $?"   # message hidden, exit 1
//              ./cc-c zhouyi.txt > /dev/full; echo "exit $?"   # disk full: error writing stdout, exit 2

//K&R2 7.6 Error Handling -- Stderr and Exit: cat, version 2.
//Typed from the book, with three fixes:
//  - #include <stdlib.h> added: exit is declared there
//  - int main instead of plain main (modern gcc rejects implicit int)
//  - filecopy added below: the book says it is the same as version 1
//What changed from version 1:
//  - errors go to stderr, so they show on screen even when stdout is
//    piped or redirected (version 1 printf'd them into the output)
//  - the message starts with the program's own name, argv[0]
//  - exit codes: 0 ok, 1 can't open a file, 2 can't write stdout

//cat:  concatenate files, version 2
int main(int argc, char *argv[])
{
    FILE *fp;
    void filecopy(FILE *, FILE *);
    //IDIOM: save argv[0] before the loop moves argv -- the program name
    //for error messages, whatever name it was run under (./cc-c here)
    char *prog = argv[0];

    if (argc == 1)  //no args; copy standard input
        filecopy(stdin, stdout);
    else
        while (--argc > 0)
            if ((fp = fopen(*++argv, "r")) == NULL) {
                //IDIOM: fprintf(stderr, ...) -- errors on their own stream,
                //never mixed into the real output on stdout
                fprintf(stderr, "%s: can't open %s\n",
                        prog, *argv);
                //IDIOM: exit(n) -- ends the program from anywhere, not
                //just from main; the caller sees n as $? in bash
                exit(1);
            } else {
                filecopy(fp, stdout);
                fclose(fp);
            }
    //IDIOM: check ferror(stdout) at the end -- putc doesn't stop on a
    //write error, so ask the stream once whether any write failed
    if (ferror(stdout)) {
        fprintf(stderr, "%s: error writing stdout\n", prog);
        exit(2);
    }
    exit(0);
}

//filecopy:  copy file ifp to file ofp
void filecopy(FILE *ifp, FILE *ofp)
{
    int c;  //int, not char: must hold every char value AND EOF

    while ((c = getc(ifp)) != EOF)
        putc(c, ofp);
}
*/

/*
#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'hello\nworld\n' | ./cc-c        # no args: copies stdin
//              ./cc-c cc-c-zh.txt                     # one file
//              ./cc-c cc-c-zh.txt cc-c-zh.txt | wc -l   # two files back to back: 132
//              ./cc-c cc-c-zh.txt nosuchfile zhouyi.txt; echo "exit $?"   # stops at the bad file

//K&R2 7.5 File Access: cat, version 1.
//Typed from the book, with three fixes:
//  - semicolon added after the filecopy declaration
//  - closing quote added in the printf string: "cat: can't open %s\n"
//  - int main instead of plain main (modern gcc rejects implicit int)

//cat:  concatenate files, version 1
int main(int argc, char *argv[])
{
    FILE *fp;
    //IDIOM: function declared inside the function that calls it -- legal
    //C, visible only inside main; the book does this to show filecopy is
    //a helper defined further down
    void filecopy(FILE *, FILE *);

    if (argc == 1)  //no args; copy standard input
        filecopy(stdin, stdout);
    else
        //IDIOM: while (--argc > 0) with *++argv -- skip argv[0] (the
        //program name), then step through each argument exactly once
        while (--argc > 0)
            //IDIOM: assign-in-test -- open the file and check for NULL
            //in one expression; NULL means it couldn't be opened
            if ((fp = fopen(*++argv, "r")) == NULL) {
                printf("cat: can't open %s\n", *argv);
                return 1;
            } else {
                filecopy(fp, stdout);
                fclose(fp);
            }
    return 0;
}

//filecopy:  copy file ifp to file ofp
void filecopy(FILE *ifp, FILE *ofp)
{
    int c;  //int, not char: must hold every char value AND EOF

    //IDIOM: while ((c = getc(f)) != EOF) -- the copy loop from chapter 1,
    //now with any FILE * instead of only stdin/stdout
    while ((c = getc(ifp)) != EOF)
        putc(c, ofp);
}
*/

/*
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
*/

/*
#include <stdio.h>
#include <stdarg.h>     //va_list, va_start, va_arg, va_end
#include <ctype.h>      //isspace, isdigit
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf '14/10/2026 TSM 186.5\n15/10/2026 BRK 471.25\n' | ./cc-c
//              printf '14-10-2026 TSM 186.5\n' | ./cc-c    # mismatch at '-'
//              ./cc-c < /dev/null                          # EOF right away

//K&R2 exercise 7-4: minscanf, a private scanf analogous to minprintf.
//Same trick as exercise 7-3: each %-spec is copied into a small local
//format string and handed to the real scanf with ONE argument, fetched
//with va_arg. Everything between specs is handled here, by hand:
//whitespace in fmt skips any amount of whitespace in the input, and
//any other character must match the next input character exactly.
//
//Handled: width (%19s), the l modifier, conversions d i o u x c s e f g,
//and %% for a literal percent. Not handled: %*d (assignment suppression).
//Returns the number of items assigned, or EOF if input ended first.
//
//The key difference from minprintf: every argument is a POINTER.
//scanf has to store into the caller's variables, and C passes by value,
//so the caller sends addresses. Pointers are not promoted, so here
//%f means float * and %lf means double * -- unlike printf, where a
//float has already become a double by the time it arrives.

#define LOCALFMT 100    //room for one conversion spec

int minscanf(char *fmt, ...);

int main(void)
{
    int day, month, year, n;
    char ticker[20];
    double price;

    while ((n = minscanf("%d/%d/%d %19s %lf",
                         &day, &month, &year, ticker, &price)) == 5)
        printf("%04d-%02d-%02d  %-5s %8.2f\n", year, month, day, ticker, price);
    printf("minscanf returned %d\n", n);
    return 0;
}

//minscanf: minimal scanf with variable argument list
int minscanf(char *fmt, ...)
{
    va_list ap;                         //points to each unnamed arg in turn
    char *p;
    char localfmt[LOCALFMT];
    int c, i, n;
    int islong;
    int nassigned = 0;

    va_start(ap, fmt);                  //make ap point to 1st unnamed arg
    for (p = fmt; *p; p++) {
        if (isspace(*p)) {              //whitespace: skip any amount of it
            while (isspace(c = getchar()))
                ;
            ungetc(c, stdin);           //one too far: push it back
            continue;
        }
        if (*p != '%' || *(p+1) == '%') {   //a literal: must match exactly
            if (*p == '%')
                p++;                    //"%%" matches a single '%'
            if ((c = getchar()) != *p) {
                if (c == EOF && nassigned == 0)
                    nassigned = EOF;
                ungetc(c, stdin);       //leave the mismatch for the caller
                break;
            }
            continue;
        }

        i = 0;
        localfmt[i++] = '%';
        while (isdigit(*(p+1)) && i < LOCALFMT - 4)    //width
            localfmt[i++] = *++p;
        islong = 0;
        if (*(p+1) == 'l') {
            localfmt[i++] = *++p;
            islong = 1;
        }
        localfmt[i++] = *++p;           //the conversion character
        localfmt[i] = '\0';
        if (*p == '\0')                 //fmt ended inside a spec
            break;

        //each group: conversions that store into this pointer type
        switch (*p) {
        case 'd': case 'i':
            if (islong)
                n = scanf(localfmt, va_arg(ap, long *));
            else
                n = scanf(localfmt, va_arg(ap, int *));
            break;
        case 'o': case 'u': case 'x':
            if (islong)
                n = scanf(localfmt, va_arg(ap, unsigned long *));
            else
                n = scanf(localfmt, va_arg(ap, unsigned int *));
            break;
        case 'e': case 'f': case 'g':
            if (islong)
                n = scanf(localfmt, va_arg(ap, double *));
            else
                n = scanf(localfmt, va_arg(ap, float *));
            break;
        case 'c': case 's':
            n = scanf(localfmt, va_arg(ap, char *));
            break;
        default:                        //unknown conversion: stop
            n = 0;
            break;
        }
        //scanf returns 1 if it stored the item, 0 on a mismatch, EOF if
        //input ended before anything was read
        if (n != 1) {
            if (n == EOF && nassigned == 0)
                nassigned = EOF;
            break;
        }
        nassigned++;
    }
    va_end(ap);                         //clean up when done
    return nassigned;
}
*/

/*
#include <stdio.h>
#include <stdarg.h>     //va_list, va_start, va_arg, va_end
#include <string.h>     //strchr
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 exercise 7-3: minprintf revised to handle more of printf.
//Instead of re-implementing every conversion by hand, each %-spec is
//copied into a small local format string ("%-8.3f", "%lx", ...) and
//handed to the real printf together with ONE argument, fetched with
//va_arg as the right type. minprintf's job is now just the parsing:
//which characters make up the spec, and which type the conversion eats.
//
//Handled: flags - + space # 0, width, .precision, * for width or
//precision taken from the argument list, the l (long) modifier, and
//conversions d i o x X u c s f e E g G p %.

#define LOCALFMT 100    //room for one conversion spec

void minprintf(char *fmt, ...);

int main(void)
{
    //each line: real printf first, then minprintf with the same args
    printf(    "[%d] [%5d] [%-5d] [%05d] [%+d]\n", 42, 42, 42, 42, 42);
    minprintf( "[%d] [%5d] [%-5d] [%05d] [%+d]\n", 42, 42, 42, 42, 42);
    printf(    "[%o] [%#o] [%x] [%#X] [%u]\n", 255, 255, 255, 255, 255u);
    minprintf( "[%o] [%#o] [%x] [%#X] [%u]\n", 255, 255, 255, 255, 255u);
    printf(    "[%ld] [%lx]\n", 1234567890123L, 0xdeadbeefcafeUL);
    minprintf( "[%ld] [%lx]\n", 1234567890123L, 0xdeadbeefcafeUL);
    printf(    "[%f] [%.2f] [%10.3f] [%e] [%g]\n", 3.14159, 3.14159, 3.14159, 31415.9, 0.0001);
    minprintf( "[%f] [%.2f] [%10.3f] [%e] [%g]\n", 3.14159, 3.14159, 3.14159, 31415.9, 0.0001);
    printf(    "[%c] [%s] [%10s] [%-10s] [%.3s]\n", 'A', "hello", "hello", "hello", "hello");
    minprintf( "[%c] [%s] [%10s] [%-10s] [%.3s]\n", 'A', "hello", "hello", "hello", "hello");
    printf(    "[%*d] [%-*.*f] [100%%]\n", 6, 42, 9, 2, 2.71828);
    minprintf( "[%*d] [%-*.*f] [100%%]\n", 6, 42, 9, 2, 2.71828);
    return 0;
}

//minprintf: minimal printf with variable argument list
void minprintf(char *fmt, ...)
{
    va_list ap;                         //points to each unnamed arg in turn
    char *p;
    char localfmt[LOCALFMT];
    int i;
    int islong;

    va_start(ap, fmt);                  //make ap point to 1st unnamed arg
    for (p = fmt; *p; p++) {
        if (*p != '%') {
            putchar(*p);
            continue;
        }
        i = 0;
        localfmt[i++] = '%';

        //flags, width, precision: copy them through as they are.
        //A '*' means "the next int argument", so fetch it now and
        //write its digits into localfmt in place of the '*'.
        //The bound on i leaves room for the digits of one int plus
        //the modifier, the conversion, and the '\0'
        while (*(p+1) && strchr("-+ #0123456789.*", *(p+1))
               && i < LOCALFMT - 16)
            if (*++p == '*')
                i += sprintf(localfmt + i, "%d", va_arg(ap, int));
            else
                localfmt[i++] = *p;

        islong = 0;
        if (*(p+1) == 'l') {
            localfmt[i++] = *++p;
            islong = 1;
        }
        localfmt[i++] = *++p;           //the conversion character
        localfmt[i] = '\0';

        //IDIOM: case labels stacked with no break -- several values
        //share one body. Each group is "conversions that eat this type"
        switch (*p) {
        case 'd': case 'i':
            if (islong)
                printf(localfmt, va_arg(ap, long));
            else
                printf(localfmt, va_arg(ap, int));
            break;
        case 'o': case 'x': case 'X': case 'u':
            if (islong)
                printf(localfmt, va_arg(ap, unsigned long));
            else
                printf(localfmt, va_arg(ap, unsigned int));
            break;
        case 'c':                       //a char arrives promoted to int
            printf(localfmt, va_arg(ap, int));
            break;
        case 'f': case 'e': case 'E': case 'g': case 'G':
            printf(localfmt, va_arg(ap, double));   //floats arrive as double
            break;
        case 's':
            printf(localfmt, va_arg(ap, char *));
            break;
        case 'p':
            printf(localfmt, va_arg(ap, void *));
            break;
        case '%':
            putchar('%');
            break;
        case '\0':                      //fmt ended inside a spec, e.g. "50%":
            localfmt[i-1] = '\0';       //print what was collected, and stop
            fputs(localfmt, stdout);    //before p++ steps past the '\0'
            va_end(ap);
            return;
        default:                        //unknown conversion: print it as text
            fputs(localfmt, stdout);
            break;
        }
    }
    va_end(ap);                         //clean up when done
}
*/

/*
#include <stdio.h>
#include <stdarg.h>     //va_list, va_start, va_arg, va_end
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 section 7.3: minprintf -- a minimal printf with a variable
//argument list. The "..." in the declaration means "any number of
//further arguments, of any type"; stdarg.h is how a function walks them.

void minprintf(char *fmt, ...);

int main(void)
{
    minprintf("int: %d, double: %f, string: %s, percent: %%\n",
              42, 3.14, "hello");
    minprintf("no arguments at all\n");
    minprintf("%s is %d years old\n", "K&R2", 2026 - 1988);
    return 0;
}

//minprintf: minimal printf with variable argument list
void minprintf(char *fmt, ...)
{
    va_list ap;                         //points to each unnamed arg in turn
    char *p, *sval;
    int ival;
    double dval;

    va_start(ap, fmt);                  //make ap point to 1st unnamed arg
    for (p = fmt; *p; p++) {
        if (*p != '%') {
            putchar(*p);
            continue;
        }
        switch (*++p) {
        case 'd':
            ival = va_arg(ap, int);
            printf("%d", ival);
            break;
        case 'f':
            dval = va_arg(ap, double);
            printf("%f", dval);
            break;
        case 's':
            for (sval = va_arg(ap, char *); *sval; sval++)
                putchar(*sval);
            break;
        default:
            putchar(*p);
            break;
        }
    }
    va_end(ap);                         //clean up when done
}
*/

/*
#include <stdio.h>
#include <ctype.h>      //isprint
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'tab\there, bell\a, esc\033[0m\n' | ./cc-c
//              head -c 200 /dev/urandom | ./cc-c       # raw binary
//              ./cc-c < cc-c.c                         # ordinary text

//K&R2 exercise 7-2: print arbitrary input "in a sensible way".
//Graphic characters (isprint) go through as-is; anything else except
//newline is shown as a C-style octal escape, \ooo -- octal is the Unix
//custom (od, \033 in C strings, cat -v's cousin). Lines longer than
//MAXCOL columns are broken, and an escape is never split across a break.

#define MAXCOL  80      //maximum output columns per line
#define OCTLEN  4       //width of one escape: backslash + 3 octal digits

int inc(int pos, int n);

int main(void)
{
    int c;
    int pos = 0;                        //columns used on the current line

    while ((c = getchar()) != EOF)
        if (c == '\n') {                //a real line end: keep it, reset
            putchar('\n');
            pos = 0;
        } else if (isprint(c)) {
            pos = inc(pos, 1);
            putchar(c);
        } else {
            //getchar returns an unsigned char value (0..255) as an int,
            //so it never needs more than 3 octal digits (255 = \377).
            //%03o pads with zeros: 7 -> "007", so every escape is 4 wide
            pos = inc(pos, OCTLEN);
            printf("\\%03o", c);
        }
    return 0;
}

//inc: room for n more columns? If not, break the line first.
//Returns the new column position.
int inc(int pos, int n)
{
    if (pos + n > MAXCOL) {
        putchar('\n');
        return n;
    }
    return pos + n;
}
*/

/*
#include <stdio.h>
#include <string.h>     //strstr
#include <ctype.h>      //tolower, toupper
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ln -s cc-c lower      # one-time setup: skip if the links exist
//              ln -s cc-c upper
//              echo 'Hello, World 123' | ./lower     # hello, world 123
//              echo 'Hello, World 123' | ./upper     # HELLO, WORLD 123
//              echo 'Hello' | ./cc-c                 # hello (any other name)
//              echo 'Hello' | (exec -a upper ./cc-c) # HELLO (no links needed)
//clean up:     rm lower upper

//K&R2 exercise 7-1, the SHORT version: the book's section 7.1 "lower"
//program plus the one thing the exercise adds -- a look at argv[0].
//If the name the program was invoked with contains "upper", convert to
//upper case; under any other name, to lower case.
//
//strstr searches for "upper" anywhere in argv[0], so "./upper" and
//"/home/win/webdev-projects/upper" both match without stripping the path.
//Compare the longer version archived below: exact name match, an error
//for unknown names, and a function pointer chosen once.

int main(int argc, char *argv[])
{
    int c;
    int up;

    (void) argc;                        //unused; silences -Wextra

    //IDIOM: strstr(s, t) != NULL -- "s contains t"; strstr returns a
    //pointer to the first match, or NULL if there is none.
    //The comparison itself is an int, 1 or 0, so it can be stored as a flag
    up = strstr(argv[0], "upper") != NULL;

    //IDIOM: the getchar copy loop -- c is int, not char, so EOF (-1) fits
    while ((c = getchar()) != EOF)
        //IDIOM: cond ? a : b -- pick one of two values inside an expression
        putchar(up ? toupper(c) : tolower(c));
    return 0;
}
*/

/*
#include <stdio.h>
#include <string.h>     //strrchr, strcmp
#include <ctype.h>      //tolower, toupper
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//make two names for the same program (like gunzip/zcat, or busybox):
//              ln -s cc-c lower
//              ln -s cc-c upper
//run with:     echo 'Hello, World 123' | ./lower     # hello, world 123
//              echo 'Hello, World 123' | ./upper     # HELLO, WORLD 123
//              echo 'Hello' | ./cc-c                 # error: invoked as cc-c
//              echo 'Hello' | /home/win/webdev-projects/upper   # HELLO
//no extra files instead -- bash's exec -a sets argv[0] to any name:
//              echo 'Hello' | (exec -a lower ./cc-c) # hello
//clean up:     rm lower upper

//K&R2 exercise 7-1: convert upper case to lower or lower case to upper,
//depending on the name the program is invoked with, as found in argv[0].
//
//argv[0] is whatever the shell typed to start the program, path and all:
//"./lower", "/home/win/webdev-projects/lower", or plain "lower" if found
//on $PATH. A symlink keeps ITS name in argv[0], not the target's, so one
//compiled file behaves differently under each name. To compare just the
//name, skip past the last '/'.
//
//The choice is made once, up front, by pointing a function pointer at
//tolower or toupper (section 5.11); the copy loop then just calls it.

int main(int argc, char *argv[])
{
    char *name;
    int (*conv)(int);
    int c;

    (void) argc;                        //unused; silences -Wextra

    //IDIOM: basename -- strrchr finds the LAST '/'; if there is none the
    //name is already bare, otherwise start one char past the slash
    name = strrchr(argv[0], '/');
    name = (name == NULL) ? argv[0] : name + 1;

    //IDIOM: strcmp(a, b) == 0 -- "equal"; strcmp returns 0 on a match,
    //so a bare if (strcmp(a, b)) would mean "DIFFERENT"
    if (strcmp(name, "lower") == 0)
        conv = tolower;
    else if (strcmp(name, "upper") == 0)
        conv = toupper;
    else {
        //IDIOM: errors go to stderr, exit status nonzero -- so a pipe's
        //output isn't polluted and the shell can see it failed (section 7.6)
        fprintf(stderr, "error: invoked as %s; run me as lower or upper\n",
                name);
        return 1;
    }

    //IDIOM: the getchar copy loop -- c is int, not char, so EOF (-1)
    //fits; and getchar's values (unsigned char or EOF) are exactly what
    //tolower/toupper accept, so no cast is needed here
    while ((c = getchar()) != EOF)
        //IDIOM: call through a function pointer -- conv(c) is the same as
        //(*conv)(c); non-letters come back unchanged
        putchar(conv(c));
    return 0;
}

*/
/*
#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 section 6.9: bit-fields -- the same three symbol-table flags
//(keyword? extern? static?) packed into one word, done twice:
//
//  1. MASKS: an unsigned int plus named single-bit constants, set,
//     cleared and tested with | & ~ (the section 2.9 operators)
//  2. BIT-FIELDS: a struct whose members are declared ": 1" wide, so the
//     compiler does the shifting and masking for you
//
//After each step both versions print their raw bits, so you can see they
//end up as the SAME pattern in memory. To see a bit-field's raw bits the
//struct is put in a union with a plain unsigned int (section 6.8):
//store through one member, read through the other. That is the "store as
//one type, extract as another" case -- implementation-dependent, but gcc
//documents it as working, and it is the honest way to peek.
//
//Then the rough edges of bit-fields:
//  3. a value too big for its field is silently cut to the low bits
//  4. a 1-bit SIGNED field holds only 0 and -1, never 1
//  5. unnamed fields are padding; width 0 jumps to the next word
//  6. a field has no address (shown in a comment -- it won't compile)

//IDIOM: one bit per flag -- octal powers of two, each with exactly one 1 bit
enum { KEYWORD = 01, EXTERNAL = 02, STATIC = 04 };

struct flagbits {                   //the book's struct, given a tag
    unsigned int is_keyword : 1;
    unsigned int is_extern  : 1;
    unsigned int is_static  : 1;
};

union peek {                        //two views of the same 4 bytes
    struct flagbits f;
    unsigned int raw;
};

struct small {
    unsigned int u : 3;             //0..7
    int s : 1;                      //plain int: signed on gcc, so 0 or -1
};

struct padded {
    unsigned int a : 3;
    unsigned int   : 2;             //unnamed: 2 bits of padding
    unsigned int b : 3;
};

struct split {
    unsigned int a : 3;
    unsigned int   : 0;             //width 0: start the next field in a new word
    unsigned int b : 3;
};

void printbits(unsigned int, int);

int main(void)
{
    unsigned int flags = 0;
    union peek p = { { 0, 0, 0 } };     //first member is the struct: all fields 0
    struct small sm;
    int n;

    //1. masks
    printf("--- masks ---\n");
    //IDIOM: x |= MASK -- turn the mask's bits ON, leave the rest alone
    flags |= EXTERNAL | STATIC;
    printf("flags |= EXTERNAL | STATIC     ");
    printbits(flags, 3);
    //IDIOM: x &= ~MASK -- turn the mask's bits OFF (AND with its complement)
    flags &= ~(EXTERNAL | STATIC);
    printf("flags &= ~(EXTERNAL | STATIC)  ");
    printbits(flags, 3);
    //IDIOM: (x & MASK) == 0 -- the inner parens are required: == binds
    //tighter than &, so without them it would be x & (MASK == 0)
    if ((flags & (EXTERNAL | STATIC)) == 0)
        printf("both off\n");
    flags |= KEYWORD;
    printf("flags |= KEYWORD               ");
    printbits(flags, 3);

    //2. bit-fields: the same three steps
    printf("\n--- bit-fields (sizeof(struct flagbits) = %zu) ---\n",
            sizeof(struct flagbits));
    //IDIOM: a = b = 1 -- chained assignment, right to left
    p.f.is_extern = p.f.is_static = 1;
    printf("is_extern = is_static = 1      ");
    printbits(p.raw, 3);
    p.f.is_extern = p.f.is_static = 0;
    printf("is_extern = is_static = 0      ");
    printbits(p.raw, 3);
    if (p.f.is_extern == 0 && p.f.is_static == 0)
        printf("both off\n");
    p.f.is_keyword = 1;
    printf("is_keyword = 1                 ");
    printbits(p.raw, 3);
    printf("(gcc on x86 puts the FIRST field in bit 0, so this matches the masks;\n"
           " another compiler may start from the top bit instead)\n");

    //3. too big for the field: only the low bits are kept
    printf("\n--- truncation ---\n");
    n = 9;                  //a variable, so gcc can't see the overflow and won't warn
    sm.u = n;
    printf("store 9 = 1001 in 3 bits -> %u = ", sm.u);
    printbits(sm.u, 3);
    printf("the top 1 fell off, no warning\n");

    //4. a 1-bit signed field
    printf("\n--- 1-bit signed field ---\n");
    n = 1;
    sm.s = n;
    printf("int s : 1;  s = 1  ->  s reads back %d\n", sm.s);
    //gcc -Wextra knows this too: writing  if (sm.s == 1)  here gets
    //"warning: comparison is always false due to limited range of data type"
    printf("its one bit is the sign bit, so it holds 0 or -1 -- use unsigned\n");

    //5. unnamed and zero-width fields
    printf("\n--- padding ---\n");
    printf("a:3, unnamed :2, b:3   sizeof = %zu  (8 bits used, one word)\n",
            sizeof(struct padded));
    printf("a:3, unnamed :0, b:3   sizeof = %zu  (:0 pushed b into a 2nd word)\n",
            sizeof(struct split));

    //6. no address: uncomment the next line and gcc says
    //   error: cannot take address of bit-field 'is_static'
    //unsigned int *ip = &p.f.is_static;
    return 0;
}

//printbits:  print the low n bits of x, highest first, then a newline
void printbits(unsigned int x, int n)
{
    //IDIOM: (x >> i) & 1 -- shift bit i down to position 0, then mask off the rest
    while (--n >= 0)
        putchar((x >> n) & 1 ? '1' : '0');
    putchar('\n');
}

*/
/*

#include <stdio.h>
#include <stddef.h>     //for offsetof()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 section 6.8: unions -- the book's symbol-table constant that may
//be an int, a float, or a character pointer.
//
//A union is declared exactly like a struct, but where a struct lays its
//members out one AFTER another, a union puts them all ON TOP of each
//other: every member starts at offset 0, and the union is as big as its
//widest member. It holds ONE value at a time; storing into one member
//overwrites the others.
//
//The union itself doesn't remember which member was stored last -- that
//is the programmer's job, here done by a separate int "utype" next to
//it (a "tagged union"). main shows, in order:
//
//  1. sizes and offsets: union size = largest member, all offsets 0
//  2. the book's print code, run as printed -- it has a dangling-else
//     bug: an INT or FLOAT also prints "bad type" (see bookprint)
//  3. the fixed version with an else-if chain
//  4. storing a float and reading it back as an int (the "results are
//     implementation-dependent" case the book warns about)
//  5. the book's symtab[] array: a union inside a struct inside an array
#define NSYM 3

enum { INT, FLOAT, STRING };    //the values utype can hold

union u_tag {
    int ival;
    float fval;
    char *sval;
};

struct {                        //no tag: symtab is the only variable of this type
    char *name;
    int flags;
    int utype;
    union {                     //no tag either: reached only as .u
        int ival;
        float fval;
        char *sval;
    } u;
} symtab[NSYM];

void bookprint(union u_tag, int);
void fixedprint(union u_tag, int);

int main(void)
{
    //a union may only be initialized with a value for its FIRST member,
    //so { 42 } goes into ival
    union u_tag u = { 42 };
    union u_tag v;
    int utype = INT;
    int i;

    //1. size and layout
    printf("sizeof: int %zu, float %zu, char * %zu  ->  union u_tag %zu\n",
            sizeof(int), sizeof(float), sizeof(char *), sizeof(union u_tag));
    //IDIOM: offsetof(type, member) -- byte distance from the start of a
    //struct or union to that member; for a union it is always 0
    printf("offsetof: ival %zu, fval %zu, sval %zu\n",
            offsetof(union u_tag, ival), offsetof(union u_tag, fval),
            offsetof(union u_tag, sval));
    printf("addresses: &u %p, &u.ival %p, &u.fval %p, &u.sval %p\n\n",
            (void *) &u, (void *) &u.ival, (void *) &u.fval, (void *) &u.sval);

    //2. and 3. the book's printing code vs the fixed one, one type at a time
    printf("--- u holds an int (utype = INT) ---\n");
    bookprint(u, utype);
    fixedprint(u, utype);

    u.fval = 3.14;
    utype = FLOAT;
    printf("--- u holds a float (utype = FLOAT) ---\n");
    bookprint(u, utype);
    fixedprint(u, utype);

    u.sval = "hello";
    utype = STRING;
    printf("--- u holds a string (utype = STRING) ---\n");
    bookprint(u, utype);
    fixedprint(u, utype);

    //4. store as one type, extract as another
    u.fval = 1.0;
    printf("\n--- stored u.fval = 1.0, read back u.ival ---\n");
    printf("u.ival = %d  (0x%08x): the raw IEEE-754 bits of 1.0f, not 1\n\n",
            u.ival, (unsigned) u.ival);

    //a union copies as a unit, like a struct
    v = u;
    printf("--- v = u copies the whole union: v.fval = %f ---\n\n", v.fval);

    //5. the symbol table: union inside a struct inside an array
    symtab[0].name = "MAXLINE";
    symtab[0].utype = INT;
    symtab[0].u.ival = 1000;
    symtab[1].name = "PI";
    symtab[1].utype = FLOAT;
    symtab[1].u.fval = 3.14159;
    symtab[2].name = "GREETING";
    symtab[2].utype = STRING;
    symtab[2].u.sval = "hello, world";

    printf("sizeof(symtab[0]) = %zu, sizeof(symtab[0].u) = %zu\n",
            sizeof(symtab[0]), sizeof(symtab[0].u));
    for (i = 0; i < NSYM; i++) {
        printf("symtab[%d] %-8s = ", i, symtab[i].name);
        //IDIOM: switch on the tag -- the tag says which union member is live
        switch (symtab[i].utype) {
        case INT:
            printf("%d\n", symtab[i].u.ival);
            break;
        case FLOAT:
            printf("%f\n", symtab[i].u.fval);
            break;
        case STRING:
            //IDIOM: *p and p[0] are the same thing -- both are the first char
            printf("\"%s\"  (first char: '%c' via *, '%c' via [0])\n",
                    symtab[i].u.sval, *symtab[i].u.sval, symtab[i].u.sval[0]);
            break;
        }
    }
    return 0;
}

//bookprint:  the book's code exactly as printed in 6.8
//
//The last else belongs ONLY to the nearest if (the STRING test), so for
//an INT or a FLOAT the STRING test fails and "bad type" prints as well.
//The first two ifs are separate statements, not part of the chain.
void bookprint(union u_tag u, int utype)
{
    printf("  book:  ");
    if (utype == INT)
        printf("%d\n", u.ival);
    if (utype == FLOAT)
        printf("%f\n", u.fval);
    if (utype == STRING)
        printf("%s\n", u.sval);
    else
        printf("bad type %d in utype\n", utype);
}

//fixedprint:  same tests joined into one chain, so exactly one branch runs
void fixedprint(union u_tag u, int utype)
{
    printf("  fixed: ");
    //IDIOM: if / else if / else -- a multi-way decision; the final else
    //catches "none of the above"
    if (utype == INT)
        printf("%d\n", u.ival);
    else if (utype == FLOAT)
        printf("%f\n", u.fval);
    else if (utype == STRING)
        printf("%s\n", u.sval);
    else
        printf("bad type %d in utype\n", utype);
}

*/
/*

#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace()
#include <string.h>     //for strcmp(), strlen(), strcpy()
#include <stdlib.h>     //for malloc()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'the cat and the hat\n' | ./cc-c                         # 1 and, 1 cat, 1 hat, 2 the
//         or:  ./cc-c < cc-c.c | sort -rn | head -5                           # the 5 most frequent words in this file

//K&R2 section 6.7: typedef -- the 6.5 word-count tree again, rewritten
//with the two type names the book defines on p.146-147:
//
//  typedef struct tnode *Treeptr;      Treeptr  = struct tnode *
//  typedef struct tnode { ... } Treenode;     Treenode = struct tnode
//
//The rule: a typedef reads exactly like a variable declaration. Drop
//the word typedef and "struct tnode *Treeptr;" would declare a pointer
//VARIABLE named Treeptr. With typedef in front, Treeptr becomes the
//NAME of that pointer type instead.
//
//Notice the order: Treeptr is defined FIRST, before struct tnode has
//any members. That's legal -- a pointer to a struct that isn't finished
//yet (an "incomplete type") is fine, because every struct pointer is
//the same size no matter what it points to. So inside the struct the
//children can already be written as Treeptr. The book still writes
//"struct tnode *left" there; this block uses Treeptr to show it works.
//
//Compare this block with the 6.5 one further down: the program is
//line-for-line the same, only the type names changed. typedef makes NO
//new type -- Treeptr and struct tnode * are the same type to the
//compiler, so they mix freely. main proves it before counting words:
//it assigns one to the other and compares the sizeof of each.
#define MAXWORD 100

typedef struct tnode *Treeptr;

typedef struct tnode {      //the tree node:
    char *word;             //points to the text
    int count;              //number of occurrences
    Treeptr left;           //left child
    Treeptr right;          //right child
} Treenode;

Treeptr addtree(Treeptr, char *);
void treeprint(Treeptr);
int getword(char *, int);

//word frequency count
int main(void)
{
    Treeptr root;
    char word[MAXWORD];
    struct tnode *plain;

    //same type, two spellings: no cast, no warning
    plain = NULL;
    root = plain;
    fprintf(stderr, "sizeof(Treenode) = %zu, sizeof(struct tnode) = %zu\n",
            sizeof(Treenode), sizeof(struct tnode));
    fprintf(stderr, "sizeof(Treeptr)  = %zu, sizeof(struct tnode *) = %zu\n\n",
            sizeof(Treeptr), sizeof(struct tnode *));

    //IDIOM: while ((x = get()) != EOF) -- read, test for end, loop, all in one line
    while (getword(word, MAXWORD) != EOF)
        if (isalpha(word[0]))
            //IDIOM: p = addtree(p, w) -- the recursive function returns the
            //(possibly new) subtree root, and the caller stores it back
            root = addtree(root, word);
    treeprint(root);
    return 0;
}

Treeptr talloc(void);
char *mystrdup(char *);

//addtree:  add a node with w, at or below p
Treeptr addtree(Treeptr p, char *w)
{
    int cond;

    if (p == NULL) {        //a new word has arrived
        p = talloc();       //make a new node
        p->word = mystrdup(w);
        p->count = 1;
        //IDIOM: a = b = NULL -- assignment is an expression, so it chains right to left
        p->left = p->right = NULL;
    //IDIOM: assign-in-test -- save strcmp's result AND test it, so the
    //following else-ifs reuse cond instead of calling strcmp again
    } else if ((cond = strcmp(w, p->word)) == 0)
        p->count++;         //repeated word
    else if (cond < 0)      //less than into left subtree
        p->left = addtree(p->left, w);
    else                    //greater than into right subtree
        p->right = addtree(p->right, w);
    return p;
}

//treeprint:  in-order print of tree p
void treeprint(Treeptr p)
{
    if (p != NULL) {
        treeprint(p->left);
        printf("%4d %s\n", p->count, p->word);
        treeprint(p->right);
    }
}

//talloc:  make a tnode -- the book's typedef version (p.147)
Treeptr talloc(void)
{
    //IDIOM: (T *) malloc(sizeof(T)) -- the typedef names read as plain
    //English here: "make room for one Treenode, hand back a Treeptr"
    return (Treeptr) malloc(sizeof(Treenode));
}

//mystrdup:  make a duplicate of s (the book's strdup)
char *mystrdup(char *s)
{
    char *p;

    //IDIOM: strlen(s)+1 -- strlen doesn't count the '\0', the copy needs it
    p = (char *) malloc(strlen(s)+1);
    if (p != NULL)
        strcpy(p, s);
    return p;
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
    //IDIOM: (n > 0) ? buf[--n] : getchar() -- take a pushed-back char first, else read a new one
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

*/
/*

#include <stdio.h>
#include <string.h>     //for strcmp(), strlen(), strcpy()
#include <stdlib.h>     //for malloc(), free()
#include <ctype.h>      //for isalpha(), isalnum(), isdigit()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c < some-file.c        (or type input, end with Ctrl-D)
//
//try:          ./cc-c <<'EOF'
//              #define MAXLINE 1000
//              #define IN 1    // inside a word
//              #define MSG "hello, world\n"
//              char line[MAXLINE];
//              int INDEX = 0x1IN;
//              if (state == IN) printf(MSG);
//              printf("IN stays IN in a string\n");    // and IN here too
//              EOF

//K&R2 exercise 6-6: implement a simple version of the #define processor
//(i.e., no arguments) suitable for use with C programs, based on the
//routines of this section. You may also find getch and ungetch helpful.
//
//The table half is already done: install() and lookup() from 6.6 ARE a
//#define table -- name in, replacement text out. What's new is the
//scanner around it, which reads C source on stdin and writes it to
//stdout with two changes:
//
//  1. a line  #define NAME text  is swallowed and (NAME, text) installed
//  2. every identifier that matches an installed NAME is replaced
//
//The hard part is knowing what NOT to touch. Replacing every "IN" in
//the input would be a text editor's search-and-replace; a preprocessor
//works on TOKENS, so it must step over things that only look like names:
//
//  "IN a string"      string literal      -> copied verbatim
//  'I'                char constant       -> copied verbatim
//  // IN, and the block-comment kind      -> copied verbatim
//  INDEX              a longer identifier -> not IN, read it whole
//  0x1IN              a number            -> digits+letters read whole
//
//That's why main is a dispatcher on the FIRST character of each token:
//letter/_ starts an identifier, digit starts a number, quote starts a
//literal, '/' MIGHT start a comment. Each branch reads its whole token
//before the loop looks at another character.
//
//Where getch/ungetch earn their place: a scanner often only knows a
//token has ended after reading one character too many. "IN;" -- the
//';' is what says IN is over, but ';' belongs to the next token. So
//getident reads it and ungetch()s it back. Same with '/': it takes the
//NEXT character to decide between slash-star, "//" and plain division, and if
//it was just division, that next character goes back.
//
//Simplifications vs. the real cpp: no rescanning of replacement text
//(#define A B, #define B 2 turns A into B, not 2), no line continuation
//with backslash, no #undef, and other directives (#include, #if...) are
//just passed through.
#define HASHSIZE 101
#define MAXWORD  100        //longest identifier
#define MAXDEFN 1000        //longest replacement text
#define BUFSIZE  100        //ungetch buffer

struct nlist {              //table entry:
    struct nlist *next;     //next entry in chain
    char *name;             //defined name
    char *defn;             //replacement text
};

static struct nlist *hashtab[HASHSIZE];     //pointer table, all NULL

unsigned hash(char *);
struct nlist *lookup(char *);
struct nlist *install(char *, char *);
char *mystrdup(char *);
int getident(char *, int);
void directive(void);
void copyquoted(int);
void copyslash(void);
int getch(void);
void ungetch(int);

int main(void)
{
    int c, d;
    int bol = 1;            //at beginning of line (only blanks so far)?
    char word[MAXWORD];
    struct nlist *np;

    while ((c = getch()) != EOF) {
        if (c == '#' && bol)
            directive();                //# only counts at start of line
        else if (isalpha(c) || c == '_') {
            ungetch(c);
            getident(word, MAXWORD);
            if ((np = lookup(word)) != NULL)
                fputs(np->defn, stdout);    //the substitution itself
            else
                fputs(word, stdout);
        } else if (isdigit(c)) {        //0x1F, 10L, 1e5: one token
            putchar(c);
            while (isalnum(d = getch()) || d == '_' || d == '.')
                putchar(d);
            ungetch(d);
        } else if (c == '"' || c == '\'')
            copyquoted(c);
        else if (c == '/')
            copyslash();
        else
            putchar(c);

        if (c == '\n')
            bol = 1;
        else if (c != ' ' && c != '\t')
            bol = 0;
    }
    return 0;
}

//directive:  called just after a '#' at start of line; if it's
//            #define NAME text, install it, else pass the '#' line on
void directive(void)
{
    int c, i;
    char word[MAXWORD], name[MAXWORD], defn[MAXDEFN];

    while ((c = getch()) == ' ' || c == '\t')   //"#  define" is legal
        ;
    ungetch(c);
    getident(word, MAXWORD);
    if (strcmp(word, "define") != 0) {          //#include etc.: echo it,
        printf("#%s", word);                    //main copies the rest
        return;
    }

    while ((c = getch()) == ' ' || c == '\t')
        ;
    ungetch(c);
    if (getident(name, MAXWORD) == 0) {
        fprintf(stderr, "error: #define without a name\n");
        return;
    }

    while ((c = getch()) == ' ' || c == '\t')
        ;
    //replacement text = rest of the line, but stop before a comment so
    //"#define IN 1  // inside" defines IN as "1", not "1  // inside"
    for (i = 0; c != '\n' && c != EOF && i < MAXDEFN - 1; c = getch()) {
        if (c == '/') {
            int next = getch();
            //IDIOM: two-character lookahead -- ungetch is a stack, so
            //push back in REVERSE order: next now, '/' after the loop,
            //and getch hands back '/' first, then next
            ungetch(next);
            if (next == '/' || next == '*')
                break;
        }
        defn[i++] = c;
    }
    ungetch(c);         //the '\n' or '/' is main's to copy, so the line
                        //count of the output matches the input
    while (i > 0 && (defn[i-1] == ' ' || defn[i-1] == '\t'))
        i--;            //trim trailing blanks
    defn[i] = '\0';
    install(name, defn);
}

//getident:  read an identifier (letters, digits, _) into w; return
//           its length, 0 if the next char can't start one
int getident(char *w, int lim)
{
    int c;
    char *p = w;

    c = getch();
    if (isalpha(c) || c == '_')
        for ( ; --lim > 0 && (isalnum(c) || c == '_'); c = getch())
            *p++ = c;
    ungetch(c);         //read one too many: give it back
    *p = '\0';
    return p - w;
}

//copyquoted:  copy a string or char literal opened by quote q;
//             a backslash protects the next char, so "a\"b" is one string
void copyquoted(int q)
{
    int c;

    putchar(q);
    while ((c = getch()) != EOF) {
        if (c == '\n') {        //unterminated: stop at end of line
            ungetch(c);
            return;
        }
        putchar(c);
        if (c == '\\') {
            if ((c = getch()) != EOF)
                putchar(c);
        } else if (c == q)
            return;
    }
}

//copyslash:  called after a '/'; copy a comment through untouched, or
//            if it was just a division sign, give the lookahead back
void copyslash(void)
{
    int c, prev;

    c = getch();
    if (c == '/') {                     //line comment: up to the '\n'
        putchar('/');
        putchar('/');
        while ((c = getch()) != '\n' && c != EOF)
            putchar(c);
        ungetch(c);
    } else if (c == '*') {              //block comment: up to star-slash
        putchar('/');
        putchar('*');
        for (prev = 0; (c = getch()) != EOF; prev = c) {
            putchar(c);
            if (prev == '*' && c == '/')
                return;
        }
    } else {                            //plain division
        putchar('/');
        ungetch(c);
    }
}

//hash:  form hash value for string s
unsigned hash(char *s)
{
    unsigned hashval;

    for (hashval = 0; *s != '\0'; s++)
        hashval = *s + 31 * hashval;
    return hashval % HASHSIZE;
}

//lookup:  look for s in hashtab
struct nlist *lookup(char *s)
{
    struct nlist *np;

    for (np = hashtab[hash(s)]; np != NULL; np = np->next)
        if (strcmp(s, np->name) == 0)
            return np;      //found
    return NULL;            //not found
}

//install:  put (name, defn) in hashtab
struct nlist *install(char *name, char *defn)
{
    struct nlist *np;
    unsigned hashval;

    if ((np = lookup(name)) == NULL) {      //not found
        np = (struct nlist *) malloc(sizeof(*np));
        if (np == NULL || (np->name = mystrdup(name)) == NULL)
            return NULL;
        hashval = hash(name);
        np->next = hashtab[hashval];
        hashtab[hashval] = np;
    } else                                  //already there
        free((void *) np->defn);            //free previous defn
    if ((np->defn = mystrdup(defn)) == NULL)
        return NULL;
    return np;
}

//mystrdup:  make a duplicate of s (the book's strdup)
char *mystrdup(char *s)
{
    char *p;

    p = (char *) malloc(strlen(s) + 1);     //+1 for '\0'
    if (p != NULL)
        strcpy(p, s);
    return p;
}

int buf[BUFSIZE];       //int, not char: EOF can be pushed back (ex 4-9)
int bufp = 0;           //next free position in buf

int getch(void)         //get a (possibly pushed back) character
{
    return (bufp > 0) ? buf[--bufp] : getchar();
}

void ungetch(int c)     //push character back on input
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters\n");
    else
        buf[bufp++] = c;
}

*/
/*

#include <stdio.h>
#include <string.h>     //for strcmp(), strlen(), strcpy()
#include <stdlib.h>     //for malloc(), free()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 exercise 6-5: write a function undef that will remove a name and
//definition from the table maintained by lookup and install.
//
//Removing a node from a chain means: whatever points AT the node must be
//made to point PAST it, to node->next. The trouble is that "whatever
//points at it" is one of two different things:
//
//  - the node is first in its chain:   hashtab[h] points at it
//  - the node is further along:        the previous node's next does
//
//                 hashtab[18]          Hm's next
//                     |                    |
//                     v                    v
//  hashtab[18] --> {Hm, next} ----------> {IN, next} --> NULL
//
//The usual answer is to remember the previous node while walking, and
//write if (prev == NULL) hashtab[h] = ...; else prev->next = ...;
//
//undef below uses a pointer to a POINTER instead: pp holds the address
//of the arrow itself -- first &hashtab[h], then &node->next for each
//node. Both are just "a struct nlist * stored somewhere", so one
//statement, *pp = np->next, unlinks the first node and a middle node
//alike. No prev, no special case.
//
//main installs IN and Hm (both in chain 18, Hm at the head) and OUT,
//then removes a middle node, a head node, and a name that isn't there.
#define HASHSIZE 101

struct nlist {              //table entry:
    struct nlist *next;     //next entry in chain
    char *name;             //defined name
    char *defn;             //replacement text
};

static struct nlist *hashtab[HASHSIZE];     //pointer table, all NULL

unsigned hash(char *);
struct nlist *lookup(char *);
struct nlist *install(char *, char *);
int undef(char *);
char *mystrdup(char *);
void dump(void);

int main(void)
{
    install("IN", "1");
    install("OUT", "0");
    install("Hm", "oops");          //same chain as IN, goes in front of it
    dump();

    printf("\nundef(\"IN\")  = %d   (middle of chain 18)\n", undef("IN"));
    dump();

    printf("\nundef(\"Hm\")  = %d   (head of chain 18)\n", undef("Hm"));
    dump();

    printf("\nundef(\"EOF\") = %d   (never installed)\n", undef("EOF"));
    printf("lookup(\"IN\") = %s\n", lookup("IN") == NULL ? "NULL" : "found");
    return 0;
}

//undef:  remove name and its definition from hashtab;
//        return 1 if it was there, 0 if not
int undef(char *name)
{
    struct nlist **pp;      //address of the pointer that points at a node
    struct nlist *np;

    //IDIOM: pointer to pointer for list removal -- pp starts at the
    //address of the chain's head, then moves to the address of each
    //node's next; *pp is always "the arrow pointing at the current node"
    for (pp = &hashtab[hash(name)]; *pp != NULL; pp = &(*pp)->next)
        if (strcmp(name, (*pp)->name) == 0) {
            np = *pp;
            *pp = np->next;     //the arrow now skips np: np is unlinked
            //IDIOM: free in reverse of allocation -- the strings first,
            //while np still exists to reach them, then np itself
            free(np->name);
            free(np->defn);
            free(np);
            return 1;
        }
    return 0;
}

//hash:  form hash value for string s
unsigned hash(char *s)
{
    unsigned hashval;

    for (hashval = 0; *s != '\0'; s++)
        hashval = *s + 31 * hashval;
    return hashval % HASHSIZE;
}

//lookup:  look for s in hashtab
struct nlist *lookup(char *s)
{
    struct nlist *np;

    for (np = hashtab[hash(s)]; np != NULL; np = np->next)
        if (strcmp(s, np->name) == 0)
            return np;      //found
    return NULL;            //not found
}

//install:  put (name, defn) in hashtab
struct nlist *install(char *name, char *defn)
{
    struct nlist *np;
    unsigned hashval;

    if ((np = lookup(name)) == NULL) {      //not found
        np = (struct nlist *) malloc(sizeof(*np));
        if (np == NULL || (np->name = mystrdup(name)) == NULL)
            return NULL;
        hashval = hash(name);
        np->next = hashtab[hashval];        //new entry points at old head
        hashtab[hashval] = np;              //and becomes the new head
    } else                                  //already there
        free((void *) np->defn);            //free previous defn
    if ((np->defn = mystrdup(defn)) == NULL)
        return NULL;
    return np;
}

//mystrdup:  make a duplicate of s (the book's strdup)
char *mystrdup(char *s)
{
    char *p;

    p = (char *) malloc(strlen(s) + 1);     //+1 for '\0'
    if (p != NULL)
        strcpy(p, s);
    return p;
}

//dump:  print every non-empty chain, head first
void dump(void)
{
    int i;
    struct nlist *np;

    for (i = 0; i < HASHSIZE; i++)
        if (hashtab[i] != NULL) {
            printf("[%3d]", i);
            for (np = hashtab[i]; np != NULL; np = np->next)
                printf(" --> %s=%s", np->name, np->defn);
            printf(" --> NULL\n");
        }
}

*/
/*

#include <stdio.h>
#include <string.h>     //for strcmp(), strlen(), strcpy()
#include <stdlib.h>     //for malloc(), free()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 6.6 Table Lookup: the symbol table of a #define processor.
//
//install(name, defn)  remember that name stands for defn
//lookup(s)            find s's entry, or NULL
//
//hashtab is an array of 101 POINTERS, each the head of a linked list
//("chain"). hash(s) picks the chain; strcmp picks the entry within it.
//
//  hashtab
//   [0]  NULL
//   ...
//   [18] --> {next, "Hm", "oops"} --> {next, "IN", "1"} --> NULL
//   ...
//
//main installs a few names and prints every non-empty chain, to show:
//  - "IN" and "Hm" hash to the same slot (31*73+78 == 31*72+109 == 2341,
//    and 2341 % 101 == 18), so they share chain 18
//  - new entries go at the HEAD of a chain, so "Hm" comes before "IN"
//  - installing "IN" again replaces its defn; no new entry is made
//
//The book's strdup is called mystrdup here: <string.h> already declares
//a strdup of its own, and a second definition would clash with it.
#define HASHSIZE 101

struct nlist {              //table entry:
    struct nlist *next;     //next entry in chain
    char *name;             //defined name
    char *defn;             //replacement text
};

static struct nlist *hashtab[HASHSIZE];     //pointer table, all NULL

unsigned hash(char *);
struct nlist *lookup(char *);
struct nlist *install(char *, char *);
char *mystrdup(char *);
void dump(void);

int main(void)
{
    struct nlist *np;

    install("IN", "1");
    install("OUT", "0");
    install("MAXLINE", "1000");
    install("Hm", "oops");          //collides with "IN"
    printf("hash(\"IN\") = %u   hash(\"Hm\") = %u\n\n", hash("IN"), hash("Hm"));
    dump();

    install("IN", "2");             //redefine: same entry, new defn
    printf("\nafter install(\"IN\", \"2\"):\n");
    dump();

    printf("\n");
    if ((np = lookup("MAXLINE")) != NULL)
        printf("lookup(\"MAXLINE\") -> %s\n", np->defn);
    if ((np = lookup("EOF")) == NULL)
        printf("lookup(\"EOF\")     -> NULL (never installed)\n");
    return 0;
}

//hash:  form hash value for string s
unsigned hash(char *s)
{
    unsigned hashval;

    //IDIOM: walk a string by moving the pointer itself -- s++ steps to
    //the next char, *s != '\0' stops at the terminator; no index needed
    for (hashval = 0; *s != '\0'; s++)
        hashval = *s + 31 * hashval;
    return hashval % HASHSIZE;
}

//lookup:  look for s in hashtab
struct nlist *lookup(char *s)
{
    struct nlist *np;

    //IDIOM: walk a linked list -- for (p = head; p != NULL; p = p->next)
    //is the list version of for (i = 0; i < n; i++)
    for (np = hashtab[hash(s)]; np != NULL; np = np->next)
        if (strcmp(s, np->name) == 0)
            return np;      //found
    return NULL;            //not found
}

//install:  put (name, defn) in hashtab
struct nlist *install(char *name, char *defn)
{
    struct nlist *np;
    unsigned hashval;

    //IDIOM: assign and test in one go, like while ((c = getchar()) != EOF);
    //the inner parens matter: = binds more loosely than ==
    if ((np = lookup(name)) == NULL) {      //not found
        //IDIOM: sizeof(*np) -- the size of whatever np points to; sizeof
        //never evaluates *np, so using the not-yet-set np is safe
        np = (struct nlist *) malloc(sizeof(*np));
        //IDIOM: guard with || -- the right side only runs if np != NULL,
        //so np->name is never touched through a null pointer
        if (np == NULL || (np->name = mystrdup(name)) == NULL)
            return NULL;
        hashval = hash(name);
        //IDIOM: insert at the head of a list -- link to the old head
        //FIRST, then make the new node the head; swap them and the
        //rest of the chain is lost
        np->next = hashtab[hashval];        //new entry points at old head
        hashtab[hashval] = np;              //and becomes the new head
    } else                                  //already there
        free((void *) np->defn);            //free previous defn
    if ((np->defn = mystrdup(defn)) == NULL)
        return NULL;
    return np;
}

//mystrdup:  make a duplicate of s (the book's strdup)
char *mystrdup(char *s)
{
    char *p;

    //IDIOM: malloc(strlen(s) + 1) -- strlen doesn't count the '\0',
    //so a string copy always needs one byte more than its length
    p = (char *) malloc(strlen(s) + 1);     //+1 for '\0'
    if (p != NULL)
        strcpy(p, s);
    return p;
}

//dump:  print every non-empty chain, head first
void dump(void)
{
    int i;
    struct nlist *np;

    for (i = 0; i < HASHSIZE; i++)
        if (hashtab[i] != NULL) {
            printf("[%3d]", i);
            for (np = hashtab[i]; np != NULL; np = np->next)
                printf(" --> %s=%s", np->name, np->defn);
            printf(" --> NULL\n");
        }
}

*/
/*

#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace(), tolower()
#include <string.h>     //for strcmp(), strlen(), strcpy()
#include <stdlib.h>     //for malloc(), qsort()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'the cat and the hat and the bat\n' | ./cc-c          # 3 the | 2 and | 1 bat | 1 cat | 1 hat
//         or:  ./cc-c < cc-c.c | head -10                                 # the 10 most frequent words in this file

//K&R2 exercise 6-4: write a program that prints the distinct words in
//its input sorted into decreasing order of frequency of occurrence.
//Precede each word by its count.
//
//Two stages:
//
//1. COUNT -- exactly 6.5: a binary tree of words, each with a count.
//   The tree is sorted by WORD, which is what makes finding a word fast.
//
//2. RE-SORT BY COUNT -- the tree can't give that order, so:
//     treecount  counts the nodes, n
//     malloc     gets an array of n POINTERS to nodes
//     fill       walks the tree in order, storing each node's address
//     qsort      sorts the pointers by count (the nodes don't move)
//
//         tree (by word)                 nodes[] after qsort (by count)
//              the 3                     [0] --> the 3
//             /     \                    [1] --> and 2
//          cat 1    ...                  [2] --> bat 1
//         /                              [3] --> cat 1
//      and 2  ...                        [4] --> hat 1
//
//qsort is the standard library's sort (K&R 5.11 wrote its own; this is
//the real one from <stdlib.h>). It can sort an array of anything, so it
//needs to be told how to compare two elements: you pass it a FUNCTION,
//bycount, and qsort calls it as often as it needs.
//
//qsort hands bycount two "const void *": pointers to elements of unknown
//type. Here each element is itself a pointer (struct tnode *), so each
//argument is really a pointer to a pointer, struct tnode **. bycount
//casts it back and follows it once to get the node.
//
//Equal counts are put in alphabetical order, so the output is the same
//on every system (qsort alone may order equal elements any way it likes).
//Words are lowercased first, so "The" and "the" are counted together.
#define MAXWORD 100

struct tnode {
    char *word;
    int count;
    struct tnode *left;
    struct tnode *right;
};

struct tnode *addtree(struct tnode *, char *);
int treecount(struct tnode *);
struct tnode **fill(struct tnode *, struct tnode **);
int bycount(const void *, const void *);
int getword(char *, int);

//print words by decreasing frequency, each preceded by its count
int main(void)
{
    struct tnode *root = NULL;
    struct tnode **nodes;   //array of pointers to the tree's nodes
    char word[MAXWORD];
    char *p;
    int n, i;

    //MAXWORD - 1: K&R's getword stores up to lim chars PLUS '\0', so a
    //100-letter word with lim = MAXWORD would write '\0' to word[100]
    while (getword(word, MAXWORD - 1) != EOF)
        if (isalpha(word[0])) {
            for (p = word; *p != '\0'; p++)
                *p = tolower(*p);
            root = addtree(root, word);
        }

    if ((n = treecount(root)) == 0)
        return 0;
    nodes = (struct tnode **) malloc(n * sizeof(struct tnode *));
    if (nodes == NULL) {
        printf("cc-c: out of memory\n");
        return 1;
    }
    fill(root, nodes);
    qsort(nodes, n, sizeof(struct tnode *), bycount);
    for (i = 0; i < n; i++)
        printf("%4d %s\n", nodes[i]->count, nodes[i]->word);
    return 0;
}

//treecount:  number of nodes in tree p
int treecount(struct tnode *p)
{
    if (p == NULL)
        return 0;
    return treecount(p->left) + 1 + treecount(p->right);
}

//fill:  store the address of every node of p, in order, starting at a;
//       return the next free slot
struct tnode **fill(struct tnode *p, struct tnode **a)
{
    if (p != NULL) {
        a = fill(p->left, a);
        *a++ = p;
        a = fill(p->right, a);
    }
    return a;
}

//bycount:  qsort's comparison -- higher count first; equal counts in
//          alphabetical order
int bycount(const void *a, const void *b)
{
    struct tnode *p = *(struct tnode * const *) a;
    struct tnode *q = *(struct tnode * const *) b;

    if (p->count != q->count)
        return q->count - p->count;     //bigger count sorts earlier
    return strcmp(p->word, q->word);
}

struct tnode *talloc(void);
char *mystrdup(char *);

//addtree:  add a node with w, at or below p (6.5)
struct tnode *addtree(struct tnode *p, char *w)
{
    int cond;

    if (p == NULL) {
        p = talloc();
        p->word = mystrdup(w);
        p->count = 1;
        p->left = p->right = NULL;
    } else if ((cond = strcmp(w, p->word)) == 0)
        p->count++;
    else if (cond < 0)
        p->left = addtree(p->left, w);
    else
        p->right = addtree(p->right, w);
    return p;
}

//talloc:  make a tnode
struct tnode *talloc(void)
{
    return (struct tnode *) malloc(sizeof(struct tnode));
}

//mystrdup:  make a duplicate of s (the book's strdup)
char *mystrdup(char *s)
{
    char *p;

    p = (char *) malloc(strlen(s)+1);   //+1 for '\0'
    if (p != NULL)
        strcpy(p, s);
    return p;
}

int getch(void);
void ungetch(int);

//getword:  get next word or character from input (6.3)
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

int buf[BUFSIZE];       //buffer for ungetch -- int, so it can hold EOF
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

*/
/*

#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace(), tolower()
#include <string.h>     //for strcmp(), strlen(), strcpy()
#include <stdlib.h>     //for malloc()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'The cat sat\non the mat.\nThe cat ran, and the dog sat.\n' | ./cc-c     # cat 1 3 | dog 3 | mat 2 | ran 3 | sat 1 3
//         or:  ./cc-c < cc-c.c | grep '^lnum '                                         # every line of cc-c.c that mentions lnum

//K&R2 exercise 6-3: write a cross-referencer that prints a list of all
//words in a document, and for each word, a list of the line numbers on
//which it occurs. Remove noise words like "the," "and," and so on.
//
//Same shape as 6.5's word counter -- a binary tree of words, printed in
//order -- but each node now holds a LIST of line numbers instead of a
//count. That list is a LINKED LIST, a second self-referential struct:
//
//  struct lnode {
//      int lnum;               a line number
//      struct lnode *next;     the next one, or NULL at the end
//  };
//
//  "cat" on lines 1 and 3:   tnode "cat" --> [1] --> [3] --> NULL
//
//A tree node keeps a pointer to the first lnode (lines, where printing
//starts) and to the last (last, where the next number is added), so
//adding a number never has to walk the whole list. A word that appears
//twice on one line gets that line once: a new number is added only if
//it differs from the last one.
//
//COUNTING LINES. The book's getword skips newlines as whitespace, so the
//program would never see a line end. Here getword skips blanks and tabs
//but returns '\n' as a word of its own; main counts those.
//
//NOISE WORDS. noise[] is a sorted array of pointers to strings (as in
//5.6-5.8) and isnoise() binary-searches it, like 6.3's keytab. Words are
//lowercased first, so "The" and "the" are one word and both are noise.
//"s" and "t" are in the list because getword splits "don't" into don
//and t (an apostrophe isn't a letter).
#define MAXWORD 100

struct lnode {              //one line number in a word's list
    int lnum;
    struct lnode *next;
};

struct tnode {              //one word
    char *word;
    struct lnode *lines;    //first line number
    struct lnode *last;     //last line number, where new ones go
    struct tnode *left;
    struct tnode *right;
};

char *noise[] = {           //must stay in alphabetical order
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for",
    "from", "had", "has", "have", "he", "her", "his", "i", "if", "in",
    "is", "it", "its", "me", "my", "not", "of", "on", "or", "s",
    "she", "so", "t", "that", "the", "their", "them", "then", "there",
    "they", "this", "to", "was", "we", "were", "which", "with", "you"
};

#define NNOISE (sizeof noise / sizeof noise[0])

struct tnode *addtree(struct tnode *, char *, int);
void treeprint(struct tnode *);
int isnoise(char *);
int getword(char *, int);

//cross-reference: each word with the lines it's on
int main(void)
{
    struct tnode *root = NULL;
    char word[MAXWORD];
    char *p;
    int lnum = 1;
    int c;

    while ((c = getword(word, MAXWORD)) != EOF)
        if (c == '\n')
            lnum++;
        else if (isalpha(word[0])) {
            for (p = word; *p != '\0'; p++)
                *p = tolower(*p);
            if (!isnoise(word))
                root = addtree(root, word, lnum);
        }
    treeprint(root);
    return 0;
}

//isnoise:  1 if w is in noise[], by binary search
int isnoise(char *w)
{
    int cond;
    int low, high, mid;

    low = 0;
    high = NNOISE - 1;
    while (low <= high) {
        mid = (low+high) / 2;
        if ((cond = strcmp(w, noise[mid])) < 0)
            high = mid - 1;
        else if (cond > 0)
            low = mid + 1;
        else
            return 1;
    }
    return 0;
}

struct tnode *talloc(void);
struct lnode *lalloc(int);
char *mystrdup(char *);

//addtree:  add w, seen on line lnum, at or below p
struct tnode *addtree(struct tnode *p, char *w, int lnum)
{
    int cond;

    if (p == NULL) {                    //a new word: node + first line number
        p = talloc();
        p->word = mystrdup(w);
        p->lines = p->last = lalloc(lnum);
        p->left = p->right = NULL;
    } else if ((cond = strcmp(w, p->word)) == 0) {
        if (p->last->lnum != lnum) {    //not already listed for this line
            p->last->next = lalloc(lnum);
            p->last = p->last->next;
        }
    } else if (cond < 0)
        p->left = addtree(p->left, w, lnum);
    else
        p->right = addtree(p->right, w, lnum);
    return p;
}

//treeprint:  in-order print of tree p, each word with its line numbers
void treeprint(struct tnode *p)
{
    struct lnode *q;

    if (p != NULL) {
        treeprint(p->left);
        printf("%-15s", p->word);
        for (q = p->lines; q != NULL; q = q->next)
            printf(" %d", q->lnum);
        putchar('\n');
        treeprint(p->right);
    }
}

//talloc:  make a tnode
struct tnode *talloc(void)
{
    return (struct tnode *) malloc(sizeof(struct tnode));
}

//lalloc:  make an lnode holding line number n, at the end of a list
struct lnode *lalloc(int n)
{
    struct lnode *q;

    q = (struct lnode *) malloc(sizeof(struct lnode));
    q->lnum = n;
    q->next = NULL;
    return q;
}

//mystrdup:  make a duplicate of s (the book's strdup)
char *mystrdup(char *s)
{
    char *p;

    p = (char *) malloc(strlen(s)+1);   //+1 for '\0'
    if (p != NULL)
        strcpy(p, s);
    return p;
}

int getch(void);
void ungetch(int);

//getword:  get next word or character from input; a newline comes
//          back as a word of its own (the book's getword, except that
//          its whitespace loop stops at '\n')
int getword(char *word, int lim)
{
    int c;
    char *w = word;

    while (isspace(c = getch()) && c != '\n')
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

int buf[BUFSIZE];       //buffer for ungetch -- int, so it can hold EOF
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

*/
/*

#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace(), isdigit()
#include <string.h>     //for strcmp(), strncmp(), strlen(), strcpy()
#include <stdlib.h>     //for malloc(), atoi()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'int buffer, buffers, buffer_size, count;\n' | ./cc-c          # buffer, buffer_size, buffers (one per line)
//         or:  printf '%s\n' 'int buffer; char *s = "bufferx"; // buffery' | ./cc-c   # (nothing: the others are in a string and a comment)
//         or:  printf 'int count, counter, cost, costly, cos;\n' | ./cc-c -4         # cost, costly / blank line / count, counter
//         or:  ./cc-c -4 < cc-c.c        # getch getchar | isalnum isalpha | skipblockcomment skipline skipquoted | strcmp strcpy

//K&R2 exercise 6-2: write a program that reads a C program and prints
//in alphabetical order each group of variable names that are identical
//in the first 6 characters, but different somewhere thereafter. Don't
//count words within strings and comments. Make 6 a parameter that can
//be set from the command line.
//
//Built from three earlier blocks:
//  - getword from exercise 6-1 (archived three blocks down): skips
//    strings, character constants, comments and # lines, and keeps _
//    inside names.
//  - keytab + binsearch from 6.3: a C keyword is not a variable name.
//  - the tree from 6.5 (just below): every name is stored once, in
//    alphabetical order.
//
//"Variable names" here means every identifier that isn't a keyword.
//Telling a variable from a function or type name would need a real C
//parser, so names like printf are included too.
//
//HOW A GROUP IS FOUND. Each node gets a flag, match. When a new word w
//is added, addtree compares it with every node on its way down; if one
//shares the first num characters, both get match = 1. Is that enough
//to catch every partner? Yes, because of a tree fact: a newly added
//word always passes, on its way down, the two words that sort just
//before and just after it. Words sharing a prefix sort next to each
//other, so if w has any partner, one of those two neighbours is one.
//
//PRINTING. treeprint walks the tree in order (6.5's left, node, right),
//prints only nodes with match set, and puts a blank line between groups
//-- whenever a printed word's first num characters differ from the one
//printed before it.
//
//Words shorter than num are skipped: "cos" and "cost" aren't "identical
//in the first 4 characters" when one doesn't have 4.
//
//Command line: ./cc-c -4 sets num to 4; with no argument it's 6.
#define MAXWORD 100
#define DEFAULT 6

struct tnode {
    char *word;
    int match;              //1 if it shares its first num chars with another word
    struct tnode *left;
    struct tnode *right;
};

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

struct tnode *addtree(struct tnode *, char *, int, int *);
void treeprint(struct tnode *, int);
int binsearch(char *, struct key *, int);
int getword(char *, int);

//print groups of names that agree in their first num characters
int main(int argc, char *argv[])
{
    struct tnode *root = NULL;
    char word[MAXWORD];
    int num = DEFAULT;
    int found;

    if (argc == 2 && argv[1][0] == '-' && isdigit(argv[1][1]))
        num = atoi(argv[1] + 1);
    else if (argc != 1) {
        printf("usage: cc-c -6 < file.c\n");
        return 1;
    }
    if (num < 1) {
        printf("cc-c: the number must be at least 1\n");
        return 1;
    }

    while (getword(word, MAXWORD) != EOF)
        if ((isalpha(word[0]) || word[0] == '_')
                && (int) strlen(word) >= num
                && binsearch(word, keytab, NKEYS) < 0) {
            found = 0;
            root = addtree(root, word, num, &found);
        }
    treeprint(root, num);
    return 0;
}

struct tnode *talloc(void);
char *mystrdup(char *);

//addtree:  add w at or below p; mark it and any node met on the way
//          that shares its first num characters (*found carries that
//          down to the new node)
struct tnode *addtree(struct tnode *p, char *w, int num, int *found)
{
    int cond;

    if (p == NULL) {                    //a new word: make its node
        p = talloc();
        p->word = mystrdup(w);
        p->match = *found;
        p->left = p->right = NULL;
    } else if ((cond = strcmp(w, p->word)) != 0) {
        if (strncmp(w, p->word, num) == 0)
            *found = p->match = 1;      //same first num chars: a group
        if (cond < 0)
            p->left = addtree(p->left, w, num, found);
        else
            p->right = addtree(p->right, w, num, found);
    }                                   //cond == 0: already in the tree
    return p;
}

char *lastword = NULL;      //the word treeprint printed last

//treeprint:  in-order print of the matched words in tree p, with a
//            blank line between groups
void treeprint(struct tnode *p, int num)
{
    if (p != NULL) {
        treeprint(p->left, num);
        if (p->match) {
            if (lastword != NULL && strncmp(lastword, p->word, num) != 0)
                putchar('\n');
            printf("%s\n", p->word);
            lastword = p->word;
        }
        treeprint(p->right, num);
    }
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

//talloc:  make a tnode
struct tnode *talloc(void)
{
    return (struct tnode *) malloc(sizeof(struct tnode));
}

//mystrdup:  make a duplicate of s (the book's strdup)
char *mystrdup(char *s)
{
    char *p;

    p = (char *) malloc(strlen(s)+1);   //+1 for '\0'
    if (p != NULL)
        strcpy(p, s);
    return p;
}

int getch(void);
void ungetch(int);
int skipquoted(int quote);
int skipblockcomment(void);
int skipline(void);

//getword:  get next word or character from input, skipping comments
//          and preprocessor lines; a string or character constant
//          comes back as its opening quote (exercise 6-1)
int getword(char *word, int lim)
{
    int c, d;
    char *w = word;

    for (;;) {
        while (isspace(c = getch()))
            ;
        if (c == EOF) {
            *w = '\0';
            return EOF;
        }
        if (isalpha(c) || c == '_') {                   //identifier
            *w++ = c;
            for ( ; --lim > 0; w++)
                if (!isalnum(c = getch()) && c != '_') {
                    ungetch(c);
                    break;
                } else
                    *w = c;
            *w = '\0';
            return word[0];
        }
        if (c == '"' || c == '\'') {                    //string or char constant
            if (skipquoted(c) == EOF)
                continue;                               //next pass returns EOF
            word[0] = c;
            word[1] = '\0';
            return c;
        }
        if (c == '#') {                                 //preprocessor line
            skipline();
            continue;
        }
        if (c == '/') {
            if ((d = getch()) == '*') {                 //block comment
                skipblockcomment();
                continue;
            }
            if (d == '/') {                             //line comment
                skipline();
                continue;
            }
            ungetch(d);                                 //just a division sign
        }
        word[0] = c;                                    //any other character
        word[1] = '\0';
        return c;
    }
}

//skipquoted:  skip to the closing quote, stepping over \ escapes;
//             return the quote, or EOF if input ends first
int skipquoted(int quote)
{
    int c;

    while ((c = getch()) != EOF && c != quote)
        if (c == '\\' && getch() == EOF)
            return EOF;
    return c;
}

//skipblockcomment:  skip to the star-slash that ends a block comment
int skipblockcomment(void)
{
    int c, prev = 0;

    while ((c = getch()) != EOF) {
        if (prev == '*' && c == '/')
            return c;
        prev = c;
    }
    return EOF;
}

//skipline:  skip to the end of the line, following backslash-newline
//           continuations (a #define may span several lines)
int skipline(void)
{
    int c;

    while ((c = getch()) != EOF && c != '\n')
        if (c == '\\' && getch() == EOF)
            return EOF;
    return c;
}

#define BUFSIZE 100

int buf[BUFSIZE];       //buffer for ungetch -- int, so it can hold EOF
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

*/
/*

#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace()
#include <string.h>     //for strcmp(), strlen(), strcpy()
#include <stdlib.h>     //for malloc()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'the cat and the hat\n' | ./cc-c                         # 1 and, 1 cat, 1 hat, 2 the
//         or:  printf 'now is the time for all good men to come to the aid of their party\n' | ./cc-c
//         or:  ./cc-c < cc-c.c | sort -rn | head -5                           # the 5 most frequent words in this file

//K&R2 section 6.5: self-referential structures -- count EVERY word in
//the input (not just keywords) and print them in alphabetical order.
//
//6.3/6.4 had a fixed, sorted table of 32 keywords. Here the words
//aren't known in advance, so there's no table to search. Instead each
//new word gets its own struct, made at run time with malloc, and the
//structs are linked into a BINARY TREE:
//
//  struct tnode {
//      char *word;             the word
//      int count;              how often it's been seen
//      struct tnode *left;     words that sort BEFORE it
//      struct tnode *right;    words that sort AFTER it
//  };
//
//A struct can't contain itself (it would be infinitely big), but it can
//contain a POINTER to its own kind -- 8 bytes, whatever it points to.
//That's what "self-referential" means. A NULL left or right means
//"nothing there yet".
//
//"the cat and the hat" builds this tree (the first word is the root):
//
//              the
//             /
//          cat
//         /   \        (and < cat < hat < the)
//      and     hat
//
//addtree is RECURSIVE: compare the word with this node; equal -> count++;
//smaller -> do the same thing on the left subtree; bigger -> on the
//right. When it reaches a NULL, the word is new: make a node there.
//treeprint is recursive too: print everything on the left (smaller),
//then this node, then everything on the right (bigger) -- which comes
//out in alphabetical order. That's called an in-order traversal.
//
//Pieces the book shows on the pages around the listing, filled in:
//struct tnode (p.139), talloc and strdup (p.142-143), getword (6.3).
//
//Two fixes:
//  - the book's addtree definition says "struct treenode *" -- a typo
//    for struct tnode (the prototype has it right).
//  - the book's strdup is renamed mystrdup: <string.h> now declares its
//    own strdup (standard since C23, POSIX long before), and a second,
//    different declaration of the same name won't compile.
//
//Nothing is ever freed: the program ends right after printing, and the
//operating system takes back all its memory then.
#define MAXWORD 100

struct tnode {              //the tree node:
    char *word;             //points to the text
    int count;              //number of occurrences
    struct tnode *left;     //left child
    struct tnode *right;    //right child
};

struct tnode *addtree(struct tnode *, char *);
void treeprint(struct tnode *);
int getword(char *, int);

//word frequency count
int main(void)
{
    struct tnode *root;
    char word[MAXWORD];

    root = NULL;
    while (getword(word, MAXWORD) != EOF)
        if (isalpha(word[0]))
            root = addtree(root, word);
    treeprint(root);
    return 0;
}

struct tnode *talloc(void);
char *mystrdup(char *);

//addtree:  add a node with w, at or below p
struct tnode *addtree(struct tnode *p, char *w)
{
    int cond;

    if (p == NULL) {        //a new word has arrived
        p = talloc();       //make a new node
        p->word = mystrdup(w);
        p->count = 1;
        p->left = p->right = NULL;
    } else if ((cond = strcmp(w, p->word)) == 0)
        p->count++;         //repeated word
    else if (cond < 0)      //less than into left subtree
        p->left = addtree(p->left, w);
    else                    //greater than into right subtree
        p->right = addtree(p->right, w);
    return p;
}

//treeprint:  in-order print of tree p
void treeprint(struct tnode *p)
{
    if (p != NULL) {
        treeprint(p->left);
        printf("%4d %s\n", p->count, p->word);
        treeprint(p->right);
    }
}

//talloc:  make a tnode
struct tnode *talloc(void)
{
    return (struct tnode *) malloc(sizeof(struct tnode));
}

//mystrdup:  make a duplicate of s (the book's strdup)
char *mystrdup(char *s)
{
    char *p;

    p = (char *) malloc(strlen(s)+1);   //+1 for '\0'
    if (p != NULL)
        strcpy(p, s);
    return p;
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

*/
/*

#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace()
#include <string.h>     //for strcmp()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'int main(void)\n{\n    int i;\n    for (i = 0; i < 10; i++)\n        if (i > 5)\n            break;\n    return 0;\n}\n' | ./cc-c     # 1 break, 1 for, 1 if, 2 int, 1 return, 1 void
//         or:  printf 'int my_int;\n' | ./cc-c                                  # 2 int  (book getword: no _ handling)

//K&R2 section 6.4: pointers to structures -- the keyword counter again,
//with pointers instead of array indexes.
//
//Same program as 6.3 (archived two blocks below). keytab and getword
//are the book's, unchanged; only main and binsearch differ:
//
//1. binsearch RETURNS A POINTER to the matching struct key, or NULL if
//   the word isn't there (6.3 returned an index, or -1). The prototype
//   reads: binsearch is a function returning "struct key *".
//
//2. p->count  means  (*p).count  -- the member of the struct p points
//   to. The parentheses would be needed, since . binds tighter than *;
//   -> exists so nobody has to write them.
//
//3. high = &tab[n] points ONE PAST THE END of the table. C promises
//   that address is legal to compute and compare, though never to
//   dereference. So the loop is  while (low < high)  and the halves are
//   high = mid (not mid - 1): high is always just outside the range.
//
//4. mid = low + (high-low) / 2, not (low+high) / 2. Adding two
//   pointers is illegal -- the sum means nothing. Subtracting them
//   gives the number of ELEMENTS between them (an integer), and
//   pointer + integer is a pointer again. As a bonus this form can't
//   overflow, the bug mentioned for 6.3's binsearch.
//
//5. p++ moves to the NEXT STRUCT, not the next byte: the compiler
//   scales by sizeof(struct key), 16 here. Same for keytab + NKEYS,
//   the one-past-the-end pointer that stops main's for loop.
//
//Typo fixed: the book's binsearch definition says "struck key *tab".
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

*/
/*

#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace()
#include <string.h>     //for strcmp()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c < cc-c.c
//         or:  printf 'int my_int;\n' | ./cc-c                                  # 1 int
//         or:  printf '%s\n' 'puts("say \"if\" twice"); while (1) ;' | ./cc-c    # 1 while
//         or:  printf '%s\n' "char c = '\"'; return c;" | ./cc-c                 # 1 char, 1 return
//         or:  printf '/%s for *%s int x; // if else\n' '*' '/' | ./cc-c          # 1 int
//         or:  printf '#define M(x) \\\n    sizeof x\nint y;\n' | ./cc-c          # 1 int

//K&R2 exercise 6-1: our version of getword does not properly handle
//underscores, string constants, comments, or preprocessor control
//lines. Write a better version.
//
//Same keyword counter as section 6.3 (archived just below); only
//getword changes, plus one fix in getch/ungetch. getword now looks at
//the first character and decides what KIND of thing is starting:
//
//  letter or _     an identifier: collect letters, digits AND
//                  underscores, so my_int is one word, not my _ int
//  " or '          a string or character constant: skip to the
//                  matching closing quote, stepping over \" and \'
//                  escapes, and return the quote as a 1-char "word"
//                  (so main ignores it -- it doesn't start with a letter)
//  slash-star      a block comment: skip to star-slash
//  slash-slash     a line comment (C99, used all over this file):
//                  skip to the end of the line
//  #               a preprocessor line: skip to the end of the line,
//                  following backslash-newline continuations
//
//Comments and preprocessor lines are treated like whitespace: getword
//just goes round its loop again and reads the next real token. So the
//whole function is a for (;;) loop with one return per kind of token.
//
//Recognizing a comment needs TWO characters of lookahead: a slash
//might be division. getword reads the next character and, if it isn't
//a star or a slash, pushes it back with ungetch and returns the '/'.
//
//getch/ungetch: buf is now int, not char (the fix from exercise 4-9).
//getword may push back EOF (an identifier at the very end of input),
//and a char can't be relied on to hold EOF -- on a machine with
//unsigned chars, -1 would come back as 255 and the loop would never end.
//
//Still not handled: a # that isn't at the start of a line (only legal
//inside a #define anyway), keywords used only inside macros (they're
//skipped with the rest of the # line), and C99 keywords like inline.
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
int skipquoted(int quote);
int skipblockcomment(void);
int skipline(void);

//getword:  get next word or character from input, skipping comments
//          and preprocessor lines; a string or character constant
//          comes back as its opening quote
int getword(char *word, int lim)
{
    int c, d;
    char *w = word;

    for (;;) {
        while (isspace(c = getch()))
            ;
        if (c == EOF) {
            *w = '\0';
            return EOF;
        }
        if (isalpha(c) || c == '_') {                   //identifier
            *w++ = c;
            for ( ; --lim > 0; w++)
                if (!isalnum(c = getch()) && c != '_') {
                    ungetch(c);
                    break;
                } else
                    *w = c;
            *w = '\0';
            return word[0];
        }
        if (c == '"' || c == '\'') {                    //string or char constant
            if (skipquoted(c) == EOF)
                continue;                               //next pass returns EOF
            word[0] = c;
            word[1] = '\0';
            return c;
        }
        if (c == '#') {                                 //preprocessor line
            skipline();
            continue;
        }
        if (c == '/') {
            if ((d = getch()) == '*') {                 //block comment
                skipblockcomment();
                continue;
            }
            if (d == '/') {                             //line comment
                skipline();
                continue;
            }
            ungetch(d);                                 //just a division sign
        }
        word[0] = c;                                    //any other character
        word[1] = '\0';
        return c;
    }
}

//skipquoted:  skip to the closing quote, stepping over \ escapes;
//             return the quote, or EOF if input ends first
int skipquoted(int quote)
{
    int c;

    while ((c = getch()) != EOF && c != quote)
        if (c == '\\' && getch() == EOF)
            return EOF;
    return c;
}

//skipblockcomment:  skip to the star-slash that ends a block comment
int skipblockcomment(void)
{
    int c, prev = 0;

    while ((c = getch()) != EOF) {
        if (prev == '*' && c == '/')
            return c;
        prev = c;
    }
    return EOF;
}

//skipline:  skip to the end of the line, following backslash-newline
//           continuations (a #define may span several lines)
int skipline(void)
{
    int c;

    while ((c = getch()) != EOF && c != '\n')
        if (c == '\\' && getch() == EOF)
            return EOF;
    return c;
}

#define BUFSIZE 100

int buf[BUFSIZE];       //buffer for ungetch -- int, so it can hold EOF
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

*/
/*

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

*/
/*

#include <stdio.h>
#include <string.h>     //for strcpy(), strcat(), strcmp(), strlen()
#include <ctype.h>      //for isalpha(), isalnum()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'const char *p\nchar *const q\n' | ./cc-c                # p: pointer to const char | q: const pointer to char
//         or:  printf 'int main(int argc, char *argv[])\n' | ./cc-c            # main: function taking (argc: int, argv: array[] of pointer to char) returning int
//         or:  printf 'int (*comp)(void *, void *)\n' | ./cc-c                 # comp: pointer to function taking (pointer to void, pointer to void) returning int
//         or:  printf 'int printf(const char *fmt, ...)\n' | ./cc-c            # printf: function taking (fmt: pointer to const char, ...) returning int
//         or:  printf 'void (*signal(int sig, void (*handler)(int)))(int)\n' | ./cc-c
//         or:  printf 'unsigned long n\nstruct tnode *talloc(void)\nFILE *fp\n' | ./cc-c

//K&R2 exercise 5-20: expand dcl to handle declarations with function
//argument types, qualifiers like const, and so on.
//
//Builds on exercise 5-18's dcl (archived just below 5-19), keeping its
//error recovery. New:
//
//1. TYPES OF MORE THAN ONE WORD, and qualifiers in them:
//       unsigned long n         n:  unsigned long
//       const char *p           p:  pointer to const char
//       struct tnode *t         t:  pointer to struct tnode
//       FILE *fp                fp:  pointer to FILE
//   typespec() reads type words until it meets the declarator. The
//   words come from three lists (arrays of pointers, as in 5.6-5.8):
//       basetypes   void char short int long float double signed unsigned
//       quals       const volatile
//       tags        struct union enum   (followed by a tag name)
//   A name that's in none of the lists is the declarator's name -- or,
//   if no real type has been seen yet, a typedef name like FILE or
//   size_t. ("const x" is the one case this guesses wrong.)
//
//2. QUALIFIERS AFTER A *:
//       char *const q           q:  const pointer to char
//       char *const *pp         pp:  pointer to const pointer to char
//   dcl now records each * with its qualifiers (as bits: QCONST,
//   QVOLATILE) and prints them in REVERSE order -- the * nearest the
//   name is the outermost, so it's said first. The book printed every
//   "pointer to" alike, so the order never mattered.
//
//3. FUNCTION ARGUMENT TYPES:
//       int f(char *s, int)     f:  function taking (s: pointer to char,
//                                   int) returning int
//   A '(' after a name now starts an argument list. Each argument is a
//   whole declaration -- a type, then a declarator -- so params() reads
//   it with typespec() and dcl() again: the same functions, called
//   recursively. "..." is accepted as the last argument.
//
//   Arguments may have no name ("abstract declarators"): char *, or
//   int (*)(int). So dcl and dirdcl take a flag, abstract. With it, a
//   missing name is fine. It also makes '(' ambiguous: in int (*)(int)
//   the first '(' groups, the second starts an argument list. dirdcl
//   PEEKS at the next token (5-19's prevtoken): '*' or a plain name
//   means grouping; anything else means an argument list.
//
//The big change in shape: dcl and dirdcl used to write into the
//globals out and name. An argument has its own out and name, while the
//outer declaration's are only half built. So both now take the buffers
//as arguments -- dcl(out, name, abstract) -- and params() gives each
//argument fresh local buffers. Recursion keeps every level separate.
//
//Still not handled: typedef names in arguments that are followed by
//nothing (f(x) reads x as a type), initializers (int x = 5), several
//declarators in one line (int x, y), bit fields, and K&R-style old
//function definitions.
#define MAXTOKEN 100
#define MAXOUT   1000
#define MAXPTR   20         //max *'s in one dcl

enum { NAME, PARENS, BRACKETS };
enum { NOTTYPE, BASE, QUAL, TAG };      //what istype() says a word is
#define QCONST    1         //qualifier bits on a *
#define QVOLATILE 2

void dcl(char *out, char *name, int abstract);
void dirdcl(char *out, char *name, int abstract);
void params(char *out);
int typespec(char *type);
int istype(char *s);
int gettoken(void);
void errmsg(char *msg);
void append(char *to, char *s);

int tokentype;              //type of last token
char token[MAXTOKEN];       //last token string
int prevtoken = 0;          //1: next gettoken() repeats the last token
int err = 0;                //1 once the current line has an error

//convert declaration to words
int main(void)
{
    char name[MAXTOKEN];        //identifier name
    char datatype[MAXOUT];      //data type = const char, unsigned long, etc.
    char out[MAXOUT];

    while (gettoken() != EOF) {
        if (tokentype == '\n')              //blank line
            continue;
        err = 0;
        out[0] = name[0] = '\0';
        prevtoken = 1;                      //typespec re-reads this token
        if (typespec(datatype) == 0)
            errmsg("expected a data type");
        else {
            dcl(out, name, 0);              //parse rest of line
            if (tokentype != '\n' && tokentype != EOF)
                errmsg("syntax error");
        }
        if (err)                            //skip the rest of a bad line
            while (tokentype != '\n' && tokentype != EOF)
                gettoken();
        else
            printf("%s: %s %s\n", name, out, datatype);
    }
    return 0;
}

//dcl:  parse a declarator into out; its name (if any) goes into name
void dcl(char *out, char *name, int abstract)
{
    int ns, i, q[MAXPTR];

    for (ns = 0; gettoken() == '*'; ns++) { //each * and its qualifiers
        if (ns >= MAXPTR) {
            errmsg("too many *'s");
            return;
        }
        q[ns] = 0;
        while (gettoken() == NAME && istype(token) == QUAL)
            q[ns] |= (strcmp(token, "const") == 0) ? QCONST : QVOLATILE;
        prevtoken = 1;                      //not a qualifier: give it back
    }
    dirdcl(out, name, abstract);
    for (i = ns-1; i >= 0; i--) {           //the * nearest the name first
        if (q[i] & QCONST)
            append(out, " const");
        if (q[i] & QVOLATILE)
            append(out, " volatile");
        append(out, " pointer to");
    }
}

//dirdcl:  parse a direct declarator into out
void dirdcl(char *out, char *name, int abstract)
{
    int type;

    if (tokentype == '(') {
        type = gettoken();                  //peek: grouping, or arguments?
        prevtoken = 1;
        if (type == '*' || (type == NAME && istype(token) == NOTTYPE)) {
            dcl(out, name, abstract);       //( dcl )
            if (tokentype != ')') {
                errmsg("missing )");
                return;
            }
            type = gettoken();
        } else if (abstract)
            type = '(';                     //no name, then an argument list
        else {
            errmsg("expected name or (dcl)");
            return;
        }
    } else if (tokentype == NAME) {         //variable name
        strcpy(name, token);
        type = gettoken();
    } else if (abstract)
        type = tokentype;                   //no name: suffixes may follow
    else {
        errmsg("expected name or (dcl)");
        return;
    }
    while (type == PARENS || type == BRACKETS || type == '(') {
        if (type == PARENS)
            append(out, " function returning");
        else if (type == BRACKETS) {
            append(out, " array");
            append(out, token);
            append(out, " of");
        } else {
            params(out);                    //( argument list )
            if (err)
                return;
        }
        type = gettoken();
    }
}

//params:  parse a function's argument list, after its '('
void params(char *out)
{
    char ptype[MAXOUT];         //an argument's type
    char pout[MAXOUT];          //...its declarator, in words
    char pname[MAXTOKEN];       //...and its name, if it has one
    int n = 0;

    append(out, " function taking (");
    do {
        if (n++ > 0)
            append(out, ", ");
        if (gettoken() == '.') {            //... : more arguments may follow
            if (gettoken() != '.' || gettoken() != '.') {
                errmsg("expected ...");
                return;
            }
            append(out, "...");
            gettoken();                     //should be the ')'
            break;
        }
        prevtoken = 1;
        if (typespec(ptype) == 0) {
            errmsg("expected an argument type");
            return;
        }
        pout[0] = pname[0] = '\0';
        dcl(pout, pname, 1);                //name optional
        if (err)
            return;
        if (pname[0] != '\0') {
            append(out, pname);
            append(out, ": ");
        }
        if (pout[0] != '\0') {
            append(out, pout + 1);          //skip pout's leading blank
            append(out, " ");
        }
        append(out, ptype);
    } while (tokentype == ',');
    if (tokentype != ')') {
        errmsg("missing ) after arguments");
        return;
    }
    append(out, ") returning");
}

//typespec:  read a type like "const unsigned long" into type;
//return the number of words read (0: no type there)
int typespec(char *type)
{
    int n = 0;                  //words in type
    int base = 0;               //1 once a real type (not a qualifier) is seen
    int kind;

    type[0] = '\0';
    while (gettoken() == NAME) {
        kind = istype(token);
        if (kind == NOTTYPE) {
            if (base)
                break;                      //the declarator's name
            base = 1;                       //a typedef name: FILE, size_t
        } else if (kind == BASE)
            base = 1;
        if (n++ > 0)
            append(type, " ");
        append(type, token);
        if (kind == TAG) {                  //struct, union, enum: + a tag
            if (gettoken() != NAME) {
                errmsg("expected a struct/union/enum tag");
                return 0;
            }
            append(type, " ");
            append(type, token);
            base = 1;
        }
    }
    prevtoken = 1;                          //that token isn't part of the type
    return n;
}

char *basetypes[] = { "void", "char", "short", "int", "long", "float",
                      "double", "signed", "unsigned", NULL };
char *quals[] = { "const", "volatile", NULL };
char *tags[] = { "struct", "union", "enum", NULL };

//inlist:  1 if s is one of the words in list (which ends with NULL)
int inlist(char *list[], char *s)
{
    for ( ; *list != NULL; list++)
        if (strcmp(*list, s) == 0)
            return 1;
    return 0;
}

//istype:  BASE, QUAL or TAG if s is that kind of type word, else NOTTYPE
int istype(char *s)
{
    if (inlist(basetypes, s))
        return BASE;
    else if (inlist(quals, s))
        return QUAL;
    else if (inlist(tags, s))
        return TAG;
    else
        return NOTTYPE;
}

//errmsg:  report the first error on a line; later ones are echoes of it
void errmsg(char *msg)
{
    if (!err)
        printf("error: %s\n", msg);
    err = 1;
}

//append:  add s to the end of to (a MAXOUT buffer), if there's room
void append(char *to, char *s)
{
    if (strlen(to) + strlen(s) < MAXOUT)
        strcat(to, s);
    else
        errmsg("declaration too long");
}

//gettoken:  return next token
int gettoken(void)
{
    int c, getch(void);
    void ungetch(int);
    char *p = token;

    if (prevtoken) {                    //a token given back: repeat it
        prevtoken = 0;
        return tokentype;
    }
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
        for (*p++ = c; (c = getch()) != ']' && c != '\n' && c != EOF; )
            if (p < token + MAXTOKEN - 2)   //leave room for ']' and '\0'
                *p++ = c;
        if (c != ']') {                 //line ended inside [ ]
            *p = '\0';
            errmsg("missing ]");
            return tokentype = c;       //the '\n' (or EOF) ends the line
        }
        *p++ = ']';
        *p = '\0';
        return tokentype = BRACKETS;
    } else if (isalpha(c) || c == '_') {
        for (*p++ = c; isalnum(c = getch()) || c == '_'; )
            if (p < token + MAXTOKEN - 1)   //leave room for '\0'
                *p++ = c;
        *p = '\0';
        ungetch(c);
        return tokentype = NAME;
    } else
        return tokentype = c;
}

//--- from section 4.3 ---

#define BUFSIZE 100

int buf[BUFSIZE];           //buffer for ungetch (int: holds any byte)
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

*/
/*

#include <stdio.h>
#include <string.h>     //for strcpy(), strcat()
#include <ctype.h>      //for isalpha(), isalnum()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'argv * * char\n' | ./cc-c             # char **argv          (5.12's undcl: char (*(*argv)))
//         or:  printf 'daytab [13] * int\n' | ./cc-c         # int *daytab[13]      (5.12's undcl: int (*daytab[13]))
//         or:  printf 'daytab * [13] int\n' | ./cc-c         # int (*daytab)[13]    (parentheses needed: kept)
//         or:  printf 'x () * [] * () char\n' | ./cc-c       # char (*(*x())[])()
//         or:  printf 'x * * [] char\n' | ./cc-c             # char (**x)[]

//K&R2 exercise 5-19: modify undcl so that it does not add redundant
//parentheses to declarations.
//
//Builds on section 5.12's undcl (archived just below 5-18). undcl
//wrapped EVERY * as (*...), giving char (*(*argv)) for char **argv.
//
//When are the parentheses needed? Only when the NEXT token is () or
//[]. Those bind tighter than *, so without parentheses they'd attach
//to the name instead of to the pointer:
//
//    *daytab[13]       daytab is an array of pointers
//    (*daytab)[13]     daytab is a pointer to an array
//
//Anything else after the * -- another *, the type name, or the end of
//the line -- can't steal it, so "*" alone is enough.
//
//So at each *, undcl must LOOK AHEAD one token before deciding. It
//reads the next token, then marks it to be handed out again: a flag,
//prevtoken, makes the next gettoken() call return the same token
//instead of reading new input. That's "peek": see a token without
//using it up.
//
//    x * * [] char
//    *   next is *    ->  no ( )    *x
//    *   next is []   ->  ( )       (**x)
//    []                             (**x)[]
//    char                           char (**x)[]
//
//Also fixed: the inner loop now stops at EOF as well as '\n'. undcl's
//loop waited only for '\n', so a last line without one made it loop
//forever printing "invalid input" (gettoken returns EOF every time).
#define MAXTOKEN 100
#define MAXOUT   1000

enum { NAME, PARENS, BRACKETS };

int gettoken(void);

int tokentype;              //type of last token
char token[MAXTOKEN];       //last token string
char out[MAXOUT];
int prevtoken = 0;          //1: next gettoken() repeats the last token

//undcl:  convert word descriptions to declarations
int main(void)
{
    int type;
    char temp[MAXTOKEN + MAXOUT];   //room for token, a blank and out

    while (gettoken() != EOF) {
        strcpy(out, token);
        while ((type = gettoken()) != '\n' && type != EOF)
            if (type == PARENS || type == BRACKETS)
                strcat(out, token);
            else if (type == '*') {
                type = gettoken();      //peek at the next token...
                prevtoken = 1;          //...and hand it out again
                if (type == PARENS || type == BRACKETS)
                    sprintf(temp, "(*%s)", out);
                else
                    sprintf(temp, "*%s", out);
                strcpy(out, temp);
            } else if (type == NAME) {
                sprintf(temp, "%s %s", token, out);
                strcpy(out, temp);
            } else
                printf("invalid input at %s\n", token);
        printf("%s\n", out);
    }
    return 0;
}

//gettoken:  return next token
int gettoken(void)
{
    int c, getch(void);
    void ungetch(int);
    char *p = token;

    if (prevtoken) {                    //a peeked-at token: repeat it
        prevtoken = 0;
        return tokentype;
    }
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

*/
/*

#include <stdio.h>
#include <string.h>     //for strcpy(), strcat(), strlen()
#include <ctype.h>      //for isalpha(), isalnum()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'int x)\nchar **argv\n' | ./cc-c          # error: syntax error | argv:  pointer to pointer to char
//         or:  printf 'int (*pf\nint *daytab[13]\n' | ./cc-c    # error: missing ) | daytab:  array[13] of pointer to int
//         or:  printf 'int *\nvoid (*comp)()\n' | ./cc-c       # error: expected name or (dcl) | comp:  pointer to function returning void
//         or:  printf 'int x[5\nint (*daytab)[13]\n' | ./cc-c  # error: missing ] | daytab:  pointer to array[13] of int
//         or:  printf '*x\n\nchar c' | ./cc-c                  # error: expected a data type | c:  char

//K&R2 exercise 5-18: make dcl recover from input errors.
//
//Builds on section 5.12's dcl (archived two blocks down, below undcl).
//The book's dcl, given the bad line "int x)", printed:
//
//    syntax error
//    x:  int                         <- a result for a line that failed
//    error: expected name or (dcl)   <- the leftover \n read as a new
//    syntax error                       line, then EOF read as a name
//    x:  x
//
//Two problems: one mistake produces a CASCADE of messages, and the
//parse keeps reading past the end of the bad line into the next one.
//Recovery here means: report the FIRST error on a line, print no
//result for that line, skip whatever is left of it, and start fresh on
//the next line. Now "int x)" gives just:
//
//    error: syntax error
//
//How:
//1. A flag, err, set by errmsg(). errmsg prints only if err is still
//   0, so the first error on a line is reported and the echoes of it
//   are not. main clears err at the start of every line.
//2. dirdcl RETURNS as soon as it finds an error. The book's dirdcl
//   carried on into its while loop, calling gettoken -- which, if the
//   error was at the end of the line, read the NEXT line's first token.
//3. After the parse, if err is set, main throws away tokens up to the
//   '\n' (or EOF), then prints nothing for the line.
//
//Other input that broke the book's version, also fixed:
//4. "int x[5" -- no ']'. The book's loop
//       for (*p++ = c; (*p++ = getch()) != ']'; )
//   kept reading until it found a ']' -- across lines, past EOF, past
//   the end of token[100] into other memory. Now it stops at '\n' or
//   EOF and reports "missing ]".
//5. A name or [size] longer than token[] holds -- the book wrote past
//   the end of token. Now the extra characters are dropped.
//6. Too many *'s, ()'s or []'s -- each adds a phrase to out[1000] by
//   strcat, which never checks the size. append() checks first and
//   reports "declaration too long".
//7. A line not starting with a name ("*x"): the book copied whatever
//   was left in token as the data type. Now: "expected a data type".
//8. Blank lines are skipped, and a last line without '\n' is accepted
//   (EOF counts as the end of the line).
//9. buf in ungetch is now int, not char, so a pushed-back byte >= 128
//   (part of a UTF-8 character) comes back as itself, not as a negative
//   number -- which isalpha() would choke on.
#define MAXTOKEN 100
#define MAXOUT   1000

enum { NAME, PARENS, BRACKETS };

void dcl(void);
void dirdcl(void);
int gettoken(void);
void errmsg(char *msg);
void append(char *s);

int tokentype;              //type of last token
char token[MAXTOKEN];       //last token string
char name[MAXTOKEN];        //identifier name
char datatype[MAXTOKEN];    //data type = char, int, etc.
char out[MAXOUT];
int err = 0;                //1 once the current line has an error

//convert declaration to words
int main(void)
{
    while (gettoken() != EOF) {
        if (tokentype == '\n')              //blank line
            continue;
        err = 0;
        out[0] = '\0';
        if (tokentype != NAME)
            errmsg("expected a data type");
        else {
            strcpy(datatype, token);        //1st token is the datatype
            dcl();                          //parse rest of line
            if (tokentype != '\n' && tokentype != EOF)
                errmsg("syntax error");
        }
        if (err)                            //skip the rest of a bad line
            while (tokentype != '\n' && tokentype != EOF)
                gettoken();
        else
            printf("%s: %s %s\n", name, out, datatype);
    }
    return 0;
}

//errmsg:  report the first error on a line; later ones are echoes of it
void errmsg(char *msg)
{
    if (!err)
        printf("error: %s\n", msg);
    err = 1;
}

//append:  add s to the end of out, if there's room
void append(char *s)
{
    if (strlen(out) + strlen(s) < MAXOUT)
        strcat(out, s);
    else
        errmsg("declaration too long");
}

//dcl:  parse a declarator
void dcl(void)
{
    int ns;

    for (ns = 0; gettoken() == '*'; )   //count *'s
        ns++;
    dirdcl();
    while (ns-- > 0)
        append(" pointer to");
}

//dirdcl:  parse a direct declarator
void dirdcl(void)
{
    int type;

    if (tokentype == '(') {             //( dcl )
        dcl();
        if (tokentype != ')') {
            errmsg("missing )");
            return;                     //don't read past the error
        }
    } else if (tokentype == NAME)       //variable name
        strcpy(name, token);
    else {
        errmsg("expected name or (dcl)");
        return;                         //don't read past the error
    }
    while ((type=gettoken()) == PARENS || type == BRACKETS)
        if (type == PARENS)
            append(" function returning");
        else {
            append(" array");
            append(token);
            append(" of");
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
        for (*p++ = c; (c = getch()) != ']' && c != '\n' && c != EOF; )
            if (p < token + MAXTOKEN - 2)   //leave room for ']' and '\0'
                *p++ = c;
        if (c != ']') {                 //line ended inside [ ]
            *p = '\0';
            errmsg("missing ]");
            return tokentype = c;       //the '\n' (or EOF) ends the line
        }
        *p++ = ']';
        *p = '\0';
        return tokentype = BRACKETS;
    } else if (isalpha(c)) {
        for (*p++ = c; isalnum(c = getch()); )
            if (p < token + MAXTOKEN - 1)   //leave room for '\0'
                *p++ = c;
        *p = '\0';
        ungetch(c);
        return tokentype = NAME;
    } else
        return tokentype = c;
}

//--- from section 4.3 ---

#define BUFSIZE 100

int buf[BUFSIZE];           //buffer for ungetch (int: holds any byte)
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

*/
/*

#include <stdio.h>
#include <string.h>     //for strcpy(), strcat()
#include <ctype.h>      //for isalpha(), isalnum()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'x () * [] * () char\n' | ./cc-c       # char (*(*x())[])()
//         or:  printf 'daytab * [13] int\n' | ./cc-c         # int (*daytab)[13]
//         or:  printf 'comp * () void\n' | ./cc-c            # void (*comp)()
//         or:  printf 'argv * * char\n' | ./cc-c             # char (*(*argv))     correct, but with redundant ()
//         or:  printf 'daytab [13] * int\n' | ./cc-c         # int (*daytab[13])   correct, but with redundant ()

//K&R2 section 5.12: undcl, the reverse of dcl (archived just below).
//It reads a declaration written as words -- in a short form, one token
//per word -- and turns it back into C:
//
//    x () * [] * () char    ->    char (*(*x())[])()
//
//The words are the same order dcl prints them in, shortened:
//    x () * [] * () char
//    x: function returning pointer to array[] of pointer to function
//       returning char
//
//How it works: out holds the declaration built so far, and each token
//WRAPS it from the inside out:
//
//    token   rule                    out
//    x       start                   x
//    ()      append                  x()
//    *       wrap as (*...)          (*x())
//    []      append                  (*x())[]
//    *       wrap as (*...)          (*(*x())[])
//    ()      append                  (*(*x())[])()
//    char    put type in front       char (*(*x())[])()
//
//Every * gets parentheses around it, needed or not, because undcl
//doesn't look ahead to see whether a () or [] follows. So "argv * *
//char" gives char (*(*argv)) -- correct C, but char **argv is what a
//person would write. Exercise 5-19 asks you to remove the redundant
//parentheses.
//
//sprintf is printf into a string instead of onto the screen:
//sprintf(temp, "(*%s)", out) writes "(*" + out + ")" into temp. It
//can't write into out directly -- out is also the input being read --
//hence temp, then strcpy back into out.
//
//Fixed from the book's text:
//1. main() -> int main(void), as in dcl (gcc 15 / C23).
//2. Added printf("%s\n", out) after the inner loop -- without it the
//   declaration is built and never printed.
//3. temp was char temp[MAXTOKEN] -- 100 bytes -- but sprintf copies
//   all of out (up to 1000) into it. gcc -Wall caught it:
//       warning: '%s' directive writing up to 999 bytes into a
//       region of size 98 [-Wformat-overflow=]
//   A declaration over ~97 characters would overflow temp and
//   overwrite whatever memory follows. temp is now MAXTOKEN + MAXOUT,
//   big enough for token + ' ' + out.
//
//gettoken, getch and ungetch are unchanged from dcl.
#define MAXTOKEN 100
#define MAXOUT   1000

enum { NAME, PARENS, BRACKETS };

int gettoken(void);

int tokentype;              //type of last token
char token[MAXTOKEN];       //last token string
char out[MAXOUT];

//undcl:  convert word descriptions to declarations
int main(void)
{
    int type;
    char temp[MAXTOKEN + MAXOUT];   //room for token, a blank and out

    while (gettoken() != EOF) {
        strcpy(out, token);
        while ((type = gettoken()) != '\n')
            if (type == PARENS || type == BRACKETS)
                strcat(out, token);
            else if (type == '*') {
                sprintf(temp, "(*%s)", out);
                strcpy(out, temp);
            } else if (type == NAME) {
                sprintf(temp, "%s %s", token, out);
                strcpy(out, temp);
            } else
                printf("invalid input at %s\n", token);
        printf("%s\n", out);
    }
    return 0;
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

*/
/*

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

*/
/*

#include <stdio.h>
#include <stdlib.h>     //for atof(), atoi()
#include <string.h>     //for strcpy()
#include <ctype.h>      //for tolower(), isalnum(), isdigit()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'pointer\t102\n#define\t89\nPointer\t94\ndefine\t14\npointer\t98\n' | ./cc-c                # #define 89, Pointer 94, define 14, pointer 102, pointer 98
//         or:  printf 'pointer\t102\n#define\t89\nPointer\t94\ndefine\t14\npointer\t98\n' | ./cc-c +1 -df +2 -n   # define 14, #define 89, Pointer 94, pointer 98, pointer 102
//         or:  printf 'pointer\t102\n#define\t89\nPointer\t94\ndefine\t14\npointer\t98\n' | ./cc-c +1 -df +2 -nr  # #define 89, define 14, pointer 102, pointer 98, Pointer 94
//         or:  printf 'a-d\nAC\nab\n' | ./cc-c -dfr    # a-d AC ab   (no +N: whole line, as in 5-16)

//K&R2 exercise 5-17: add a field-searching capability, so sorting may
//be done on fields within lines, each field sorted according to an
//independent set of options. (The index for this book was sorted with
//-df for the index category and -n for the page numbers.)
//
//Builds on exercise 5-16 (archived just below).
//
//FIELDS: a line is split into fields at each TAB. In "pointer\t102",
//field 1 is "pointer" and field 2 is "102". Field 0 means the whole
//line. A field past the end of a line counts as an empty string.
//
//KEYS: "+N" on the command line starts a sort key on field N, and the
//flags that follow it (-n -r -f -d) belong to that key alone:
//
//    ./cc-c +1 -df +2 -n
//           ^^^^^^ ^^^^^
//           key 1: field 1, directory order, fold case
//                  key 2: field 2, numeric
//
//Two lines are compared on key 1 first. Only if key 1 calls them equal
//does key 2 get a say -- exactly how the book's index works: entries
//sort by name, and entries with the same name sort by page number.
//Flags given BEFORE any +N make a key on the whole line (field 0), so
//every command from 5-14 to 5-16 still works unchanged.
//
//Each key's flags are kept as bits in one int (chapter 2's bitwise
//operators), one bit per flag:
//
//    #define NUMERIC 1       0001
//    #define REVERSE 2       0010
//    #define FOLD    4       0100
//    #define DIR     8       1000
//
//-df sets opt |= DIR, then opt |= FOLD, giving 1100. Testing a flag is
//opt & FOLD: non-zero if that bit is on. Two parallel arrays hold the
//keys: kfield[i] is key i's field number, kopt[i] its flag bits.
//(Chapter 6's structs will be the neater way to bundle these.)
//
//What changed from 5-16:
//1. my_qsort now always gets ONE comparison, fieldcmp. For each key in
//   turn it copies that field out of both lines, compares the copies
//   with that key's flags, and returns the first non-zero answer.
//2. fold and dir are no longer globals: fieldcmp calls charcmp
//   directly, so it can simply pass them as arguments. Only my_qsort's
//   calls are limited to two arguments, and fieldcmp is the only
//   function my_qsort calls now.
//3. basecmp and revcmp are gone. -r is handled inside fieldcmp by the
//   same trick as revcmp -- comparing (b, a) instead of (a, b) -- but
//   per key, so +1 -df +2 -nr sorts names up and page numbers down.
#define MAXLINES  5000      //max #lines to be sorted
#define MAXLEN    10000     //max length of any input line (book: 1000)
#define ALLOCSIZE 1000000   //size of available space for alloc
#define MAXKEYS   10        //max #sort keys (+N) on the command line

#define NUMERIC 1           //-n: compare as numbers
#define REVERSE 2           //-r: decreasing order
#define FOLD    4           //-f: fold upper and lower case
#define DIR     8           //-d: only letters, digits and blanks

char *lineptr[MAXLINES];    //pointers to text lines

int nkeys = 0;              //number of sort keys
int kfield[MAXKEYS];        //kfield[i]: field that key i sorts on
int kopt[MAXKEYS];          //kopt[i]: key i's flag bits

int readlines(char *lineptr[], int nlines);
void writelines(char *lineptr[], int nlines);
void my_qsort(void *lineptr[], int left, int right,
              int (*comp)(void *, void *));
int fieldcmp(void *, void *);
void getfield(char *s, int n, char *field);
int numcmp(char *, char *);
int charcmp(char *, char *, int fold, int dir);

//sort input lines
int main(int argc, char *argv[])
{
    int nlines;             //number of input lines read
    int bad = 0;            //1 if the command line is wrong
    char *p, *q;
    int c;

    while (--argc > 0 && !bad) {
        p = *++argv;
        if (*p == '+') {                    //+N: start a key on field N
            for (q = p+1; isdigit((unsigned char) *q); q++)
                ;
            if (q == p+1 || *q != '\0') {   //no digits, or junk after them
                printf("sort: bad field %s\n", p);
                bad = 1;
            } else if (nkeys >= MAXKEYS) {
                printf("sort: more than %d keys\n", MAXKEYS);
                bad = 1;
            } else {
                kfield[nkeys] = atoi(p+1);
                kopt[nkeys++] = 0;
            }
        } else if (*p == '-') {             //flags for the current key
            if (nkeys == 0) {               //no +N yet: key on whole line
                kfield[0] = 0;
                kopt[0] = 0;
                nkeys = 1;
            }
            while ((c = *++p))
                switch (c) {
                case 'n':
                    kopt[nkeys-1] |= NUMERIC;
                    break;
                case 'r':
                    kopt[nkeys-1] |= REVERSE;
                    break;
                case 'f':
                    kopt[nkeys-1] |= FOLD;
                    break;
                case 'd':
                    kopt[nkeys-1] |= DIR;
                    break;
                default:
                    printf("sort: illegal option %c\n", c);
                    bad = 1;
                    break;
                }
        } else {
            printf("sort: unexpected argument %s\n", p);
            bad = 1;
        }
    }
    if (bad) {
        printf("usage: sort [+N] -n -r -f -d ...    e.g.  ./cc-c +1 -df +2 -n\n");
        return 1;
    }
    if (nkeys == 0) {                       //no arguments: plain text sort
        kfield[0] = 0;
        kopt[0] = 0;
        nkeys = 1;
    }
    if ((nlines = readlines(lineptr, MAXLINES)) >= 0) {
        my_qsort((void **) lineptr, 0, nlines-1, fieldcmp);
        writelines(lineptr, nlines);
        return 0;
    } else {
        printf("input too big to sort\n");
        return 1;
    }
}

//fieldcmp:  compare lines a and b key by key; the first key that
//finds a difference decides
int fieldcmp(void *a, void *b)
{
    char fa[MAXLEN], fb[MAXLEN];    //the current field of a and of b
    char *s1, *s2;
    int i, r;

    for (i = 0; i < nkeys; i++) {
        getfield(a, kfield[i], fa);
        getfield(b, kfield[i], fb);
        if (kopt[i] & REVERSE) {    //swap arguments, as revcmp did
            s1 = fb;
            s2 = fa;
        } else {
            s1 = fa;
            s2 = fb;
        }
        if (kopt[i] & NUMERIC)
            r = numcmp(s1, s2);
        else
            r = charcmp(s1, s2, kopt[i] & FOLD, kopt[i] & DIR);
        if (r != 0)
            return r;
    }
    return 0;                       //equal on every key
}

//getfield:  copy field n of line s into field; fields are separated
//by tabs, field 0 is the whole line, a missing field is empty
void getfield(char *s, int n, char *field)
{
    if (n == 0) {
        strcpy(field, s);
        return;
    }
    while (--n > 0) {               //skip the n-1 fields before field n
        while (*s != '\0' && *s != '\t')
            s++;
        if (*s == '\0') {           //line has fewer than n fields
            *field = '\0';
            return;
        }
        s++;                        //step over the tab
    }
    while (*s != '\0' && *s != '\t')
        *field++ = *s++;
    *field = '\0';
}

//numcmp:  compare s1 and s2 numerically
int numcmp(char *s1, char *s2)
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

//dirchar:  1 if c counts in directory order (letter, digit, blank)
int dirchar(int c)
{
    return isalnum(c) || c == ' ' || c == '\t';
}

//charcmp:  compare s1 and s2 as text; if fold, upper and lower case
//compare equal; if dir, only letters, digits and blanks are compared
int charcmp(char *s1, char *s2, int fold, int dir)
{
    unsigned char *p1 = (unsigned char *) s1;
    unsigned char *p2 = (unsigned char *) s2;
    int c1, c2;

    for (;;) {
        if (dir) {
            while (*p1 != '\0' && !dirchar(*p1))
                p1++;
            while (*p2 != '\0' && !dirchar(*p2))
                p2++;
        }
        c1 = fold ? tolower(*p1) : *p1;
        c2 = fold ? tolower(*p2) : *p2;
        if (c1 != c2)
            return c1 - c2;
        if (c1 == '\0')         //both strings ended together
            return 0;
        p1++;
        p2++;
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
#include <stdlib.h>     //for atof()
#include <string.h>     //for strcpy()
#include <ctype.h>      //for tolower(), isalnum()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'a-d\nAC\nab\n' | ./cc-c          # AC a-d ab
//         or:  printf 'a-d\nAC\nab\n' | ./cc-c -f       # a-d ab AC
//         or:  printf 'a-d\nAC\nab\n' | ./cc-c -d       # AC ab a-d
//         or:  printf 'a-d\nAC\nab\n' | ./cc-c -df      # ab AC a-d
//         or:  printf 'a-d\nAC\nab\n' | ./cc-c -dfr     # a-d AC ab

//K&R2 exercise 5-16: add the -d ("directory order") option, which
//makes comparisons only on letters, numbers and blanks. Make sure it
//works in conjunction with -f.
//
//Builds on exercise 5-15 (archived just below). -d means: while
//comparing, act as if every character that isn't a letter, a digit, a
//space or a tab weren't there. So "a-d" compares as "ad", and sorts
//AFTER "ab" -- without -d, '-' (45) is smaller than 'b' (98), and
//"a-d" sorts first.
//
//Why one comparison instead of more: -d and -f are independent, so
//separate functions would need four (plain, fold, dir, dir+fold), and
//every future flag would double that. Instead ONE function, charcmp,
//does both jobs, switched on and off by two flags:
//
//    1. if dir:  skip ahead in each string past characters -d ignores
//    2. if fold: compare tolower() of the two characters, else the
//                characters themselves
//    3. differ?  return the difference;  both at '\0'?  return 0
//    4. otherwise step both pointers and go round again
//
//With neither flag, charcmp is just strcmp, so strcmp_v and 5-15's
//strcmp_f are both gone.
//
//fold and dir moved OUT of main and became globals, for the same
//reason basecmp is one: my_qsort calls charcmp with exactly two
//arguments, so charcmp has no other way to learn what the flags are.
//
//-n still overrides -d and -f (numbers have no case or punctuation to
//skip), and 5-14's revcmp still reverses whichever comparison was
//picked, so -r works with everything.
//
//Note: in the default "C" locale, isalnum() is true only for ASCII
//letters and digits. Bytes of a UTF-8 character like 乾 are >= 128, so
//-d skips them entirely.
#define MAXLINES  5000      //max #lines to be sorted
#define MAXLEN    10000     //max length of any input line (book: 1000)
#define ALLOCSIZE 1000000   //size of available space for alloc

char *lineptr[MAXLINES];    //pointers to text lines

int readlines(char *lineptr[], int nlines);
void writelines(char *lineptr[], int nlines);
void my_qsort(void *lineptr[], int left, int right,
              int (*comp)(void *, void *));
int numcmp(void *, void *);
int charcmp(void *, void *);
int revcmp(void *, void *);

int (*basecmp)(void *, void *);     //the comparison revcmp reverses
int fold = 0;           //1 if -f: fold upper and lower case
int dir = 0;            //1 if -d: compare only letters, digits, blanks

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
            case 'f':
                fold = 1;
                break;
            case 'd':
                dir = 1;
                break;
            default:
                printf("sort: illegal option %c\n", c);
                argc = -1;          //force the usage message below
                break;
            }
    if (argc != 0) {
        printf("usage: sort -n -r -f -d    e.g.  printf 'a-d\\nAC\\nab\\n' | ./cc-c -df\n");
        return 1;
    }
    basecmp = numeric ? numcmp : charcmp;
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

//dirchar:  1 if c counts in directory order (letter, digit, blank)
int dirchar(int c)
{
    return isalnum(c) || c == ' ' || c == '\t';
}

//charcmp:  compare s1 and s2 as text; if fold, upper and lower case
//compare equal; if dir, only letters, digits and blanks are compared
int charcmp(void *s1, void *s2)
{
    unsigned char *p1 = s1, *p2 = s2;
    int c1, c2;

    for (;;) {
        if (dir) {
            while (*p1 != '\0' && !dirchar(*p1))
                p1++;
            while (*p2 != '\0' && !dirchar(*p2))
                p2++;
        }
        c1 = fold ? tolower(*p1) : *p1;
        c2 = fold ? tolower(*p2) : *p2;
        if (c1 != c2)
            return c1 - c2;
        if (c1 == '\0')         //both strings ended together
            return 0;
        p1++;
        p2++;
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
#include <stdlib.h>     //for atof()
#include <string.h>     //for strcmp(), strcpy()
#include <ctype.h>      //for tolower()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'b\nA\na\nB\n' | ./cc-c           (A B a b)
//         or:  printf 'b\nA\na\nB\n' | ./cc-c -f        (A a b B)
//         or:  printf 'b\nA\na\nB\n' | ./cc-c -fr       (B b A a)
//         or:  printf '10\n9\n100\n' | ./cc-c -nr       (100 10 9)

//K&R2 exercise 5-15: add the option -f to fold upper and lower case
//together, so that case distinctions are not made during sorting; for
//example, a and A compare equal.
//
//Builds on exercise 5-14 (archived just below). Why plain sorting
//needs fixing: strcmp compares character CODES, and in ASCII every
//upper-case letter comes before every lower-case one ('A' is 65, 'Z'
//is 90, 'a' is 97). So without -f, "B" sorts before "a" -- the output
//is A B a b, not a dictionary order.
//
//The fix is one new comparison, strcmp_f. It walks both strings like
//strcmp does, but compares tolower() of each character, so 'A' and
//'a' both look like 'a'. It returns the difference of the first pair
//that differs (after folding), or 0 if the strings match to the end.
//
//Two details inside strcmp_f:
//1. tolower(c) is only defined for c that fits in an unsigned char (or
//   is EOF). A plain char holding a byte >= 128 (e.g. part of a UTF-8
//   character) can be NEGATIVE, so each byte is read through an
//   unsigned char pointer first.
//2. The loop tests for '\0' only on s1. That's enough: if s2 ends
//   first, its '\0' differs from s1's character, so the loop stops on
//   the mismatch anyway.
//
//Nothing else changes. main just picks the base comparison:
//
//    basecmp = numeric ? numcmp : (fold ? strcmp_f : strcmp_v);
//
//and 5-14's revcmp reverses whichever one was picked, so -f works with
//-r for free (-n ignores -f: numbers have no case).
//
//Note: "a" and "A" compare EQUAL under -f, so which one prints first is
//up to my_qsort -- it isn't a stable sort, so equal lines may come out
//in either order.
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
int strcmp_f(void *, void *);
int revcmp(void *, void *);

int (*basecmp)(void *, void *);     //the comparison revcmp reverses

//sort input lines
int main(int argc, char *argv[])
{
    int nlines;             //number of input lines read
    int numeric = 0;        //1 if -n: numeric sort
    int reverse = 0;        //1 if -r: decreasing order
    int fold = 0;           //1 if -f: fold upper and lower case
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
            case 'f':
                fold = 1;
                break;
            default:
                printf("sort: illegal option %c\n", c);
                argc = -1;          //force the usage message below
                break;
            }
    if (argc != 0) {
        printf("usage: sort -n -r -f    e.g.  printf 'b\\nA\\na\\n' | ./cc-c -f\n");
        return 1;
    }
    basecmp = numeric ? numcmp : (fold ? strcmp_f : strcmp_v);
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

//strcmp_f:  like strcmp, but upper and lower case compare equal
int strcmp_f(void *s1, void *s2)
{
    unsigned char *p1 = s1, *p2 = s2;

    for ( ; tolower(*p1) == tolower(*p2); p1++, p2++)
        if (*p1 == '\0')
            return 0;
    return tolower(*p1) - tolower(*p2);
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

*/
/*

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

*/
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
