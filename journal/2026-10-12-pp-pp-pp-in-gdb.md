---
title: pp *pp **pp in gdb
date: 2026-10-12
---

```c
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

delete
b undef
run
n
p pp
p *pp
p **pp


Breakpoint 6, undef (name=0x55555555600a "IN") at cc-c.c:79
79          for (pp = &hashtab[hash(name)]; *pp != NULL; pp = &(*pp)->next)
(gdb) n
80              if (strcmp(name, (*pp)->name) == 0) {
(gdb) p pp
$3 = (struct nlist **) 0x5555555580d0 <hashtab+144>
(gdb) p *pp
$4 = (struct nlist *) 0x5555555590d0
(gdb) p **pp
$5 = {next = 0x555555559010, name = 0x5555555590f0 "Hm", defn = 0x555555559110 "oops"}
(gdb) p &(*pp)->next
$6 = (struct nlist **) 0x5555555590d0
```
they are all numbers.
