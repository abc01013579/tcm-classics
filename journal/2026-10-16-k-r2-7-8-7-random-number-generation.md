---
title: K&R2 7.8.7 Random Number Generation
date: 2026-10-16
---

```c
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

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
1. RAND_MAX = 2147483647  (= INT_MAX here: glibc uses the whole int range)
   the standard only promises RAND_MAX >= 32767
   first rand() calls, no srand: 1804289383 846930886 1681692777
   after srand(1):               1804289383 846930886 1681692777   <- same three

2. frand() five times: 0.798440 0.911647 0.197551 0.335223 0.768230
   without (double): rand() / RAND_MAX = 596516649 / 2147483647 = 0  (int division)
   biggest rand() / RAND_MAX       = 1.00000000000000000  <- 1 is NOT < 1
   biggest rand() / (RAND_MAX+1.0) = 0.99999999953433871
   RAND_MAX+1.0 = 2147483648.0;  RAND_MAX+1 as int would be INT_MAX+1: overflow
   a die, (int)(frand() * 6) + 1: 4 3 4 3 4 6 6 4 5 1

3. drand48() three times: 0.04163034477187821 0.45449244472862915 0.83481721816691490

4. srand(1) first: 1804289383 846930886 1681692777
   srand(1) again: 1804289383 846930886 1681692777   <- same seed, same sequence

5. kr_rand() after kr_srand(1): 16838 5758 10113 17515 31051
   range 0..32767 only -- the standard's minimum RAND_MAX;
   glibc's rand is a different, bigger generator, so its
   numbers above don't match these even with the same seed

three-coin cast, seed 1 (top line first):
   line 6: 6  -x-
   line 5: 7  ---
   line 4: 7  ---
   line 3: 8  - -
   line 2: 7  ---
   line 1: 7  ---
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
1. RAND_MAX = 2147483647  (= INT_MAX here: glibc uses the whole int range)
   the standard only promises RAND_MAX >= 32767
   first rand() calls, no srand: 1804289383 846930886 1681692777
   after srand(1):               1804289383 846930886 1681692777   <- same three

2. frand() five times: 0.798440 0.911647 0.197551 0.335223 0.768230
   without (double): rand() / RAND_MAX = 596516649 / 2147483647 = 0  (int division)
   biggest rand() / RAND_MAX       = 1.00000000000000000  <- 1 is NOT < 1
   biggest rand() / (RAND_MAX+1.0) = 0.99999999953433871
   RAND_MAX+1.0 = 2147483648.0;  RAND_MAX+1 as int would be INT_MAX+1: overflow
   a die, (int)(frand() * 6) + 1: 4 3 4 3 4 6 6 4 5 1

3. drand48() three times: 0.04163034477187821 0.45449244472862915 0.83481721816691490

4. srand(1) first: 1804289383 846930886 1681692777
   srand(1) again: 1804289383 846930886 1681692777   <- same seed, same sequence

5. kr_rand() after kr_srand(1): 16838 5758 10113 17515 31051
   range 0..32767 only -- the standard's minimum RAND_MAX;
   glibc's rand is a different, bigger generator, so its
   numbers above don't match these even with the same seed

three-coin cast, seed 1 (top line first):
   line 6: 6  -x-
   line 5: 7  ---
   line 4: 7  ---
   line 3: 8  - -
   line 2: 7  ---
   line 1: 7  ---
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c 42
1. RAND_MAX = 2147483647  (= INT_MAX here: glibc uses the whole int range)
   the standard only promises RAND_MAX >= 32767
   first rand() calls, no srand: 1804289383 846930886 1681692777
   after srand(1):               1804289383 846930886 1681692777   <- same three

2. frand() five times: 0.798440 0.911647 0.197551 0.335223 0.768230
   without (double): rand() / RAND_MAX = 596516649 / 2147483647 = 0  (int division)
   biggest rand() / RAND_MAX       = 1.00000000000000000  <- 1 is NOT < 1
   biggest rand() / (RAND_MAX+1.0) = 0.99999999953433871
   RAND_MAX+1.0 = 2147483648.0;  RAND_MAX+1 as int would be INT_MAX+1: overflow
   a die, (int)(frand() * 6) + 1: 4 3 4 3 4 6 6 4 5 1

3. drand48() three times: 0.04163034477187821 0.45449244472862915 0.83481721816691490

4. srand(42) first: 71876166 708592740 1483128881
   srand(42) again: 71876166 708592740 1483128881   <- same seed, same sequence

5. kr_rand() after kr_srand(42): 19081 17033 15269 25461 13856
   range 0..32767 only -- the standard's minimum RAND_MAX;
   glibc's rand is a different, bigger generator, so its
   numbers above don't match these even with the same seed

three-coin cast, seed 42 (top line first):
   line 6: 7  ---
   line 5: 9  -o-
   line 4: 8  - -
   line 3: 7  ---
   line 2: 9  -o-
   line 1: 8  - -
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c time
1. RAND_MAX = 2147483647  (= INT_MAX here: glibc uses the whole int range)
   the standard only promises RAND_MAX >= 32767
   first rand() calls, no srand: 1804289383 846930886 1681692777
   after srand(1):               1804289383 846930886 1681692777   <- same three

2. frand() five times: 0.798440 0.911647 0.197551 0.335223 0.768230
   without (double): rand() / RAND_MAX = 596516649 / 2147483647 = 0  (int division)
   biggest rand() / RAND_MAX       = 1.00000000000000000  <- 1 is NOT < 1
   biggest rand() / (RAND_MAX+1.0) = 0.99999999953433871
   RAND_MAX+1.0 = 2147483648.0;  RAND_MAX+1 as int would be INT_MAX+1: overflow
   a die, (int)(frand() * 6) + 1: 4 3 4 3 4 6 6 4 5 1

3. drand48() three times: 0.04163034477187821 0.45449244472862915 0.83481721816691490

4. srand(1792192586) first: 1110961151 1820287451 1373220166
   srand(1792192586) again: 1110961151 1820287451 1373220166   <- same seed, same sequence

5. kr_rand() after kr_srand(1792192586): 20647 1318 31635 24979 4093
   range 0..32767 only -- the standard's minimum RAND_MAX;
   glibc's rand is a different, bigger generator, so its
   numbers above don't match these even with the same seed

three-coin cast, seed 1792192586 (top line first):
   line 6: 8  - -
   line 5: 7  ---
   line 4: 7  ---
   line 3: 8  - -
   line 2: 7  ---
   line 1: 6  -x-
```
