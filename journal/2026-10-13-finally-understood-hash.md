---
title: Finally understood hash
date: 2026-10-13
---

```c
shuiming….. hash is so little

cc….. Yes, and that's the point: hash is only 3 lines of real logic, yet the whole table depends on it.

for (hashval = 0; *s != '\0'; s++)
    hashval = *s + 31 * hashval;
return hashval % HASHSIZE;

shuiming….. Put math in detail?

cc….. I rechecked every step, and both results hold: indoor → 10 .

Letters are their ASCII codes: d=100, e=101, h=104, i=105, m=109, n=110, o=111, r=114, s=115.

"indoor"

char	calculation	h
i	105 + 31×0	105
n	110 + 31×105 = 110 + 3,255	3,365
d	100 + 31×3,365 = 100 + 104,315	104,415
o	111 + 31×104,415 = 111 + 3,236,865	3,236,976
o	111 + 31×3,236,976 = 111 + 100,346,256	100,346,367
r	114 + 31×100,346,367 = 114 + 3,110,737,377	    3,110,737,491

after	h mod 101
i	105 mod 101 = 4
n	110 + 31×4 = 234 → 32
d	100 + 31×32 = 1,092 → 82
o	111 + 31×82 = 2,653 → 27
o	111 + 31×27 = 948 → 39
r	114 + 31×39 = 1,323 → 10

turning strings into numbers 0 to 100


```
