---
title: GDB and RAM
date: 2026-10-04
---

```c
#include <stdio.h>
//compile with: gcc -Wall -Wextra c-c.c -o c-c
//run with:     ./c-c -df -n hello        # word: -df  letters: d f | word: -n  letters: n | stopped at: hello

//Your two lines (unchanged), inside a main so they can run. The outer
//loop steps through the WORDS on the command line; the inner loop
//steps through the LETTERS of one word.

int main(int argc, char *argv[])
{
    int c;

    while (--argc > 0 && (*++argv)[0] == '-') {
        printf("word: %s  letters:", *argv);
        while((c = *++argv[0]))
            printf(" %c", c);
        printf("\n");
    }
    if (argc > 0)
        printf("stopped at: %s (doesn't start with -)\n", *argv);
        
    return 0;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -g -Wall -Wextra c-c.c -o c-c
win@DESKTOP-MEIH88T:~/webdev-projects$ gdb --args ./c-c -df -n hello
GNU gdb (Ubuntu 17.1-2ubuntu1) 17.1
Copyright (C) 2025 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from ./c-c...
(gdb) list 9,23
9       int main(int argc, char *argv[])
10      {
11          int c;
12
13          while (--argc > 0 && (*++argv)[0] == '-') {
14              printf("word: %s  letters:", *argv);
15              while((c = *++argv[0]))
16                  printf(" %c", c);
17              printf("\n");
18          }
19          if (argc > 0)
20              printf("stopped at: %s (doesn't start with -)\n", *argv);
21
22          return 0;
23      }
(gdb) start
Temporary breakpoint 1 at 0x117c: file c-c.c, line 13.
Starting program: /home/win/webdev-projects/c-c -df -n hello
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/usr/lib/x86_64-linux-gnu/libthread_db.so.1".

Temporary breakpoint 1, main (argc=4, argv=0x7fffffffde08) at c-c.c:13
13          while (--argc > 0 && (*++argv)[0] == '-') {
(gdb) run
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: /home/win/webdev-projects/c-c -df -n hello
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/usr/lib/x86_64-linux-gnu/libthread_db.so.1".
word: -df  letters: d f
word: -n  letters: n
stopped at: hello (doesn't start with -)
[Inferior 1 (process 227242) exited normally]
(gdb) info args
(gdb) start
Temporary breakpoint 2 at 0x55555555517c: file c-c.c, line 13.
Starting program: /home/win/webdev-projects/c-c -df -n hello
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/usr/lib/x86_64-linux-gnu/libthread_db.so.1".

Temporary breakpoint 2, main (argc=4, argv=0x7fffffffde08) at c-c.c:13
13          while (--argc > 0 && (*++argv)[0] == '-') {
(gdb) info args
argc = 4
argv = 0x7fffffffde08
(gdb) info locals
c = 0
(gdb) print argc
$1 = 4
(gdb) ptype argv
type = char **
(gdb) ptype *argv
type = char *
(gdb) print argv[1]
$2 = 0x7fffffffe0f1 "-df"
(gdb) print *argv[1]
$3 = 45 '-'
(gdb) print argv[1][1]
$4 = 100 'd'
(gdb) print argv[4]
$5 = 0x0
(gdb) print sizeof(argv[0])
$6 = 8
(gdb) print/x argc
$7 = 0x4
(gdb) print/t argc
$8 = 100
(gdb) print/d *argv[1]
$9 = 45
(gdb) print/x *argv[1]
$10 = 0x2d
(gdb) x/3s argv[1]
0x7fffffffe0f1: "-df"
0x7fffffffe0f5: "-n"
0x7fffffffe0f8: "hello"
(gdb) x/4cb argv[1]
0x7fffffffe0f1: 45 '-'  100 'd' 102 'f' 0 '\000'
(gdb) x/4b argv[1]
0x7fffffffe0f1: 45 '-'  100 'd' 102 'f' 0 '\000'
(gdb) x/4xb argv[1]
0x7fffffffe0f1: 0x2d    0x64    0x66    0x00
(gdb) x/5xg argv
0x7fffffffde08: 0x00007fffffffe0d3      0x00007fffffffe0f1
0x7fffffffde18: 0x00007fffffffe0f5      0x00007fffffffe0f8
0x7fffffffde28: 0x0000000000000000
(gdb) x/5i $pc
=> 0x55555555517c <main+19>:    jmp    0x5555555551e9 <main+128>
   0x55555555517e <main+21>:    mov    -0x20(%rbp),%rax
   0x555555555182 <main+25>:    mov    (%rax),%rax
   0x555555555185 <main+28>:    lea    0xe7c(%rip),%rdx        # 0x555555556008
   0x55555555518c <main+35>:    mov    %rax,%rsi
(gdb)
```

```c
This is a fuller tour than last time, organized by what you want to do. Shell commands and GDB commands are kept in separate blocks, and every output is real, from sessions I ran on your c-c.c just now.

0. Setup (in bash)

gcc -g -Wall -Wextra c-c.c -o c-c
gdb --args ./c-c -df -n hello
1. Seeing the code: list
Type inside gdb:


list 9,23
This prints lines 9–23 with their numbers, so you know which line numbers to use for breakpoints. A plain list shows the 10 lines around where you are.

2. Starting: start and run
Type inside gdb:


start

Temporary breakpoint 1, main (argc=4, argv=0x7fffffffd708) at c-c.c:13
13	    while (--argc > 0 && (*++argv)[0] == '-') {
start sets a temporary breakpoint at main (it deletes itself after one hit) and runs. It's the quickest way to begin.

run starts without stopping unless a breakpoint is set. You can also change the arguments for a new run: run -nr restarts with -nr as the only argument.

3. Looking at values
Type inside gdb:


info args
info locals

argc = 4
argv = 0x7fffffffd708
c = 0
c = 0 here is luck. c hasn't been assigned yet, so it holds whatever was in that memory. It could have been anything.

Types:


ptype argv
ptype *argv

type = char **
type = char *
GDB confirms the two-level structure: argv is a pointer to pointers, and *argv is one string pointer.

print accepts any C expression:


print argv[1]
print *argv[1]
print argv[1][1]
print argv[4]
print sizeof(argv[0])

$4 = 0x7fffffffdae6 "-df"
$5 = 45 '-'
$8 = 100 'd'
$9 = 0x0
$10 = 8
argv[4] is 0x0, the NULL that ends the array. sizeof a pointer is 8 bytes on your 64-bit machine. The $4, $5 labels are saved results, so you can reuse them later, for example print $4.

Number formats are written as print/format:


print/x argc
print/t argc
print/d *argv[1]
print/x *argv[1]

$2 = 0x4       hex
$3 = 100       binary: 4 is 100
$6 = 45        decimal
$7 = 0x2d      hex
The character '-' is just the number 45, or 0x2d. They're three views of the same byte.

4. Looking at raw memory: x
x/ + count + format + size, then an address. Formats: s string, c char, x hex, i instruction. Sizes: b byte, g 8 bytes.


x/3s argv[1]

0x7fffffffdae6:	"-df"
0x7fffffffdaea:	"-n"
0x7fffffffdaed:	"hello"
This shows three strings in a row, packed back to back.


x/4cb argv[1]
x/4xb argv[1]

0x7fffffffdae6:	45 '-'	100 'd'	102 'f'	0 '\000'
0x7fffffffdae6:	0x2d	0x64	0x66	0x00
These are the same four bytes, as characters and as hex. The fourth is the '\0' that ends the string.

The argv array itself, the pointers rather than the strings:


x/5xg argv

0x7fffffffd708:	0x00007fffffffdac8	0x00007fffffffdae6
0x7fffffffd718:	0x00007fffffffdaea	0x00007fffffffdaed
0x7fffffffd728:	0x0000000000000000
This is the argv diagram in real memory. It's five 8-byte slots. Each holds the address of one word: ...dae6 is "-df", ...daea is "-n", ...daed is "hello". The fifth slot is 0, the NULL. The array lives near d708, and the strings near dae6.

The machine code you're about to run:


x/5i $pc

=> 0x55555555517c <main+19>:	jmp    0x5555555551e9 <main+128>
   0x55555555517e <main+21>:	mov    -0x20(%rbp),%rax
$pc is the program counter, the address of the next instruction. The => marks it. This is the jump to the loop test at the bottom, which is why break 13 hit only once last time.

5. Moving through the program
command	what it does
next	run one line, treating function calls as one step
step	run one line, entering any function it calls
finish	run until the current function returns
continue	run until the next breakpoint
advance 17	run until line 17
Enter	repeat the last command
step + bt + finish, stopped at line 16, printf(" %c", c):


step
bt
finish

__printf (format=0x55555555601b " %c") at ./stdio-common/printf.c:28
#0  __printf (format=0x55555555601b " %c") at ./stdio-common/printf.c:28
#1  0x00005555555551b7 in main (argc=1, argv=0x7fffffffd730) at c-c.c:16
main (argc=1, argv=0x7fffffffd730) at c-c.c:15
Value returned is $1 = 2
step went into the library's printf.
bt shows the two levels: printf (#0) was called from main line 16 (#1).
finish came back out, and GDB reported printf's return value: 2. printf returns how many characters it printed, here a space and f. Most people never notice that printf returns anything.
Leaving a loop early with advance:


delete
advance 17

main (argc=1, argv=0x7fffffffd720) at c-c.c:17
17	        printf("\n");
This finishes the rest of the inner loop in one command. Delete the breakpoints first; otherwise advance stops at them on the way.

6. Breakpoints in more detail
A conditional breakpoint stops only when an expression is true:


break 16 if c == 'f'
break 20
info breakpoints
run

Num     Type           Disp Enb Address            What
1       breakpoint     keep y   0x...119e in main at c-c.c:16
	stop only if c == 'f'
2       breakpoint     keep y   0x...1210 in main at c-c.c:20

Breakpoint 1, main (argc=3, argv=0x7fffffffd710) at c-c.c:16
It skipped the d and stopped only at the f. In a loop that runs a thousand times, this is how you stop at the one pass you care about.

command	effect
info breakpoints	list them, with how often each has been hit
delete 2 / delete	remove one / all
disable 1 / enable 1	switch one off and on without deleting it
tbreak 15	a breakpoint that deletes itself after one hit
7. Watchpoints: stop when a value changes

start
watch argc
continue

Hardware watchpoint 2: argc

Old value = 4
New value = 3
...  at c-c.c:13
Each continue stops at the next change: 3→2, then 2→1. You don't say where to stop, only what to watch. At the end:


Watchpoint 2 deleted because the program has left the block in
which its expression is valid.
argc lives only inside main, and once main returns it no longer exists. "Hardware" means the CPU itself watches that memory address.

8. Changing the program while it runs: set var
Stopped at line 14, on the word "-df":


set var argv[0][1] = 'z'
print *argv
delete
continue

$1 = 0x7fffffffdae6 "-zf"
word: -zf  letters: z f
word: -n  letters: n
stopped at: hello (doesn't start with -)
That wrote one byte in memory, changing d (0x64) to z (0x7a), and the program printed -zf, which you never typed. You can test "what if" without editing or recompiling.

9. Automatic displays

display argc
display *argv
These print after every step until undisplay, as you used last time to watch *argv move one byte at a time.

10. Split-screen mode

gdb -tui --args ./c-c -df -n hello
This shows the source in a pane, with the current line highlighted as you step. Ctrl-x a switches the split screen on and off.

Quick reference
task	command
begin	start / run / run -nr
see code	list
move	next step finish continue advance N
stop points	break N / break N if expr / tbreak / watch var
manage	info breakpoints / delete / disable
look	print (/x /t /d /c) / ptype / info locals / info args
memory	x/s x/4cb x/4xb x/5xg x/5i $pc
calls	bt / frame N / up / down
change	set var x = ...
auto-show	display / undisplay
quit	quit
A good next session to try yourself: start, then x/5xg argv. Compare the addresses with x/3s argv[1], and you'll see the pointer array pointing at the packed strings.
```
