---
title: 6.7 typedef example
date: 2026-10-13
---

```c
#include <stdio.h>
#include <ctype.h>      //for isalpha(), isalnum(), isspace()
#include <string.h>     //for strcmp(), strlen(), strcpy()
#include <stdlib.h>     //for malloc()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'the cat and the hat\n' | ./cc-c                         # 1 and, 1 cat, 1 hat, 2 the
//         or:  ./cc-c < cc-c.c | sort -rn | head -5                           # the 5 most frequent words in this file

//K&R2 section 6.7: typedef -- the 6.5 word-count tree again, rewritten
//with the two type names the book defines on p.146-147:
//
//  typedef struct tnode *Treeptr;      Treeptr  = struct tnode *
//  typedef struct tnode { ... } Treenode;     Treenode = struct tnode
//
//The rule: a typedef reads exactly like a variable declaration. Drop
//the word typedef and "struct tnode *Treeptr;" would declare a pointer
//VARIABLE named Treeptr. With typedef in front, Treeptr becomes the
//NAME of that pointer type instead.
//
//Notice the order: Treeptr is defined FIRST, before struct tnode has
//any members. That's legal -- a pointer to a struct that isn't finished
//yet (an "incomplete type") is fine, because every struct pointer is
//the same size no matter what it points to. So inside the struct the
//children can already be written as Treeptr. The book still writes
//"struct tnode *left" there; this block uses Treeptr to show it works.
//
//Compare this block with the 6.5 one further down: the program is
//line-for-line the same, only the type names changed. typedef makes NO
//new type -- Treeptr and struct tnode * are the same type to the
//compiler, so they mix freely. main proves it before counting words:
//it assigns one to the other and compares the sizeof of each.
#define MAXWORD 100

typedef struct tnode *Treeptr;

typedef struct tnode {      //the tree node:
    char *word;             //points to the text
    int count;              //number of occurrences
    Treeptr left;           //left child
    Treeptr right;          //right child
} Treenode;

Treeptr addtree(Treeptr, char *);
void treeprint(Treeptr);
int getword(char *, int);

//word frequency count
int main(void)
{
    Treeptr root;
    char word[MAXWORD];
    struct tnode *plain;

    //same type, two spellings: no cast, no warning
    plain = NULL;
    root = plain;
    fprintf(stderr, "sizeof(Treenode) = %zu, sizeof(struct tnode) = %zu\n",
            sizeof(Treenode), sizeof(struct tnode));
    fprintf(stderr, "sizeof(Treeptr)  = %zu, sizeof(struct tnode *) = %zu\n\n",
            sizeof(Treeptr), sizeof(struct tnode *));

    //IDIOM: while ((x = get()) != EOF) -- read, test for end, loop, all in one line
    while (getword(word, MAXWORD) != EOF)
        if (isalpha(word[0]))
            //IDIOM: p = addtree(p, w) -- the recursive function returns the
            //(possibly new) subtree root, and the caller stores it back
            root = addtree(root, word);
    treeprint(root);
    return 0;
}

Treeptr talloc(void);
char *mystrdup(char *);

//addtree:  add a node with w, at or below p
Treeptr addtree(Treeptr p, char *w)
{
    int cond;

    if (p == NULL) {        //a new word has arrived
        p = talloc();       //make a new node
        p->word = mystrdup(w);
        p->count = 1;
        //IDIOM: a = b = NULL -- assignment is an expression, so it chains right to left
        p->left = p->right = NULL;
    //IDIOM: assign-in-test -- save strcmp's result AND test it, so the
    //following else-ifs reuse cond instead of calling strcmp again
    } else if ((cond = strcmp(w, p->word)) == 0)
        p->count++;         //repeated word
    else if (cond < 0)      //less than into left subtree
        p->left = addtree(p->left, w);
    else                    //greater than into right subtree
        p->right = addtree(p->right, w);
    return p;
}

//treeprint:  in-order print of tree p
void treeprint(Treeptr p)
{
    if (p != NULL) {
        treeprint(p->left);
        printf("%4d %s\n", p->count, p->word);
        treeprint(p->right);
    }
}

//talloc:  make a tnode -- the book's typedef version (p.147)
Treeptr talloc(void)
{
    //IDIOM: (T *) malloc(sizeof(T)) -- the typedef names read as plain
    //English here: "make room for one Treenode, hand back a Treeptr"
    return (Treeptr) malloc(sizeof(Treenode));
}

//mystrdup:  make a duplicate of s (the book's strdup)
char *mystrdup(char *s)
{
    char *p;

    //IDIOM: strlen(s)+1 -- strlen doesn't count the '\0', the copy needs it
    p = (char *) malloc(strlen(s)+1);
    if (p != NULL)
        strcpy(p, s);
    return p;
}

int getch(void);
void ungetch(int);

//getword:  get next word or character from input
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

#define BUFSIZE 100

char buf[BUFSIZE];      //buffer for ungetch
int bufp = 0;           //next free position in buf

//getch:  get a (possibly pushed back) character
int getch(void)
{
    //IDIOM: (n > 0) ? buf[--n] : getchar() -- take a pushed-back char first, else read a new one
    return (bufp > 0) ? buf[--bufp] : getchar();
}

//ungetch:  push character back on input
void ungetch(int c)
{
    if (bufp >= BUFSIZE)
        printf("ungetch: too many characters\n");
    else
        buf[bufp++] = c;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$  printf 'the cat and the hat\n' | ./cc-c
sizeof(Treenode) = 32, sizeof(struct tnode) = 32
sizeof(Treeptr)  = 8, sizeof(struct tnode *) = 8

   1 and
   1 cat
   1 hat
   2 the
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c < cc-c.c | sort -rn | head -5
sizeof(Treenode) = 32, sizeof(struct tnode) = 32
sizeof(Treeptr)  = 8, sizeof(struct tnode *) = 8

1350 int
1220 c
1198 the
1188 s
1175 n
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c < cc-c.c 2>/dev/null | sort -rn | head -5
1350 int
1220 c
1198 the
1188 s
1175 n

cc-c.c, active block (lines 1–172)
Lines 5–31 are the comment header, so this walk-through starts at the code.

Headers and constants (1–4, 32)

#include <stdio.h>      // printf, fprintf, getchar, EOF, stderr
#include <ctype.h>      // isalpha, isalnum, isspace
#include <string.h>     // strcmp, strlen, strcpy
#include <stdlib.h>     // malloc, and NULL
#define MAXWORD 100
#include pastes the header's declarations in, so the compiler knows each function's argument and return types before you call it. MAXWORD is the size of the buffer that holds one word. Your 6-6 program does exactly this kind of substitution: every MAXWORD becomes the text 100 before the compiler runs.

The types (34–41)

typedef struct tnode *Treeptr;
Remove typedef and this line would declare a pointer variable named Treeptr. With typedef, Treeptr becomes the name of the type "pointer to struct tnode". At this point struct tnode has no members yet. The compiler accepts that because it only needs to know a pointer's size (8 bytes), not what the pointer points to.


typedef struct tnode {
    char *word;       // pointer to the word's characters, stored elsewhere (by mystrdup)
    int count;        // how many times the word has been seen
    Treeptr left;     // subtree of words that sort before this one
    Treeptr right;    // subtree of words that sort after this one
} Treenode;
This line does two jobs. It completes struct tnode by giving it members, and it names the finished struct Treenode. The struct holds a pointer to its own kind, not a copy of itself. A struct containing itself would be infinitely large, but a pointer is always 8 bytes.

You saw sizeof(Treenode) = 32 in the output: word is 8 bytes, count is 4, then 4 bytes of padding, then left and right are 8 each. The padding is there because x86-64 wants each 8-byte pointer to start at an address divisible by 8. Without it, left would start at byte 12.

Prototypes (43–45)

Treeptr addtree(Treeptr, char *);
void treeprint(Treeptr);
int getword(char *, int);
main calls these before their definitions appear, so the compiler needs their types in advance. A prototype is enough for that, and parameter names are optional in one. talloc/mystrdup (72–73) and getch/ungetch (127–128) are declared the same way, just before the first function that uses them.

main (48–70)

Treeptr root;            // the whole tree is reached through this one pointer
char word[MAXWORD];      // getword writes each word in here
struct tnode *plain;
root is the only variable that holds the tree. Every node can be reached from it by following left and right pointers.


plain = NULL;
root = plain;
This is the typedef demonstration. It assigns a struct tnode * to a Treeptr with no cast, and the compiler gives no warning because they're the same type. It also sets root to NULL, which means the tree starts empty.


fprintf(stderr, "... %zu ...", sizeof(Treenode), sizeof(struct tnode));
fprintf(stderr, ...) is printf aimed at the error stream. That's why these lines skipped sort in your test. sizeof produces a size_t, and %zu is the matching format: z means size_t-sized and u means unsigned. Using %d for it would be a type mismatch, and -Wall would warn.


while (getword(word, MAXWORD) != EOF)
    if (isalpha(word[0]))
        root = addtree(root, word);
treeprint(root);
getword returns either a word or a single non-word character such as ( or ;. The isalpha(word[0]) test keeps only the words. root = addtree(root, word) stores the return value because, on the very first word, root is NULL and addtree creates the root node. The caller can only find that new node through the returned pointer. After that first call addtree returns the same root every time, so the assignment changes nothing.

addtree (76–95): the core of the program

if (p == NULL) {
    p = talloc();
    p->word = mystrdup(w);
    p->count = 1;
    p->left = p->right = NULL;
}
Reaching a NULL means the search walked off the bottom of the tree without finding the word, so the word is new. This branch builds a node right there.

p->word is shorthand for (*p).word.
mystrdup(w) matters because w points into main's word buffer, which the next getword call overwrites. The node needs its own copy.
a = b = NULL works because assignment is an expression. It evaluates right to left: p->right = NULL yields NULL, and that value is assigned to p->left.

} else if ((cond = strcmp(w, p->word)) == 0)
    p->count++;
else if (cond < 0)
    p->left = addtree(p->left, w);
else
    p->right = addtree(p->right, w);
return p;
strcmp returns 0 if the strings are equal, a negative number if w sorts first, and a positive number if it sorts later. Saving the result in cond lets the next test reuse it without calling strcmp again. A smaller word recurses left and a larger one recurses right. Storing the result back in p->left or p->right is the same pattern as in main: if that child was NULL, the recursive call creates a node, and this assignment is what attaches it to the tree.

Here is a trace of the cat and the hat:

word	path	result
the	root is NULL	creates root the
cat	cat < the → left is NULL	creates the.left = cat
and	and < the → left; and < cat → left is NULL	creates cat.left = and
the	strcmp == 0 at root	the.count = 2
hat	hat < the → left; hat > cat → right is NULL	creates cat.right = hat
treeprint (98–105)

if (p != NULL) {
    treeprint(p->left);
    printf("%4d %s\n", p->count, p->word);
    treeprint(p->right);
}
This prints everything smaller (the left subtree), then the current node, then everything larger (the right subtree). Applied recursively, the whole tree comes out in alphabetical order. This is called an in-order traversal. p != NULL is the base case that stops the recursion. %4d right-aligns the count in a 4-character column, which is why the output lines up.

talloc (108–113)

return (Treeptr) malloc(sizeof(Treenode));
malloc returns a void *, which is a raw address with no type attached. The cast labels it as a Treeptr. In standard C the cast is optional, because void * converts to any object pointer automatically. K&R writes it anyway as documentation. The code doesn't check whether malloc returned NULL, which the book also skips.

mystrdup (116–125)

p = (char *) malloc(strlen(s)+1);
if (p != NULL)
    strcpy(p, s);
return p;
This allocates exactly enough bytes for the string. strlen doesn't count the terminating '\0', so the +1 makes room for it. Then it copies the string in. It's named mystrdup because <string.h> already declares a standard strdup, and defining a second function with that name would clash.

getword (131–151)

while (isspace(c = getch()))
    ;
This skips whitespace. All the work happens in the loop's condition, so the body is an empty statement (;).


if (c != EOF)
    *w++ = c;
if (!isalpha(c)) {
    *w = '\0';
    return c;
}
It stores the first character. *w++ = c stores c at w and then advances w, because postfix ++ binds to w, not to *w. If that first character isn't a letter, the "word" is just that one character, such as \, and it's returned on its own. That's how the \ in \n gets separated from the n.


for ( ; --lim > 0; w++)
    if (!isalnum(*w = getch())) {
        ungetch(*w);
        break;
    }
*w = '\0';
return word[0];
This reads letters and digits until something else shows up. --lim counts down the space left in the buffer so the loop can't write past MAXWORD. The character that ended the word belongs to whatever comes next, so ungetch pushes it back to be read again. The function returns word[0], a letter, which tells main "this was a word".

getch / ungetch (153–172)

char buf[BUFSIZE];
int bufp = 0;
These are globals, so both functions share them. buf is a small stack of characters that have been pushed back. bufp points to the next free slot in it.


return (bufp > 0) ? buf[--bufp] : getchar();
If there's a pushed-back character, take it from the stack (pre-decrement first, then read). Otherwise read a new character from stdin.


if (bufp >= BUFSIZE) printf("ungetch: too many characters\n");
else buf[bufp++] = c;
This pushes a character back, storing it first and then advancing bufp, unless the stack is full. getch decrements before reading and ungetch increments after writing, so the two functions mirror each other exactly. That pairing is the standard C idiom for an array used as a stack.

Line 174 onward is the archived 6-6 block, inside /* */, so the compiler ignores it.

```
