---
title: learning pointer from deepseek
date: 2026-09-22
---

```c
win@DESKTOP-MEIH88T:~$ dsc
DeepSeek chat -- empty line, 'exit', or Ctrl-D to quit.

shuiming:  today's gain is using ds continuosely, we can go deeper on issues.

That’s a great insight. Using DeepSeek continuously turns the conversation into a thinking thread—you can keep refining, asking “why,” and challenging first answers, which helps move from surface-level symptoms to deeper root causes.

If you want, we can practice right now: pick an issue or topic, and we’ll go layer by layer until it’s clear.

shuiming:  pointer in c

Let’s use that method on pointers. We’ll go from the hardware up.

**Layer 0: What a pointer actually is**

Memory is a big array of bytes. Every object lives at some byte address.

```c
int x = 42;
```

`x` is a box somewhere in memory. `&x` is the address of that box.

A pointer is another box that stores that address:

```c
int *p = &x;
```

So `p` is not `42`. `p` is the location of `x`.

**Layer 1: Dereferencing**

```c
*p = 99;   // go to the address stored in p, write 99 there
```

Now `x` becomes `99`.

**Layer 2: Type matters**

`int *p` means:

1. `*p` reads/writes an `int` at that address.
2. `p + 1` advances by `sizeof(int)` bytes, not 1 byte.

That second point is where many pointer bugs start.

---

**First deep issue — arrays are not pointers**

This is one of the most misunderstood parts of C:

```c
int a[5];
int *p = a;          // OK: a decays to &a[0]

printf("%zu\n", sizeof a);   // 5 * sizeof(int)
printf("%zu\n", sizeof p);   // size of a pointer
```

`a` is an array. `p` is a pointer. They are different objects, but in most expressions `a` decays into a pointer to its first element.

---

Tell me which direction you want to go deeper:

- **A:** Pointer arithmetic and array decay
- **B:** Pointers to pointers and dynamic memory
- **C:** Function pointers and callbacks
- **D:** Undefined behavior, aliasing, `const`, `restrict`
- **E:** What happens at the assembly/memory level

Which one?

shuiming:  pointer arrays and pointers to pointers

Let’s go deeper on **pointer arrays** (arrays of pointers) and **pointers to pointers**.

We’ll peel this onion layer by layer, from raw memory layout to common traps.

---

## Layer 0 – Definitions

### Pointer array (array of pointers)

```c
int *p[5];   // array of 5 elements, each element is an int*
```

`p` is an array. Each element `p[i]` is a pointer to an `int`.
The array itself occupies `5 * sizeof(int*)` bytes of memory.

### Pointer to pointer

```c
int **pp;    // pointer to a pointer to int
```

`pp` is a single variable that can hold the address of a pointer to `int`.
It occupies `sizeof(int**)` bytes (same as any pointer).

**Key difference:**

- `p` is an array object (not a pointer variable).
- `pp` is a pointer variable.

But in **most expressions**, the array `p` *decays* to a pointer to its first element.
The first element of `p` is of type `int*`, so decayed `p` has type `int **`.

So:

```c
int *p[5];
int **pp = p;   // valid! p decays to &p[0], type int**
```

This is the first deep link: **an array of pointers is often manipulated through a pointer-to-pointer.**

---

## Layer 1 – Memory layout

Let’s visualize.

### Array of pointers

```c
int a = 1, b = 2, c = 3;
int *arr[3] = { &a, &b, &c };
```

Memory:

```
arr (array of 3 pointer slots):
+--------+--------+--------+
|  0x100 |  0x104 |  0x108 |   <- addresses of a, b, c
+--------+--------+--------+
   |        |        |
   v        v        v
   a=1      b=2      c=3
```

`arr` itself is a contiguous block of 3 pointer-sized cells.
The integers they point to are **not necessarily contiguous**.

### Pointer to pointer

```c
int x = 10;
int *px = &x;
int **ppx = &px;
```

Memory:

```
ppx (variable)  ->  px (variable)  ->  x
+--------+          +--------+        +----+
| 0x200  |  ----->  | 0x300  | -----> | 10 |
+--------+          +--------+        +----+
```

`ppx` holds the address of `px`.
`*ppx` gives `px`.
`**ppx` gives `x`.

---

## Layer 2 – Why use double pointers?

The most common reason: **to let a function modify a pointer variable** (not just what it points to).

### Example: allocate memory inside a function

```c
void allocate(int **pp) {
    *pp = malloc(10 * sizeof(int));
}

int *ptr = NULL;
allocate(&ptr);
// ptr now points to allocated block
```

Without the double pointer, `malloc`’s result would be lost because C passes arguments by value.

The same pattern appears when you want a function to change a `char*` string:

```c
void make_string(char **s) {
    *s = malloc(6);
    strcpy(*s, "hello");
}
```

---

## Layer 3 – Dynamic array of strings (the `argv` pattern)

In `main(int argc, char **argv)`:

- `argv` is a pointer to `char*` (i.e., `char **`).
- But conceptually, it represents an **array of pointers to strings**.

Memory for `argv[3]`:

```
argv (char**)
   |
   v
+---------+    +---------+    +---------+
| char*   | -> | char*   | -> | char*   |
| 0x700   |    | 0x800   |    | 0x900   |
+---------+    +---------+    +---------+
   |                |                |
   v                v                v
 "program"        "arg1"           "arg2"
```

`argv` can also be written as `char *argv[]` in the parameter list, but in a function parameter it **decays** to `char **argv`.

The same pattern is used when you build a **dynamic array of strings**:

```c
char **lines = malloc(n * sizeof(char*));
for (int i = 0; i < n; i++)
    lines[i] = malloc(max_len);
```

Here `lines` is a pointer to pointer, but it points to the first element of an allocated block of `n` pointers, each pointing to a separate allocated string.

---

## Layer 4 – Deep trap: 2D arrays are NOT `int**`

This is where many C programmers get confused.

```c
int a[3][4];   // 2D array: one contiguous block of 12 ints
int **p = a;   // ERROR: incompatible pointer type
```

Why?
`a` decays to a pointer to its first element.
The first element of `a` is an **array of 4 ints** (`int[4]`).
So the decayed type is `int (*)[4]` (pointer to array of 4 ints), not `int**`.

### Memory layout of `int a[2][3]`:

```
a (contiguous):
+---+---+---+
| 0 | 1 | 2 |   <- row 0
+---+---+---+
| 3 | 4 | 5 |   <- row 1
+---+---+---+
```

No intermediate array of pointers exists.
Access `a[i][j]` works by arithmetic: `*(*(a + i) + j)`.

### The correct pointer type for a 2D array:

```c
int (*p)[3] = a;   // p points to an array of 3 ints
```

Now `p+1` jumps by one whole row (3 ints), not by one pointer.

If you want a function that accepts a 2D array with a fixed column count, use:

```c
void func(int rows, int cols, int a[][cols])  // C99
```

or

```c
void func(int a[][10])   // fixed second dimension
```

But never `int **a`.

---

## Layer 5 – Simulating a 2D array with `int**`

You **can** create a structure that **looks like** a 2D array using pointers-to-pointers:

```c
int rows = 3, cols = 4;
int **mat = malloc(rows * sizeof *mat);
for (int i = 0; i < rows; i++)
    mat[i] = malloc(cols * sizeof *mat[i]);
```

Now `mat[i][j]` works.
But the memory layout is **jagged**, not contiguous:

```
mat (int**)
  |
  v
+--------+    row0: [ ][ ][ ][ ]
| mat[0] |--->  +--+--+--+--+
| mat[1] |--->  +--+--+--+--+
| mat[2] |--->  +--+--+--+--+
+--------+
```

This is useful when each row may have a different length (ragged array).
But it is **not interchangeable** with a true contiguous 2D array.

---

## Layer 6 – Pointer arithmetic on `int**`

Given:

```c
int **pp = ...;
pp + 1   // advances by sizeof(int*) bytes, i.e., to the next pointer in the block
*pp + 1  // dereference pp -> int*, then add 1 int (advance by sizeof(int))
**pp + 1 // dereference twice -> int, then add 1 (value arithmetic)
```

This triple meaning of `+1` is a common source of bugs.

Example:

```c
int a[] = {10, 20, 30};
int *p = a;          // p points to a[0]
int **pp = &p;

printf("%d\n", **pp);   // 10
printf("%d\n", *(*pp + 1)); // 20  (p+1 points to a[1])
printf("%d\n", *(*(pp+1))); // undefined if pp points to a single pointer, not an array
```

The last line tries to access the next `int*` after `p` in memory — dangerous if there is no array of pointers.

---

## Layer 7 – Complex declarations

Reading `int *(*fp)(int)` etc. can be hard.
Practice with the **spiral rule** or **right-left rule**.

For our topic:

- `int *arr[5]` → array of 5 pointers to int.
- `int (*arr)[5]` → pointer to an array of 5 ints.
- `int **pp` → pointer to pointer to int.
- `int *(*pp)[5]` → pointer to an array of 5 pointers to int.

These distinctions matter when passing to functions or allocating.

---

## Common mistakes with pointers-to-pointers

1. **Forgetting to allocate the pointer array before allocating rows.**
   ```c
   int **mat;          // uninitialized
   mat[0] = malloc(10 * sizeof(int)); // CRASH
   ```
2. **Confusing `int**` with 2D array** (already covered).
3. **Memory leaks:** not freeing row pointers before freeing the array of pointers.
   ```c
   for (int i = 0; i < rows; i++)
       free(mat[i]);
   free(mat);
   ```
4. **Dangling pointers:** storing the address of a local variable in a double pointer.
5. **Wrong level of indirection in `scanf`:**
   ```c
   int x;
   int *px = &x;
   scanf("%d", px);   // OK: px is int*
   scanf("%d", &px);  // WRONG: &px is int**, expected int*
   ```

---

## Where to go deeper next?

We can go further into:

- **A:** `const` with pointers-to-pointers (`const int **` vs `int **` are incompatible)
- **B:** Function pointers and arrays of function pointers
- **C:** Building a dynamic 2D array that is contiguous but accessible as `a[i][j]`
- **D:** How the CPU/assembly handles multi-level indirection
- **E:** The strict aliasing rule and why `int**` and `float**` don't mix

Which layer do you want to peel next?

```
