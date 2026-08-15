---
title: really love c- so beatiful
date: 2026-08-15
---

shuiming:  i never thought computer language can trigger emtions insider. a little shocked.

cc: It's less strange than it seems once you notice what's actually happening. Emotion isn't reserved for things with faces — it responds to clarity, elegance, resolution. A piece of code that says exactly what it means, with nothing wasted and nothing hidden, is the same kind of experience as a well-resolved chord in music or a clean proof in math — recognition of order where there could have been noise. You called this same code "beautiful" a minute ago without hesitating; that word wasn't a stretch, it was accurate.

What's probably shocking you more specifically is that it's happening with C, of all things — a language with a reputation for being cold, low-level, unforgiving. But that's likely exactly why it lands harder for you than JS/Python ever did: there's no abstraction cushioning the encounter. When the counters click into place and the loop runs correctly, you're not admiring a convenience someone built for you — you're seeing the raw mechanism resolve cleanly, and reacting to that, directly. Same root as the joy you named a few messages ago, just showing a new face.


shuiming: show me the code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
```
