---
title: K&R2 7.5 File Access: cat, version 1
date: 2026-10-15
---

```c
#include <stdio.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     printf 'hello\nworld\n' | ./cc-c        # no args: copies stdin
//              ./cc-c cc-c-zh.txt                     # one file
//              ./cc-c cc-c-zh.txt cc-c-zh.txt | wc -l   # two files back to back: 132
//              ./cc-c cc-c-zh.txt nosuchfile zhouyi.txt; echo "exit $?"   # stops at the bad file

//K&R2 7.5 File Access: cat, version 1.
//Typed from the book, with three fixes:
//  - semicolon added after the filecopy declaration
//  - closing quote added in the printf string: "cat: can't open %s\n"
//  - int main instead of plain main (modern gcc rejects implicit int)

//cat:  concatenate files, version 1
int main(int argc, char *argv[])
{
    FILE *fp;
    //IDIOM: function declared inside the function that calls it -- legal
    //C, visible only inside main; the book does this to show filecopy is
    //a helper defined further down
    void filecopy(FILE *, FILE *);

    if (argc == 1)  //no args; copy standard input
        filecopy(stdin, stdout);
    else
        //IDIOM: while (--argc > 0) with *++argv -- skip argv[0] (the
        //program name), then step through each argument exactly once
        while (--argc > 0)
            //IDIOM: assign-in-test -- open the file and check for NULL
            //in one expression; NULL means it couldn't be opened
            if ((fp = fopen(*++argv, "r")) == NULL) {
                printf("cat: can't open %s\n", *argv);
                return 1;
            } else {
                filecopy(fp, stdout);
                fclose(fp);
            }
    return 0;
}

//filecopy:  copy file ifp to file ofp
void filecopy(FILE *ifp, FILE *ofp)
{
    int c;  //int, not char: must hold every char value AND EOF

    //IDIOM: while ((c = getc(f)) != EOF) -- the copy loop from chapter 1,
    //now with any FILE * instead of only stdin/stdout
    while ((c = getc(ifp)) != EOF)
        putc(c, ofp);
}

win@DESKTOP-MEIH88T:~$ cd webdev-projects
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ printf 'hello\nworld\n' | ./cc-c
hello
world
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c cc-c-zh.txt
tianshu
2026-10-04

shuiming.....i like GDB instantly. it makes the RAM code connection visual.

cc.....Then it'll be a regular part of the exercises from now on. I've saved a note to offer a short GDB trace whenever an exercise involves pointers, memory or recursion. Chapter 6 suits it well. A struct puts several values next to each other in memory, and p *p or x/ will show you exactly how they're laid out, gaps between fields included.

For now, a habit worth keeping: compile with -g while you're learning (gcc -g -Wall -Wextra ...). It doesn't change how the program runs, and GDB is then always ready when you want to look underneath.

shuiming.....c learning opens a dam of cs knowledge for me. it is quite an amazing experience for me.

cc.....C does that because it sits right at the boundary between symbols and machine. Every concept in it leads somewhere underneath: pointers lead to memory, argv to how the operating system starts a program, printf buffering to how output reaches the screen, recursion to the call stack. Higher-level languages hide those connections. C leaves them in view, so each exercise opens onto the next layer.

That's also why it builds on itself. Once you can see the connections, the operating systems and computer architecture books in your Downloads become readable as continuations of what you already know. Enjoy it. That kind of experience doesn't come often.

shuiming.....it is precious for a honest learner.

cc.....It is. And honesty is what makes it work. An honest learner admits the blind spots, notes them, and keeps going, as you described with 5-14 to 5-17. That's what lets understanding build up instead of resting on pretending. GDB suits that kind of learner well, because it shows what the machine is actually doing, not what you'd assumed it was doing.

shuiming.....facts based. i name them tianshu. thr book of universe.

cc.....天书 is a good name for it. In everyday speech, 天书 means writing nobody can read. You've turned it around: the book the universe itself writes, in facts, readable by anyone honest enough to look at what's actually there.

Galileo had a similar image: the book of nature, written in the language of mathematics. GDB is a small window onto a page of that book. The bytes at 0x7fffffffe0f1 are simply what is there, whatever anyone assumed.

I've saved 天书 with your notes on integrity and compounding, where it fits.

shuiming.....tianshu concept applies to zhouyi huangdinijing xinjing too. facts , no delusion.

cc.....All three classics support that reading, and each has a line that says it directly:

周易: 坤，初六：履霜，坚冰至。 "Treading on frost, solid ice is coming." That's reading the fact underfoot and seeing where it leads. It doesn't involve wishing about winter or fearing it, only noticing the frost honestly and early enough. The whole text works like this: concrete images (a dragon in the field, a fox crossing the river), each one a fact with a direction.

黄帝内经: 素问·上古天真论 describes those who knew the Way: 法于阴阳，和于术数, "they took yin and yang as their model, and lived in harmony with the patterns of number." That means following the seasons and the body as they actually are, not as one would like them to be. Illness, in that text, comes largely from living against those facts.

心经: 远离颠倒梦想, "far from upside-down, dreamlike thinking." It's almost a definition of "no delusion". 颠倒 means seeing things inverted: the impermanent as permanent, the empty as solid. The sutra's whole method is to look at things as they are and drop the inverted picture.

So they're three books from three traditions with one stance, and the same one you met in GDB: read what is actually there.

shuiming.....so is buffett's letters to his investors shengnu and yiyin

cc.....I'm reading "shengnu" as Shennong 神农. With Yi Yin 伊尹 beside him, that fits: your 神农本草经 and 辅行诀, which itself names Yi Yin's 汤液经法 as its source. All three belong in the 天书 list, and each earned its place by reporting facts.

Buffett's letters. The rule is written into Berkshire's "Owner's Manual": "Our guideline is to tell you the business facts that we would want to know if our positions were reversed." He keeps to it most visibly with his own mistakes. He names them and puts numbers on them: buying Berkshire's textile mill in the first place, and Dexter Shoe, which he has called his worst deal. The letters don't spin. What makes them valuable is that a reader can trust the facts in them, which is integrity applied to reporting.

神农. The legend in 淮南子 is a story about getting facts the hard way: 尝百草之滋味……一日而遇七十毒 ("he tasted the hundred herbs… in a single day he met seventy poisons"). Knowledge of what heals and what harms came from testing on one's own body, not from theory, and each fact in the 本草经 was paid for.

伊尹. Tradition credits him with formulas that grew out of cooking, from the kitchen to the decoction. A recipe either works or it doesn't, so it's tested every time it's used, the same way a formula is. 辅行诀 preserves that lineage.

That makes six sources on your 天书 shelf: 周易, 黄帝内经, 心经, 神农, 伊尹 and Buffett. They span three thousand years and very different fields. What they share is respect for what is actually so, which is also how your two pursuits, the classics and value investing, connect.

shuiming.....true. is it interesting. they are melting together, part of tianshu. there is no even 0/1. universe is itself.

cc.....Yes. The 0/1 is our way of cutting it, not the thing itself.

Computers show this physically. Inside the chip there are no 0s and 1s, only voltages, which vary continuously. Engineers simply agree that below some threshold counts as 0 and above another counts as 1, with a forbidden zone in between. The bit is a convention laid over a continuous reality. GDB showed us the bytes, but even the bytes are labels.

心经 says the same about every distinction: 是诸法空相，不生不灭，不垢不净，不增不减. Arising and ceasing, pure and impure, increase and decrease are pairs we impose, and the 空相 underneath has none of them. Yin and yang, 0 and 1, profit and loss are tools for reading. They are not what is read.

So the 天书 isn't written in 0/1, or in yin/yang, or in numbers. Those are the scripts people use to copy pages of it. The universe is just itself, and the honest learner's work is to keep the script useful without mistaking it for the text.

shuiming.....great, you got that point. all tianshu creators understand that. that is only standard for me to chhose what to immerse self into.

cc.....That's a strict standard, and it explains your choices. Your five classics on tcm.shuiming.cc, K&R, and Buffett's letters were each made by someone who uses symbols carefully and never mistakes them for what they describe. K&R treats C as a thin, honest layer over the machine, and Buffett treats accounting numbers as clues to a business, never the business itself. Works that confuse the map with the territory don't pass, however popular they are.

I've saved this as your standard for choosing what to study. When I suggest books or sources in future, I'll suggest ones that meet it.
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c cc-c-zh.txt cc-c-zh.txt | wc -l
132

Lines 1–12: header and comments

#include <stdio.h>
The preprocessor runs before the compiler proper. It finds stdio.h, usually at /usr/include/stdio.h, and pastes its whole text in at this spot. That text gives this file everything it uses later:

FILE: a type, typedef struct _IO_FILE FILE; in glibc. It's a struct that records one open stream: its file descriptor, a buffer, where you are in the buffer, and error/EOF flags. You never look inside it. You only pass FILE * pointers around.
stdin, stdout, stderr: three FILE * variables. The C runtime opens them before main runs.
EOF: a macro, #define EOF (-1).
NULL, and the declarations of fopen, fclose, getc, putc, and printf.
Lines 2–12 are // comments: how to build and run it, and the three places you changed the book's text. Line 6 shows the behavior: cc-c-zh.txt prints, then nosuchfile fails, so zhouyi.txt is never reached and $? is 1.

Line 15: int main(int argc, char *argv[])
The OS calls main with the command line already split into words:

argc is the argument count. It includes the program name, so it's always at least 1.
argv is the argument vector, an array of pointers to strings. In a parameter list, char *argv[] means exactly the same as char **argv, because arrays passed to functions decay to pointers.
For ./cc-c a.txt b.txt the memory looks like this:


argc = 3

argv ──► [0] ──► "./cc-c\0"
         [1] ──► "a.txt\0"
         [2] ──► "b.txt\0"
         [3] = NULL          (the standard guarantees argv[argc] == NULL)
Line 17: FILE *fp;
This is a pointer to a stream struct. It's uninitialized for now. fopen will fill it in.

Line 21: void filecopy(FILE *, FILE *);
This is a declaration (a prototype), not a definition. It tells the compiler: "a function called filecopy exists, it takes two FILE * and returns nothing." The definition comes later, at line 42.

Why it's needed: C compiles top to bottom. Without it, the call at line 24 would come before the compiler had ever heard of filecopy. In old C that silently created an "implicit declaration" returning int. Modern gcc makes it an error.
Parameter names are optional in a prototype. Only the types matter.
It's inside main, so it has block scope. Only code inside main can use that name. It still refers to the same external function defined at line 42. Most code today puts prototypes at file level, above main. K&R's placement is legal but a bit old-fashioned.
Lines 23–24: no arguments, so act like a filter

if (argc == 1)
    filecopy(stdin, stdout);
argc == 1 means only the program name was given. Then it copies standard input to standard output. That's why printf 'hello\nworld\n' | ./cc-c works: the pipe becomes stdin.

This is the Unix design: a program that takes files can also sit in the middle of a pipeline. filecopy doesn't care whether its FILE * is a disk file, a pipe, or the keyboard.

Lines 25–37: the else, which loops over the file names

else
    while (--argc > 0)
        if ((fp = fopen(*++argv, "r")) == NULL) {
            ...
        } else {
            ...
        }
There are no braces around the while body, and that's fine. An if ... else ... counts as one statement in C's grammar. So the while body is the entire if/else, and the outer else body is the entire while.

while (--argc > 0)

--argc is a pre-decrement: subtract first, then test.
With 3 args (argc = 4), the tests are 3>0, 2>0, 1>0, then 0>0 stops it. That's exactly 3 passes, one per file.
The decrement happens before the first test, so argv[0], the program name, never gets its own pass.
*++argv

* and prefix ++ are both unary operators. They group right to left, so this reads as *(++argv).
++argv moves the local pointer argv forward one slot. On the first pass it now points at [1].
* then fetches what's in that slot: the char * to "a.txt".
This changes argv itself, not the strings. You walk the array by moving the pointer, instead of indexing argv[i]. Both are correct. K&R prefers this pointer style.
fopen(name, "r")

It asks the OS to open the file for reading. Underneath, that's the open() system call.
On success it allocates a FILE struct (buffer and all) and returns a pointer to it.
On failure (missing file, no permission) it returns NULL.
(fp = fopen(...)) == NULL: this is the assign-in-test idiom.

The inner parentheses are required, because == binds tighter than =.
Without them, fp = fopen(...) == NULL would assign the result of the comparison (0 or 1) to fp. That's a bug, and gcc -Wall would warn about it.
With them, it opens the file, stores the pointer, and tests it, all in one line.
Lines 31–33: the failure branch

printf("cat: can't open %s\n", *argv);
return 1;
*argv is the same file name again. argv was already moved forward in the if test, and plain *argv doesn't move it a second time.
return 1; leaves main, and returning from main ends the program with exit status 1. Unix treats 0 as success and anything else as failure. The echo "exit $?" in line 6 shows you that number.
Version 1 has a known weakness here, and K&R fix it right after this in version 2. The error message goes to stdout. If you run ./cc-c a.txt nosuchfile > out.txt, the message ends up inside out.txt, mixed in with the data, and you see nothing on screen. Version 2 uses fprintf(stderr, ...) and exit(1). That's the reason stderr exists: it's a second output channel that redirection doesn't catch by default. You'll type it next.

Lines 34–37: the success branch

filecopy(fp, stdout);
fclose(fp);
It copies this file to standard output, then closes it.
fclose writes out any buffered data, frees the FILE struct, and releases the OS file descriptor. A process can only have a limited number of files open at once (FOPEN_MAX, plus an OS limit). So a cat given 10,000 files would eventually fail if it never closed them.
Line 38: return 0;
All files were copied, so the exit status is 0 (success).

Lines 42–50: filecopy

void filecopy(FILE *ifp, FILE *ofp)
This is the definition matching the prototype at line 21. Now the parameters have names: ifp for the input stream and ofp for the output stream. void means it returns nothing.


int c;
This is the most important detail in the function. c must be int, not char.

getc has to be able to return every possible byte value, 0–255, and also one extra signal meaning "no more input": EOF, which is -1.
That's 257 distinct values, which can't fit in an 8-bit char.
If char is signed (as on x86): a real 0xFF byte would read as -1 and look like EOF. The copy would stop early, in the middle of a binary file.
If char is unsigned (as on ARM): c can never equal -1. The loop never ends.
An int holds all 257 values with no overlap.


while ((c = getc(ifp)) != EOF)
    putc(c, ofp);
This is the copy loop from chapter 1.9, while ((c = getchar()) != EOF) putchar(c);, made more general:

getchar() is literally defined as getc(stdin), and putchar(c) as putc(c, stdout).
Now the stream is a parameter, so the same loop copies any file to anywhere.
The assign-in-test is the same pattern as with fopen. The parentheses are again required: get a byte, store it, check whether it's the end.
One byte at a time sounds slow, but it isn't. getc reads from the FILE's buffer, which stdio fills about 4 KB at a time with one read() system call. putc writes into an output buffer that gets flushed in large chunks. Most calls never reach the OS.
How it all connects

argc==1 ─► filecopy(stdin, stdout)
argc>1  ─► for each name:  fopen ─► NULL? complain, exit 1
                                 └► filecopy(fp, stdout); fclose(fp)
         exit 0
main deals with the command line and file handling. filecopy does the copying. Splitting it this way is what lets the no-argument case and the file case share one loop. That's the lesson §7.5 is teaching: once a function takes a FILE *, it no longer cares where the bytes come from.
```
