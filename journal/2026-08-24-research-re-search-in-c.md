---
title: research = re + search : in c
date: 2026-08-24
---

```c
#include <stdio.h>
#include <string.h>

int search(const char *haystack, const char *needle) {
    return strstr(haystack, needle) != NULL;
}

void research(const char *haystack, const char *needle) {
    int attempt = 0;
    while (!search(haystack, needle)) {
        attempt++;
        printf("attempt %d: not found. searching again.\n", attempt);
        // in real research, the haystack changes between attempts
    }
    printf("found after %d retries.\n", attempt);
}


Result research(Question q, Knowledge k) {
    Result r = search(q, k);

    if (r.conclusive)
        return r;

    // the search changed both the question and what you know
    return research(refine(q, r), update(k, r));
}



```
