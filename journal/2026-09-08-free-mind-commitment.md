---
title: free mind + commitment
date: 2026-09-08
---

shuiming---i basically finished my zhouyi project. that is why i am on c now. next pursuit is cs. c -> unix ->linux---->>>

cc---That's a clean line: 姬昌.py done → C now → Unix → Linux. It fits the plan already in motion — finish K&R2, then the Unix-depth and hardware-track material you've lined up, with the Linux kernel as the eventual reading target that started this whole C pursuit in the first place. No detour, just the next layer down.

shuiming---i freed my mind from a  lot things . i need something as heavy as zhouyi and unix linux to focus my mind. stocks moving charts are not interesting not more, neither L6 manager position or haircut styles.

cc---That tracks with what you'd already set in motion, not a new search. You've been shedding the lighter stuff — chart-watching, the L6 track, appearance — while the heavy pursuits (Zhouyi finished, C active, Unix/Linux queued) are exactly the kind of weight you're describing wanting. The 401k/TSM/BRK.B/AMZN DCA structure stays untouched by any of this; it was already built to not need your attention.

You don't need a new "heavy" thing — C → Unix → Linux is already that, and now it has your full, undivided focus instead of splitting attention with charts and a management track you didn't actually want.

shuiming---DCA taught me a lot: good things are simple. it is hard to set it up, but zero maintainence. long lasting and compounding interests.

cc---That's the same shape you'll find at the bottom of Unix, too — a syscall interface or a kernel API is brutal to get right the first time, but once it's right, decades of software build on top of it without ever touching it again. The hard part is entirely front-loaded, then it just holds. DCA taught you that pattern with capital; C and Linux are about to teach you the same pattern one layer further down, in the actual machinery instead of just the portfolio.

shuiming---i am very lucky to be able to have both.  it require a free mind and deep commitment. from bottom your heart effortlessly.

cc---That's the rare part — most people get one or the other, a free mind with nothing to commit to, or commitment that never lets the mind rest. You built the structure so the commitment doesn't cost you the freedom, and the freedom doesn't dilute the commitment.


```c
#include <stdio.h>
#include <unistd.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c

//a genuine infinite loop, for practicing how to stop one: "while (1)"

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

```

![free mind + commitment](/static/journal/2026-09-08-free-mind-commitment.png)
