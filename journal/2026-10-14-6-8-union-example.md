---
title: 6.8 union example
date: 2026-10-14
---

```c
#include <stdio.h>
#include <stddef.h>     //for offsetof()
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 section 6.8: unions -- the book's symbol-table constant that may
//be an int, a float, or a character pointer.
//
//A union is declared exactly like a struct, but where a struct lays its
//members out one AFTER another, a union puts them all ON TOP of each
//other: every member starts at offset 0, and the union is as big as its
//widest member. It holds ONE value at a time; storing into one member
//overwrites the others.
//
//The union itself doesn't remember which member was stored last -- that
//is the programmer's job, here done by a separate int "utype" next to
//it (a "tagged union"). main shows, in order:
//
//  1. sizes and offsets: union size = largest member, all offsets 0
//  2. the book's print code, run as printed -- it has a dangling-else
//     bug: an INT or FLOAT also prints "bad type" (see bookprint)
//  3. the fixed version with an else-if chain
//  4. storing a float and reading it back as an int (the "results are
//     implementation-dependent" case the book warns about)
//  5. the book's symtab[] array: a union inside a struct inside an array
#define NSYM 3

enum { INT, FLOAT, STRING };    //the values utype can hold

union u_tag {
    int ival;
    float fval;
    char *sval;
};

struct {                        //no tag: symtab is the only variable of this type
    char *name;
    int flags;
    int utype;
    union {                     //no tag either: reached only as .u
        int ival;
        float fval;
        char *sval;
    } u;
} symtab[NSYM];

void bookprint(union u_tag, int);
void fixedprint(union u_tag, int);

int main(void)
{
    //a union may only be initialized with a value for its FIRST member,
    //so { 42 } goes into ival
    union u_tag u = { 42 };
    union u_tag v;
    int utype = INT;
    int i;

    //1. size and layout
    printf("sizeof: int %zu, float %zu, char * %zu  ->  union u_tag %zu\n",
            sizeof(int), sizeof(float), sizeof(char *), sizeof(union u_tag));
    //IDIOM: offsetof(type, member) -- byte distance from the start of a
    //struct or union to that member; for a union it is always 0
    printf("offsetof: ival %zu, fval %zu, sval %zu\n",
            offsetof(union u_tag, ival), offsetof(union u_tag, fval),
            offsetof(union u_tag, sval));
    printf("addresses: &u %p, &u.ival %p, &u.fval %p, &u.sval %p\n\n",
            (void *) &u, (void *) &u.ival, (void *) &u.fval, (void *) &u.sval);

    //2. and 3. the book's printing code vs the fixed one, one type at a time
    printf("--- u holds an int (utype = INT) ---\n");
    bookprint(u, utype);
    fixedprint(u, utype);

    u.fval = 3.14;
    utype = FLOAT;
    printf("--- u holds a float (utype = FLOAT) ---\n");
    bookprint(u, utype);
    fixedprint(u, utype);

    u.sval = "hello";
    utype = STRING;
    printf("--- u holds a string (utype = STRING) ---\n");
    bookprint(u, utype);
    fixedprint(u, utype);

    //4. store as one type, extract as another
    u.fval = 1.0;
    printf("\n--- stored u.fval = 1.0, read back u.ival ---\n");
    printf("u.ival = %d  (0x%08x): the raw IEEE-754 bits of 1.0f, not 1\n\n",
            u.ival, (unsigned) u.ival);

    //a union copies as a unit, like a struct
    v = u;
    printf("--- v = u copies the whole union: v.fval = %f ---\n\n", v.fval);

    //5. the symbol table: union inside a struct inside an array
    symtab[0].name = "MAXLINE";
    symtab[0].utype = INT;
    symtab[0].u.ival = 1000;
    symtab[1].name = "PI";
    symtab[1].utype = FLOAT;
    symtab[1].u.fval = 3.14159;
    symtab[2].name = "GREETING";
    symtab[2].utype = STRING;
    symtab[2].u.sval = "hello, world";

    printf("sizeof(symtab[0]) = %zu, sizeof(symtab[0].u) = %zu\n",
            sizeof(symtab[0]), sizeof(symtab[0].u));
    for (i = 0; i < NSYM; i++) {
        printf("symtab[%d] %-8s = ", i, symtab[i].name);
        //IDIOM: switch on the tag -- the tag says which union member is live
        switch (symtab[i].utype) {
        case INT:
            printf("%d\n", symtab[i].u.ival);
            break;
        case FLOAT:
            printf("%f\n", symtab[i].u.fval);
            break;
        case STRING:
            //IDIOM: *p and p[0] are the same thing -- both are the first char
            printf("\"%s\"  (first char: '%c' via *, '%c' via [0])\n",
                    symtab[i].u.sval, *symtab[i].u.sval, symtab[i].u.sval[0]);
            break;
        }
    }
    return 0;
}

//bookprint:  the book's code exactly as printed in 6.8
//
//The last else belongs ONLY to the nearest if (the STRING test), so for
//an INT or a FLOAT the STRING test fails and "bad type" prints as well.
//The first two ifs are separate statements, not part of the chain.
void bookprint(union u_tag u, int utype)
{
    printf("  book:  ");
    if (utype == INT)
        printf("%d\n", u.ival);
    if (utype == FLOAT)
        printf("%f\n", u.fval);
    if (utype == STRING)
        printf("%s\n", u.sval);
    else
        printf("bad type %d in utype\n", utype);
}

//fixedprint:  same tests joined into one chain, so exactly one branch runs
void fixedprint(union u_tag u, int utype)
{
    printf("  fixed: ");
    //IDIOM: if / else if / else -- a multi-way decision; the final else
    //catches "none of the above"
    if (utype == INT)
        printf("%d\n", u.ival);
    else if (utype == FLOAT)
        printf("%f\n", u.fval);
    else if (utype == STRING)
        printf("%s\n", u.sval);
    else
        printf("bad type %d in utype\n", utype);
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
sizeof: int 4, float 4, char * 8  ->  union u_tag 8
offsetof: ival 0, fval 0, sval 0
addresses: &u 0x7ffc1bd9e338, &u.ival 0x7ffc1bd9e338, &u.fval 0x7ffc1bd9e338, &u.sval 0x7ffc1bd9e338

--- u holds an int (utype = INT) ---
  book:  42
bad type 0 in utype
  fixed: 42
--- u holds a float (utype = FLOAT) ---
  book:  3.140000
bad type 1 in utype
  fixed: 3.140000
--- u holds a string (utype = STRING) ---
  book:  hello
  fixed: hello

--- stored u.fval = 1.0, read back u.ival ---
u.ival = 1065353216  (0x3f800000): the raw IEEE-754 bits of 1.0f, not 1

--- v = u copies the whole union: v.fval = 1.000000 ---

sizeof(symtab[0]) = 24, sizeof(symtab[0].u) = 8
symtab[0] MAXLINE  = 1000
symtab[1] PI       = 3.141590
symtab[2] GREETING = "hello, world"  (first char: 'h' via *, 'h' via [0])


Headers and constants (lines 1–28)

#include <stdio.h>
#include <stddef.h>     //for offsetof()
stddef.h is a small header with a few basic definitions: size_t, NULL, ptrdiff_t, and the offsetof macro. This block doesn't use malloc or any string functions, so the other headers aren't included.


#define NSYM 3
This is the size of the symbol table. The book uses NSYM without giving it a value, so I picked 3, one entry per type.


enum { INT, FLOAT, STRING };
An enumeration (§2.3) creates named integer constants. The values start at 0 and count up, so INT = 0, FLOAT = 1, STRING = 2. That's why the output said bad type 0 for INT and bad type 1 for FLOAT. The enum has no tag because it's never used as a type, only as a source of names. It's preferable to three #defines because the compiler and debugger know the names. The book's code uses INT/FLOAT/STRING without defining them, so this line fills that gap.

The union type (lines 30–34)

union u_tag {
    int ival;
    float fval;
    char *sval;
};
In the book, this declaration ends with } u;, which declares the type and a variable u in one statement. Here it stops at };, so it declares only the type union u_tag, and the variable is created later inside main. Splitting them is necessary because bookprint and fixedprint take a union u_tag parameter, so the type needs a name visible at file scope.

From here on, the type's name is the two words union u_tag, the same way struct tnode worked before typedef.

The symbol table (lines 36–45)

struct {
    char *name;
    int flags;
    int utype;
    union {
        int ival;
        float fval;
        char *sval;
    } u;
} symtab[NSYM];
Reading from the inside out:

The inner union { ... } u; is a union with no tag, used to declare a member named u. Because it has no tag, this union type can't be referred to anywhere else. It is a different type from union u_tag, even though its members are identical. You couldn't pass symtab[i].u to bookprint; the compiler would reject it. That's why the loop at the end prints entries with its own switch and doesn't call the print functions.
The outer struct { ... } also has no tag, so symtab is the only variable that will ever have this type.
symtab[NSYM] makes it an array of 3 such structs.
symtab is declared outside any function, so it's an external variable, and like buf in the last block it starts out zeroed. Every name begins as a null pointer, every utype as 0 (which is INT), and every u.ival as 0. flags is never assigned. It's there only because the book's struct has it.

Prototypes (lines 47–48)

void bookprint(union u_tag, int);
void fixedprint(union u_tag, int);
These take the union by value. C copies a union into a parameter the same way it copies a struct, so each call copies all 8 bytes. The function gets its own copy, and changing it there wouldn't affect main's u.

main: the variables (lines 50–57)

union u_tag u = { 42 };
union u_tag v;
int utype = INT;
int i;
{ 42 } is a brace initializer like an array's. Because it's a union, the single value goes to the first member, ival.
v is uninitialized, since it's a local variable. It's assigned before use, at line 94.
utype is the tag that keeps track of which member is valid, written by hand. Every time the code stores into u, it also updates utype. If you forget one, the program reads the wrong member and the compiler can't catch it. This is the "programmer's responsibility" the book mentions.
Section 1: printing sizes and addresses (lines 59–69)

printf("sizeof: ... union u_tag %zu\n", sizeof(int), ..., sizeof(union u_tag));
When sizeof is applied to a type, the type needs parentheses: sizeof(int). When it's applied to an expression, you can leave them out (sizeof u), though most people write them anyway.


offsetof(union u_tag, ival)
offsetof is a macro and not a function, which is how it can take a type as an argument. Functions can't. It evaluates to a size_t constant at compile time, hence %zu.


printf("addresses: &u %p, ...", (void *) &u, (void *) &u.ival, ...);
&u.ival parses as &(u.ival). Member access . binds tighter than &, so this is the address of the member, not a member of an address.
%p prints a pointer, but strictly it expects a void *. &u.ival is an int * and &u.fval is a float *, so each gets a (void *) cast. On x86-64 it works without the casts, but the standard only guarantees %p for void *.
Sections 2–3: storing each type in turn (lines 70–85)

printf("--- u holds an int (utype = INT) ---\n");
bookprint(u, utype);
fixedprint(u, utype);
u already holds 42 from the initializer.


u.fval = 3.14;
utype = FLOAT;
3.14 is a double constant, because unsuffixed floating constants are double in C. Assigning it to a float member converts it automatically and silently. Writing 3.14f would make it a float constant from the start. Storing to fval overwrites the first 4 bytes that held 42, and the next line updates the tag to match.


u.sval = "hello";
utype = STRING;
A string literal is a char array that the compiler places in read-only static storage. Used in an expression, it decays to a pointer to its first character. So u.sval gets an 8-byte address, not a copy of "hello". The union never contains the characters, only the pointer to them. That's why a 4-byte int, a 4-byte float, and a string of any length can all fit in 8 bytes.

Section 4: reading the wrong member (lines 87–91)

u.fval = 1.0;
printf("u.ival = %d  (0x%08x): ...", u.ival, (unsigned) u.ival);
This deliberately writes fval and reads ival, without updating utype. The format spec %08x means: hexadecimal, at least 8 digits, padded with leading zeros. %x expects an unsigned int, so the int is cast to match.

Copying a union (lines 93–95)

v = u;
printf("... v.fval = %f ...", v.fval);
A union assignment copies all of its bytes, including whichever member is live. v now holds 1.0.

v.fval is a float, but %f is the format for a double. It still works because of the default argument promotions. printf is variadic (it takes ...), and when a float is passed in the ... part of a call, C automatically promotes it to double. So printf never receives a float, and %f handles both. The same promotion is why %c works when you pass a char: it gets promoted to int.

Section 5: filling and walking the table (lines 97–127)

symtab[0].name = "MAXLINE";
symtab[0].utype = INT;
symtab[0].u.ival = 1000;
symtab[0].u.ival reads left to right: element 0 of the array, its u member, then the union's ival. [] and . have the same precedence and group left to right, so no parentheses are needed. Each entry follows the same three steps: name, tag, value. These are the same pairs a #define table would store, e.g. #define MAXLINE 1000.


printf("sizeof(symtab[0]) = %zu, sizeof(symtab[0].u) = %zu\n", ...);
sizeof works on an expression without evaluating it. It only looks at the expression's type, so nothing is read from the array.


for (i = 0; i < NSYM; i++) {
    printf("symtab[%d] %-8s = ", i, symtab[i].name);
In %-8s, the 8 pads the string to a width of 8 and the - left-justifies it, which lines up the = signs. (Last block, %4d right-justified.)


switch (symtab[i].utype) {
case INT:
    printf("%d\n", symtab[i].u.ival);
    break;
case FLOAT:
    ...
case STRING:
    printf("\"%s\"  (first char: '%c' via *, '%c' via [0])\n",
            symtab[i].u.sval, *symtab[i].u.sval, symtab[i].u.sval[0]);
    break;
}
switch jumps to the case label that matches the value. break exits the switch. Without it, execution falls through into the next case's code, which is a common bug.
There's no default: case, so an invalid tag prints nothing after the =. fixedprint handles that with its final else.
\" inside a string literal is an escaped quote, which prints a literal " around the string.
*symtab[i].u.sval: postfix [] and . bind tighter than the prefix *, so this is *(symtab[i].u.sval). It follows the pointer and gets the first character, 'h'. symtab[i].u.sval[0] gets the same character, because p[0] is defined as *(p + 0).
A tagged union read through a switch is the standard pattern in real code. Interpreters, compilers' symbol tables, and event systems in GUI libraries are built this way.

bookprint and fixedprint (lines 130–162)

void bookprint(union u_tag u, int utype)
The parameter names u and utype are the same as main's variables, but they are separate local variables. Each function has its own scope, and these are copies of the arguments. I reused the names so the body could match the book's code word for word.

bookprint runs three independent if statements, with the last one paired with else. fixedprint makes them a single statement with else if. In C, else if isn't a special keyword. It's an else whose body happens to be another if, so the chain is nested ifs written flat. Indenting it as a flat list is the K&R convention for a multi-way decision (§3.3).

If you want to see the "programmer's responsibility" problem directly, delete utype = FLOAT; at line 75 and rebuild. fixedprint then reads the float's bits through %d and prints a large integer instead of 3.14, and the compiler gives no warning.

```
