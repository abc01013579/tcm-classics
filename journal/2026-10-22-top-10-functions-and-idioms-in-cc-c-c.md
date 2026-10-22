---
title: top 10 functions and idioms  in cc-c.c
date: 2026-10-22
---

```c
Part 1: Top 10 functions
1. my_getline: read one line (cc-c.c:10009, retyped 37×)

int my_getline(char *s, int lim)
{
    int c = 0;
    char *p = s;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
        *p++ = c;
    if (c == '\n')
        *p++ = c;
    *p = '\0';
    return p - s;
}
int c = 0; gives c a starting value. If lim is 1, the loop never calls getchar, and the if (c == '\n') below would otherwise read garbage.

char *p = s; uses a second pointer to do the walking, so s keeps pointing at the start. That matters on the last line.

while (--lim > 0 && ...) tests three things in order, and && stops at the first false one:

--lim > 0: is there still room? It counts down first, so one slot is always left for '\0'.
(c = getchar()) != EOF: read a character and test it in the same expression.
c != '\n': stop at the end of the line.
Because the room check comes first, a full buffer never consumes a character it can't store.

*p++ = c; stores the character, then moves p forward.

if (c == '\n') *p++ = c; keeps the newline in the string, which is K&R's convention. A line therefore has length ≥ 1, so a return of 0 can only mean end of input.

*p = '\0'; terminates the string.

return p - s; subtracts two pointers into the same array, which gives the number of characters stored, so no strlen is needed.

2 & 3. getch / ungetch: one character of "undo" (cc-c.c:6478, 36× each)

char buf[BUFSIZE];      //buffer for ungetch
int bufp = 0;           //next free position in buf

int getch(void)
{
    return (bufp > 0) ? buf[--bufp] : getchar();
}

void ungetch(int c)
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters\n");
    else
        buf[bufp++] = c;
}
buf and bufp are external variables, so the two functions share them and their values last between calls. Together they make a stack: bufp is the next free slot.
getch: if something was pushed back (bufp > 0), it returns buf[--bufp]. That moves back one slot, then reads it. Otherwise it reads new input. The ?: makes the whole thing one expression.
ungetch: buf[bufp++] = c stores into the free slot, then advances. --bufp in getch and bufp++ here are exact mirror images, which is how every array stack in C is written. It's the same shape as push/pop (#9).
Why have them at all? Code like getword or getop can only tell a token has ended after reading one character too many. It hands that character back and treats the input as if it had never been read.
One catch: buf is char, so pushing back EOF (-1) is unreliable. In your exercise 4-9 version (cc-c.c:6776) you made it int buf[] for exactly this reason.
4. getword: next word or single character (cc-c.c:6450, 16×)

int getword(char *word, int lim)
{
    int c;
    char *w = word;

    while (isspace(c = getch()))
        ;
    if (c != EOF)
        *w++ = c;
    if (!isalpha(c)) {
        *w = '\0';
        return c;
    }
    for ( ; --lim > 0; w++)
        if (!isalnum(*w = getch())) {
            ungetch(*w);
            break;
        }
    *w = '\0';
    return word[0];
}
while (isspace(c = getch())) ; skips whitespace. The loop body is empty (the ; on its own line), because all the work happens in the test.
if (c != EOF) *w++ = c; stores the first non-space character, but never stores EOF as text.
if (!isalpha(c)) { ... return c; }: a word must start with a letter. Anything else (a digit, {, EOF) comes back as a one-character "word", and the function returns that character itself. The caller can then write while (getword(...) != EOF).
The for loop has no init part (( ; ...), because w is already set up. Each pass reads straight into *w, then tests it.
if (!isalnum(*w = getch())): when a character isn't a letter or digit, the word has ended. ungetch(*w) hands that character back for the next call, and break leaves the loop. The space it occupied in word gets overwritten by '\0' on the next line.
return word[0]; returns the first letter. This is non-zero, so it is never mistaken for EOF.
A subtle off-by-one worth checking yourself: trace lim = 3. You get one character before the loop, then two passes (--lim gives 2, then 1), then '\0', which makes 4 bytes in total. That's lim + 1. It's harmless with MAXWORD 100, but it's a real bound error in the book's code.
5. mystrdup: copy a string onto the heap (cc-c.c:6435, 16×)

char *mystrdup(char *s)
{
    char *p;

    p = (char *) malloc(strlen(s)+1);
    if (p != NULL)
        strcpy(p, s);
    return p;
}
strlen(s)+1: strlen doesn't count the '\0', but the copy needs it.
(char *) is a cast. In ANSI C, void * converts automatically, so the cast isn't needed. K&R2 writes it anyway, for C++ compatibility and older habits.
if (p != NULL) strcpy(...) only copies if malloc succeeded. Either way it returns p, so a NULL result passes the failure on to the caller.
Why it exists: getword reuses one word[] buffer every time. A tree node has to own its own copy, or every node would end up pointing at the same buffer.
6. addtree: recursive binary-tree insert (cc-c.c:7234, 8×)

struct tnode *addtree(struct tnode *p, char *w)
{
    int cond;

    if (p == NULL) {
        p = talloc();
        p->word = mystrdup(w);
        p->count = 1;
        p->left = p->right = NULL;
    } else if ((cond = strcmp(w, p->word)) == 0)
        p->count++;
    else if (cond < 0)
        p->left = addtree(p->left, w);
    else
        p->right = addtree(p->right, w);
    return p;
}
if (p == NULL) means you've reached an empty spot, and this is where the word belongs. talloc() creates the node, mystrdup gives it its own copy of the word, count = 1, and left = right = NULL (a chained assignment: both get NULL).
(cond = strcmp(w, p->word)) == 0 saves the comparison result and tests it at the same time, so strcmp isn't called twice.
== 0: the word is already in the tree, so just count it again.
< 0 means the word sorts before this node's word, so go left. Otherwise go right.
p->left = addtree(p->left, w); is the key trick. The recursive call returns the subtree root, which may be a new node, and the parent stores it in its own link. That's how a new node gets attached without passing a pointer to a pointer.
return p; returns this subtree's root, which may be the node just created. That's why the top-level call is root = addtree(root, word);.
7. my_qsort (+ swap): generic quicksort (cc-c.c:9948, 16×)

void my_qsort(void *v[], int left, int right,
              int (*comp)(void *, void *))
{
    int i, last;
    void swap(void *v[], int, int);

    if (left >= right)
        return;
    swap(v, left, (left + right)/2);
    last = left;
    for (i = left+1; i <= right; i++)
        if ((*comp)(v[i], v[left]) < 0)
            swap(v, ++last, i);
    swap(v, left, last);
    my_qsort(v, left, last-1, comp);
    my_qsort(v, last+1, right, comp);
}
void *v[] is an array of untyped pointers. The sort never touches the data, only rearranges the pointers to it. That's why one routine can sort strings or numbers.
int (*comp)(void *, void *): comp is a pointer to a function that compares two items. The parentheses are essential. Without them, int *comp(...) would declare a function that returns int *.
void swap(...) declared inside the function is legal, and the declaration is only visible inside my_qsort.
if (left >= right) return; is the base case: zero or one element is already sorted.
swap(v, left, (left+right)/2) moves the middle element to the front to act as the pivot. Taking it from the middle avoids the worst case on input that is already sorted.
last = left; marks where the "smaller than the pivot" region ends. Right now it's empty.
The loop goes through every other element. If v[i] sorts before the pivot, ++last grows the small region by one, and swap pulls v[i] into it.
swap(v, left, last) puts the pivot into its final position, between the two regions.
The two recursive calls sort each side. They skip last, because the pivot is already in place.
swap is the three-assignment rotation through a temporary: temp = v[i]; v[i] = v[j]; v[j] = temp;.

8. readlines: read lines into heap-free storage (cc-c.c:9982, 14×)

int readlines(char *lineptr[], int maxlines)
{
    int len, nlines;
    char *p, line[MAXLEN];

    nlines = 0;
    while ((len = my_getline(line, MAXLEN)) > 0)
        if (nlines >= maxlines || (p = alloc(len)) == NULL)
            return -1;
        else {
            line[len-1] = '\0';
            strcpy(p, line);
            lineptr[nlines++] = p;
        }
    return nlines;
}
line[MAXLEN] is a reused scratch buffer, the same idea as word[].
while ((len = my_getline(...)) > 0) reads until my_getline returns 0, which is EOF (see #1).
nlines >= maxlines || (p = alloc(len)) == NULL: if the array is full, || stops there and alloc is never called. If there is room, the second half tries to allocate and checks for failure in the same expression. Either failure returns -1.
line[len-1] = '\0' overwrites the newline. That shortens the string by one, so len bytes is exactly enough for the text plus '\0'. One flaw: if the last line of input has no '\n', its last real character gets cut off.
lineptr[nlines++] = p; stores the pointer, then counts it.
writelines is the matching output loop: printf("%s\n", lineptr[i]) puts back the newline that readlines removed.

9. alloc: the simplest allocator (cc-c.c:10026, 12×)

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
static at file level means these names are private to this file. No other file can touch the allocator's internals.
allocp = allocbuf: the array name used as a value is a pointer to element 0. So allocp starts at the beginning.
allocbuf + ALLOCSIZE - allocp is end minus current, which is the number of bytes left. Pointer subtraction again.
allocp += n; return allocp - n; moves the pointer past the block and returns where the block starts.
It's a "bump" allocator: memory can only be freed in reverse order (afree). It's the warm-up for the real malloc in #10.
10. push / pop: the calculator's stack (cc-c.c:5521, 13×)

int sp = 0;
double val[MAXVAL];

void push(double f)
{
    if (sp < MAXVAL)
        val[sp++] = f;
    else
        printf("error: stack full, can't push %g\n", f);
}

double pop(void)
{
    if (sp > 0)
        return val[--sp];
    else {
        printf("error: stack empty\n");
        return 0.0;
    }
}
This is the same shape as ungetch/getch, with double instead of char. sp always points one past the top. The bounds check comes first in both functions. On an empty stack, pop still has to return a double, so it returns 0.0 after printing the error.

Bonus (the summit): my_malloc / my_free (cc-c.c:979)
You've retyped this only 4×, but it's where chapters 5 and 6 come together. Here are the lines that matter:

union header { struct {...} s; Align x; }; The union is as large as its largest member, so each Header is sized and aligned like a long. x is never used; it only forces the alignment.
nunits = (nbytes+sizeof(Header)-1)/sizeof(Header) + 1; converts bytes to whole Header units, rounding up, plus one unit for the header itself.
if ((prevp = freep) == NULL) is true on the first call. base.s.ptr = freep = prevp = &base; then builds a one-node circular list: base points to itself.
for (p = prevp->s.ptr; ; prevp = p, p = p->s.ptr) has no test. It's an endless walk around the circle, and prevp trails one node behind p, so p can be unlinked.
Exact fit: prevp->s.ptr = p->s.ptr skips p, removing it from the list.
Too big: p->s.size -= nunits; p += p->s.size; shrinks the free block and jumps to its tail. p += counts in Headers, not bytes. The tail becomes the new block, which means the free block's own link never has to change.
return (void *)(p+1); The caller gets the space just after the header. The header stays hidden.
if (p == freep) means you've gone all the way around, so call morecore. That function calls sbrk and compares the result with (char *) -1, the system-call way of signalling failure. It then hands the new chunk to my_free, which reuses the insertion code instead of repeating it.
my_free:
bp = (Header *)ap - 1; steps back from the caller's pointer to the header.
The loop condition !(bp > p && bp < p->s.ptr) keeps walking until bp lies between two free blocks.
p >= p->s.ptr catches the wrap point, where the block at the highest address links back to the lowest.
The two ifs merge with the neighbouring free blocks: bp + bp->s.size == p->s.ptr means bp ends exactly where the next free block begins.
Part 2: Top 10 idioms (from your own //IDIOM: notes)
1. while ((c = getchar()) != EOF): the copy loop
The inner parentheses are required, because != binds tighter than =. Without them, c would get the 0/1 result of the comparison. c must be int, not char: getchar returns every byte value 0–255 plus -1, and a char can't hold 257 different values. The same shape works with any reader: getc(fp), getword, and read(fd, buf, n) > 0.

2. Assign-in-test for opening: if ((fp = fopen(name, "r")) == NULL)
Open and check in a single expression. Learn which failure value each family uses. stdio functions return NULL. System calls (open, read, sbrk) return -1, even sbrk, which returns a pointer, hence (char *) -1.

3. while (--argc > 0) f(*++argv): visit each argument
argv[0] is the program name. ++argv moves past it before use, and --argc counts down the remaining arguments. The flag version, while (--argc > 0 && (*++argv)[0] == '-'), followed by while ((c = *++argv[0])) inside, walks the letters of something like -nx. Here *++argv[0] advances the pointer inside the current string, not the list of strings.

4. The && / || guard
Evaluation stops at the first side that decides the answer, so the left side protects the right:

argc > 1 && argv[1][0] == '-' never reads argv[1] unless it exists.
i > 0 && line[i-1] == '\n' never indexes [-1].
np == NULL || strcmp(...) never passes NULL to strcmp.
This is a correctness tool, not just a speed-up.

5. malloc(strlen(s) + 1) + NULL check
The +1 is for the '\0'. A related form is sizeof *p: malloc(sizeof *np) takes the size from the pointer, not from a type name, so it stays correct if the type changes.

6. *p++ = c: store, then step
Postfix ++ binds tighter than *, but returns the old pointer. So the store goes to the current slot, and then p advances. Its sibling while ((c = *s++)) copies until '\0', because '\0' is 0, which is false. The double parentheses tell gcc that the = is deliberate.

7. Pointer minus pointer: p - s, bufp - buf, fp - my_iob
Two pointers into the same array subtract to give the number of elements between them, not bytes. my_getline uses it to return the length, alloc to measure the room left, and fp - my_iob to turn a FILE * into its slot number. Subtracting pointers into different arrays is undefined.

8. Bit flags: |=, &= ~, (x & M) == 0, (x >> i) & 1

x |= M turns bits on.
x &= ~M turns them off. ~M is all ones except M's bits, so & keeps everything else.
(x & M) == 0 asks "none of these bits are set". The parentheses are required, because == binds tighter than &. This is one of C's famous precedence traps.
(x >> i) & 1 reads bit i.
(flag & (A|B)) != A means "A set and B clear" in a single test, which is _fillbuf's check.
The flags themselves are powers of two (octal 01, 02, 04, 010…), so each one occupies its own bit.

9. (n + d - 1) / d: integer division that rounds up
Integer division normally truncates. Adding d - 1 first pushes any remainder over the next multiple. For example, 10 bytes in 8-byte units gives (10+7)/8 = 2, not 1. my_malloc uses this to count Header units, and you also used it for page and block counts.

10. Calling through a function pointer: (*comp)(a, b)
comp holds a function's address, *comp is that function, and (...) calls it. comp(a, b) also works in ANSI C, but K&R writes the * to make clear it's a pointer. This idiom lets my_qsort sort anything and lets dirwalk(dir, fsize) apply any action to every file. The caller passes the behaviour in as a value.

Runners-up
These also come up repeatedly in your notes:

The trailing pointer (prevp/p)
for (p = head; p != NULL; p = p->next)
Chained assignment: a = b = NULL
static locals that keep their value between calls
fprintf(stderr, ...) + exit(n)
(unsigned char) c before using a char as a table index
Most of these idioms show up again and again in the ten functions above. That repetition is what makes them idioms: K&R's whole book is built from about twenty patterns, used over and over.
```
