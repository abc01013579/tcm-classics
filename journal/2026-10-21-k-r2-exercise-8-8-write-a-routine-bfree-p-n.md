---
title: K&R2 Exercise 8-8. Write a routine bfree(p,n)
date: 2026-10-21
---

```c
#include <stdio.h>
#include <stdint.h>             //uintptr_t
#include <unistd.h>             //sbrk
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 Exercise 8-8. Write a routine bfree(p,n) that will free any
//arbitrary block p of n characters into the free list maintained by
//malloc and free. By using bfree, a user can add a static or external
//array to the free list at any time.
//
//The 8.7 allocator as the book has it, plus bfree. The trick: my_free
//doesn't care where a block came from, only that it has a header in
//front with the right size. morecore already uses it that way -- it
//writes a header at the start of the sbrk'd chunk and calls my_free.
//bfree does the same for any memory the caller hands it:
//  - round p up to a Header boundary (a header has to sit where one
//    of my_malloc's would)
//  - count the whole units that fit in what's left; the odd bytes at
//    either end are lost
//  - refuse if that isn't room for a header plus one unit
//  - write the size, set up the empty list if my_malloc never ran,
//    and my_free the block
//
//my_free keeps the list in address order, wrapping once, so a block
//below the heap (a static array) or above it (a local one) slots in
//like any other -- the "start or end of arena" test is what lets it.
//
//The 8-7 checks would refuse every bfree'd block: it isn't between
//heap_lo and heap_hi. bfree would have to widen that range, or the
//range test turn into a list of known regions. This block leaves
//them out, as 8-6 did.
//
//main:
//  1. bfree before any my_malloc: the list starts with the array
//  2. my_malloc serves from it -- the break doesn't move
//  3. ask for more than it holds: morecore, and both are on the list
//  4. free into it: the array's block grows back whole
//  5. a misaligned pointer: rounded up, the ends trimmed
//  6. too small to be worth a header: refused
//  7. two adjacent pieces of one array merge into one block

typedef long Align;             //for alignment to long boundary

union header {                  //block header
    struct {
        union header *ptr;      //next block if on free list
        unsigned size;          //size of this block, in Header units
    } s;
    Align x;                    //force alignment of blocks; never used
};

typedef union header Header;

static Header base;             //empty list to get started
static Header *freep = NULL;    //start of free list

static Header *morecore(unsigned);
void my_free(void *ap);

//my_malloc: general-purpose storage allocator
void *my_malloc(unsigned nbytes)
{
    Header *p, *prevp;
    unsigned nunits;

    nunits = (nbytes+sizeof(Header)-1)/sizeof(Header) + 1;
    if ((prevp = freep) == NULL) {      //no free list yet
        base.s.ptr = freep = prevp = &base;
        base.s.size = 0;
    }
    for (p = prevp->s.ptr; ; prevp = p, p = p->s.ptr) {
        if (p->s.size >= nunits) {      //big enough
            if (p->s.size == nunits)    //exactly
                prevp->s.ptr = p->s.ptr;
            else {                      //allocate tail end
                p->s.size -= nunits;
                p += p->s.size;
                p->s.size = nunits;
            }
            freep = prevp;
            return (void *)(p+1);
        }
        if (p == freep)                 //wrapped around free list
            if ((p = morecore(nunits)) == NULL)
                return NULL;            //none left
    }
}

#define NALLOC  1024                    //minimum #units to request

//morecore: ask system for more memory
static Header *morecore(unsigned nu)
{
    char *cp;
    Header *up;

    if (nu < NALLOC)
        nu = NALLOC;
    cp = sbrk(nu * sizeof(Header));
    if (cp == (char *) -1)              //no space at all
        return NULL;
    up = (Header *) cp;
    up->s.size = nu;
    my_free((void *)(up+1));
    return freep;
}

//my_free: put block ap in free list
void my_free(void *ap)
{
    Header *bp, *p;

    bp = (Header *)ap - 1;              //point to block header
    for (p = freep; !(bp > p && bp < p->s.ptr); p = p->s.ptr)
        if (p >= p->s.ptr && (bp > p || bp < p->s.ptr))
            break;  //freed block at start or end of arena

    if (bp + bp->s.size == p->s.ptr) {  //join to upper nbr
        bp->s.size += p->s.ptr->s.size;
        bp->s.ptr = p->s.ptr->s.ptr;
    } else
        bp->s.ptr = p->s.ptr;
    if (p + p->s.size == bp) {          //join to lower nbr
        p->s.size += bp->s.size;
        p->s.ptr = bp->s.ptr;
    } else
        p->s.ptr = bp;
    freep = p;
}

//bfree: put the n bytes at p on the free list; return the units added,
//0 if there was no room for a header and one unit
unsigned bfree(void *p, unsigned n)
{
    uintptr_t a, skip;
    unsigned nu;
    Header *hp;

    //IDIOM: round an address up to a multiple of k --
    //(a + k-1) / k * k; the difference is the bytes to skip
    a = (uintptr_t)p;
    skip = (a + _Alignof(Header) - 1) / _Alignof(Header) * _Alignof(Header) - a;
    //IDIOM: || guard against unsigned wrap -- n - skip is only computed
    //once n < skip is known false; otherwise it would wrap to a huge n
    if (n < skip || (n - skip) / sizeof(Header) < 2)
        return 0;
    nu = (n - skip) / sizeof(Header);   //whole units; the tail is lost
    hp = (Header *)(a + skip);
    hp->s.size = nu;
    if (freep == NULL) {                //no free list yet: as in my_malloc
        base.s.ptr = freep = &base;
        base.s.size = 0;
    }
    //IDIOM: reuse free to do the insert -- the same trick morecore
    //plays with sbrk's memory. nu is saved first: after my_free, hp may
    //be merged into its lower neighbour, its own size field stale
    my_free((void *)(hp+1));
    return nu;
}

static char pool[1024];                 //an external array to give away
static char *stk, *stk_end;             //main's local array, for where()

//where: which memory a block lives in. comparing pointers into
//different objects isn't promised by the standard; my_free does it
//on every call, and on a flat address space it just works
static const char *where(void *p)
{
    if ((char *)p >= pool && (char *)p < pool + sizeof pool)
        return "static pool";
    if ((char *)p >= stk && (char *)p < stk_end)
        return "main's stack";
    return "heap (sbrk)";
}

static void show(void)                  //free list, lowest address first
{
    Header *p, *lo;

    //IDIOM: find where a sorted ring wraps -- the one link that points
    //backwards goes from the highest block to the lowest
    for (p = &base; p->s.ptr > p; p = p->s.ptr)
        ;
    lo = p->s.ptr;
    //IDIOM: do-while to walk a ring once -- the body must run before
    //the "back to the start" test can mean anything
    p = lo;
    do {
        if (p != &base)                 //base is a 0-unit placeholder
            printf("   %p  %5u units  %s\n", (void *)p, p->s.size, where(p));
        p = p->s.ptr;
    } while (p != lo);
}

int main(void)
{
    char local[512];
    char *a, *b, *c;
    void *brk0;
    unsigned u;

    stk = local;
    stk_end = local + sizeof local;

    printf("1. bfree before any my_malloc: the array starts the list\n");
    u = bfree(pool, sizeof pool);
    printf("   bfree(pool, %zu) = %u units of %zu bytes\n",
           sizeof pool, u, sizeof(Header));
    show();

    printf("\n2. my_malloc serves from the array; the break doesn't move\n");
    brk0 = sbrk(0);
    a = my_malloc(100);
    b = my_malloc(200);
    printf("   a = my_malloc(100): %s\n", where(a));
    printf("   b = my_malloc(200): %s\n", where(b));
    printf("   sbrk(0) %s\n", sbrk(0) == brk0 ? "unchanged: no morecore"
                                              : "moved");
    show();

    printf("\n3. more than the pool has left: morecore, from sbrk\n");
    c = my_malloc(2000);
    printf("   c = my_malloc(2000): %s; sbrk(0) moved %ld bytes\n",
           where(c), (long)((char *)sbrk(0) - (char *)brk0));
    printf("   the static pool sits below the heap, so it comes first\n");
    show();

    printf("\n4. my_free(a), my_free(b): they were carved from the pool's\n"
           "   tail, so they merge back into its block\n");
    my_free(a);
    my_free(b);
    show();

    printf("\n5. a misaligned pointer: bfree(local + 3, 100)\n");
    u = bfree(local + 3, 100);
    printf("   local at %p; the header goes at the next multiple of %zu.\n"
           "   %u units = %zu bytes used of 100; the odd bytes at each end\n"
           "   are lost. the stack is above the heap, so it comes last\n",
           (void *)local, _Alignof(Header), u, u * sizeof(Header));
    show();

    printf("\n6. too small: bfree(local + 200, 20)\n");
    u = bfree(local + 200, 20);
    printf("   = %u: 20 bytes is a header and change, no unit to hand out\n",
           u);

    printf("\n7. two adjacent halves of one array merge\n");
    u = bfree(local + 256, 128);
    printf("   bfree(local + 256, 128) = %u units\n", u);
    u = bfree(local + 384, 128);
    printf("   bfree(local + 384, 128) = %u units\n", u);
    printf("   the second block's lower neighbour ends right where it\n"
           "   starts, so my_free joins them: one block of 16\n");
    show();

    printf("\n   a local array is safe here only because main's locals live\n"
           "   until exit. bfree a local of a function that returns, and\n"
           "   my_malloc will later hand out a dead stack frame\n");
    my_free(c);
    return 0;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
1. bfree before any my_malloc: the array starts the list
   bfree(pool, 1024) = 64 units of 16 bytes
   0x5f6fff6ab060     64 units  static pool

2. my_malloc serves from the array; the break doesn't move
   a = my_malloc(100): static pool
   b = my_malloc(200): static pool
   sbrk(0) unchanged: no morecore
   0x5f6fff6ab060     42 units  static pool

3. more than the pool has left: morecore, from sbrk
   c = my_malloc(2000): heap (sbrk); sbrk(0) moved 16384 bytes
   the static pool sits below the heap, so it comes first
   0x5f6fff6ab060     42 units  static pool
   0x5f703790d000    898 units  heap (sbrk)

4. my_free(a), my_free(b): they were carved from the pool's
   tail, so they merge back into its block
   0x5f6fff6ab060     64 units  static pool
   0x5f703790d000    898 units  heap (sbrk)

5. a misaligned pointer: bfree(local + 3, 100)
   local at 0x7ffce95d3d20; the header goes at the next multiple of 8.
   5 units = 80 bytes used of 100; the odd bytes at each end
   are lost. the stack is above the heap, so it comes last
   0x5f6fff6ab060     64 units  static pool
   0x5f703790d000    898 units  heap (sbrk)
   0x7ffce95d3d28      5 units  main's stack

6. too small: bfree(local + 200, 20)
   = 0: 20 bytes is a header and change, no unit to hand out

7. two adjacent halves of one array merge
   bfree(local + 256, 128) = 8 units
   bfree(local + 384, 128) = 8 units
   the second block's lower neighbour ends right where it
   starts, so my_free joins them: one block of 16
   0x5f6fff6ab060     64 units  static pool
   0x5f703790d000    898 units  heap (sbrk)
   0x7ffce95d3d28      5 units  main's stack
   0x7ffce95d3e20     16 units  main's stack

   a local array is safe here only because main's locals live
   until exit. bfree a local of a function that returns, and
   my_malloc will later hand out a dead stack frame
```
