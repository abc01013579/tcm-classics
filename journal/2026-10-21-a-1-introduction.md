---
title: A.1 Introduction
date: 2026-10-21
---

```c
#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c
//the manual's own C89 refuses this file -- that's claim 2 below:
//              gcc -std=c89 -Wall -Wextra cc-c.c -o cc-c    # error: C++ style comments are not allowed in ISO C90
//C89 plus gcc's extensions, // among them:
//              gcc -std=gnu89 -Wall -Wextra cc-c.c -o cc-c
//              ./cc-c
//C99, the first standard with //:
//              gcc -std=c99 -pedantic -Wall -Wextra cc-c.c -o cc-c
//              ./cc-c

//K&R2 Appendix A.1 Introduction -- claim by claim.
//
//"the C language specified by the draft submitted to ANSI on 31 October
//1988 ... X3.159-1989"
//  That draft became C89 (ANSI, 1989), adopted word for word by ISO as
//  C90. Since then: C95 (a small amendment), C99, C11, C17, C23.
//  A compiler says which one it is compiling with __STDC_VERSION__.
//  gcc 15 on this machine defaults to C23 -- 35 years past the manual.
//  -std picks the standard; -pedantic makes gcc complain about
//  anything that standard doesn't allow.
//
//"an interpretation of the proposed standard, not the standard itself"
//  The standard is ISO/IEC 9899. Where the manual and the standard
//  disagree, the standard decides. Where gcc's default and the manual
//  disagree, it's usually because the standard moved on (part 3).
//
//"commentary material ... highlight ways in which ANSI Standard C
//differs from the language defined by the first edition"
//  The biggest of those differences: function prototypes. In K&R1 a
//  function's parameter types were declared between ) and {, and a call
//  was never checked against them. ANSI added prototypes and kept the
//  old form as "obsolescent"; C23 finally removed it. Parts 3 and 4.
//
//main:
//  1. which standard this compile is
//  2. // comments: not in the manual's C
//  3. a first-edition (K&R1) function definition, where still allowed
//  4. a prototype converts its argument; a K&R1 definition doesn't

//IDIOM: #if defined(X) && X >= n -- test a macro that may not exist.
//(an undefined name in #if reads as 0 anyway; defined() says so aloud)
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 202311L
#define KR1_ALLOWED 0           //C23: old-style definitions are gone
#else
#define KR1_ALLOWED 1
#endif

int echo_proto(int x)           //ANSI: the types are in the parentheses
{
    return x;
}

#if KR1_ALLOWED
int echo_kr1(x)                 //K&R1: names only in the parentheses,
int x;                          //types declared before the {
{
    return x;
}
#endif

int main(void)
{
    printf("1. which C is this?\n");
    printf("   __STDC__ = %d (1: the compiler claims to conform)\n",
           __STDC__);
#ifdef __STDC_VERSION__
    printf("   __STDC_VERSION__ = %ldL\n", (long)__STDC_VERSION__);
#else
    printf("   __STDC_VERSION__ not defined: C89/C90, the manual's C\n");
#endif
    printf("   199409 = C95, 199901 = C99, 201112 = C11, 201710 = C17,\n"
           "   202311 = C23. C89 predates the macro\n");

    printf("\n2. the manual's C has no // comments: they came from C++\n"
           "   into C99. strict -std=c89 rejects this file at line 2;\n"
           "   -std=gnu89 is C89 plus gcc's extensions, // among them\n");

    printf("\n3. a first-edition function definition\n");
#if KR1_ALLOWED
    printf("   echo_kr1(9) = %d: compiled. C89 through C17 still accept\n"
           "   the K&R1 form, marked obsolescent\n", echo_kr1(9));
#else
    printf("   left out: C23 removed K&R1 definitions, and int f() now\n"
           "   means int f(void), as it always did in C++\n");
#endif

    printf("\n4. what prototypes bought: argument conversion\n");
    printf("   echo_proto(9.8) = %d: the prototype says int, so the\n"
           "   compiler converts 9.8 to 9 before the call\n",
           echo_proto(9.8));
#if KR1_ALLOWED
    printf("   echo_kr1(9.8) = %d: no prototype, so 9.8 goes as a\n"
           "   double while echo_kr1 reads an int from where an int\n"
           "   would be. undefined behaviour: on x86-64 a double travels\n"
           "   in a different register, so x is whatever was left in\n"
           "   the int one. K&R1 code was full of this bug\n",
           echo_kr1(9.8));
#endif
    return 0;
}


win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
1. which C is this?
   __STDC__ = 1 (1: the compiler claims to conform)
   __STDC_VERSION__ = 202311L
   199409 = C95, 199901 = C99, 201112 = C11, 201710 = C17,
   202311 = C23. C89 predates the macro

2. the manual's C has no // comments: they came from C++
   into C99. strict -std=c89 rejects this file at line 2;
   -std=gnu89 is C89 plus gcc's extensions, // among them

3. a first-edition function definition
   left out: C23 removed K&R1 definitions, and int f() now
   means int f(void), as it always did in C++

4. what prototypes bought: argument conversion
   echo_proto(9.8) = 9: the prototype says int, so the
   compiler converts 9.8 to 9 before the call
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -std=c89 -Wall -Wextra cc-c.c -o cc-c
cc-c.c:2:1: error: C++ style comments are not allowed in ISO C90
    2 | //compile with: gcc -Wall -Wextra cc-c.c -o cc-c
      | ^
cc-c.c:2:1: note: (this will be reported only once per input file)
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -std=c99 -pedantic -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
1. which C is this?
   __STDC__ = 1 (1: the compiler claims to conform)
   __STDC_VERSION__ = 199901L
   199409 = C95, 199901 = C99, 201112 = C11, 201710 = C17,
   202311 = C23. C89 predates the macro

2. the manual's C has no // comments: they came from C++
   into C99. strict -std=c89 rejects this file at line 2;
   -std=gnu89 is C89 plus gcc's extensions, // among them

3. a first-edition function definition
   echo_kr1(9) = 9: compiled. C89 through C17 still accept
   the K&R1 form, marked obsolescent

4. what prototypes bought: argument conversion
   echo_proto(9.8) = 9: the prototype says int, so the
   compiler converts 9.8 to 9 before the call
   echo_kr1(9.8) = -1830142496: no prototype, so 9.8 goes as a
   double while echo_kr1 reads an int from where an int
   would be. undefined behaviour: on x86-64 a double travels
   in a different register, so x is whatever was left in
   the int one. K&R1 code was full of this bug
```
