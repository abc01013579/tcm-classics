---
title: char *alloc(int n)
date: 2026-09-29
---

```c
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
```

allocbuf:  [ used | used | used | free | free | free | free | ... ]
                                    ↑
                                  allocp   (the next free byte)

Line by line

static char allocbuf[ALLOCSIZE];
The shelf: one array of ALLOCSIZE bytes (1,000,000 in your sort program). All memory alloc ever hands out comes from here.

static char *allocp = allocbuf;
The marker: a pointer to the next free byte. It starts at allocbuf, meaning the array's first byte, because an array name used as a value is the address of its first element. At the start, everything is free.

What static does here. Outside any function, static means private to this file. Other .c files can't see allocbuf or allocp, so nothing else can mess with the marker. Only alloc (and its partner afree in the book) touch them. They also exist for the whole run of the program, not just during one function call.

char *alloc(int n)
It returns a char *, the address of the space it gives you.

if (allocbuf + ALLOCSIZE - allocp >= n) {
"Is there room for n more bytes?" It's two pointer steps:

allocbuf + ALLOCSIZE is the address just past the end of the shelf.
Subtracting allocp gives how many bytes are left: end minus marker. Subtracting two pointers into the same array gives the number of elements between them, the same trick as p - s in my_getline.
So the test reads: "bytes left ≥ bytes wanted?"

allocp += n;
return allocp - n;
Give the space, and move the marker. The marker moves forward n bytes first. Then allocp - n computes where it was, which is the start of the block being handed out. (The same thing written in two steps would be char *p = allocp; allocp += n; return p;.)

} else
    return NULL;
Not enough room: return NULL, the pointer to nothing. Callers must check for it, as readlines does with (p = alloc(len)) == NULL, and that's where the sort program's "input too big to sort" comes from.
