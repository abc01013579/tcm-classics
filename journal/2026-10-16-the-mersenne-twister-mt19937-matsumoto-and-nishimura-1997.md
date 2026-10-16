---
title: The Mersenne Twister, MT19937 (Matsumoto and Nishimura, 1997)
date: 2026-10-16
---

```c
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


win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
577090037
2444712010
3639700191
3445702192
3280387012
0.06310682188770933
0.11791870367106105
0.76096244491257559
0.47224524357611664
0.37961522332372777
win@DESKTOP-MEIH88T:~/webdev-projects$ python3 -c 'import random; random.seed(1); [print(random.getrandbits(32)) for _ in range(5)]; [print("%.17g" % random.random()) for _ in range(5)]'
577090037
2444712010
3639700191
3445702192
3280387012
0.06310682188770933
0.11791870367106105
0.76096244491257559
0.47224524357611664
0.37961522332372777
win@DESKTOP-MEIH88T:~/webdev-projects$ diff <(./cc-c 1) <(python3 -c 'import random; random.seed(1); [print(random.getrandbits(32)) for _ in range(5)]; [print("%.17g" % random.random()) for _ in range(5)]') && echo same
same
win@DESKTOP-MEIH88T:~/webdev-projects$  diff <(./cc-c 20261016) <(python3 -c 'import random; random.seed(20261016); [print(random.getrandbits(32)) for _ in range(5)]; [print("%.17g" % random.random()) for _ in range(5)]') && echo same
same
win@DESKTOP-MEIH88T:~/webdev-projects$  diff <(./cc-c 12345678901234) <(python3 -c 'import random; random.seed(12345678901234); [print(random.getrandbits(32)) for _ in range(5)]; [print("%.17g" % random.random()) for _ in range(5)]') && echo same
same
win@DESKTOP-MEIH88T:~/webdev-projects$  ./cc-c check            # the reference test: seed 5489, first output 3499211612
init_genrand(5489), first output: 3499211612  (should be 3499211612)

The C you just compiled computes the same numbers Python's random does for every seed you tried, about 150 lines in all.

Because every step is visible here, you can now see why I said earlier that it isn't safe for secrets. The four tempering lines in genrand_uint32 can each be undone. Collect 624 outputs in a row, untemper each one, and you have the entire mt[] state. From there, this same code predicts every number Python will produce next. That could be a later block if you want it: take 624 outputs from Python, rebuild the state in C, and print Python's next numbers before Python does.
```
