---
title: K&R2 8.5 Example -- An Implementation of Fopen and Getc
date: 2026-10-20
---

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c < zhouyi.txt         # stdin is a file: section 8 reads it with my_getchar
//              echo 乾為天 | ./cc-c        # stdin is a pipe: my_getchar doesn't care which
//              ./cc-c                      # stdin is the terminal: section 8 is skipped

//K&R2 8.5 Example -- An Implementation of Fopen and Getc. The book's
//code, run, with every claim in the section shown by a printf:
//  1. a FILE is a struct: buffer, position, count, flags, fd; all open
//     files live in one table, _iob[OPEN_MAX]; stdin is &_iob[0]
//  2. fopen finds a free slot, gets an fd from open/creat, and sets
//     cnt 0 and base NULL -- no buffer yet
//  3. the first getc finds cnt empty and calls _fillbuf, which mallocs
//     the buffer and fills it with ONE read
//  4. after that, getc is a macro that never calls anything until the
//     buffer is empty again: one read per BUFSIZ characters
//  5. _fillbuf turns read's 0 into the EOF flag, and stops reading
//     once that flag is set
//  6. read's -1 becomes the ERR flag
//  7. the (unsigned char) cast keeps every byte 0..255, so EOF can only
//     mean end of file
//  8. stdin, stdout, stderr need no fopen: the table starts with fd 0,
//     1, 2 already in it
//  9. _UNBUF means a buffer of 1: one read per character
// 10. a macro evaluates its argument more than once (the book's
//     warning about getc and putc)
// 11. modes: "w" is creat, "a" is open + lseek to the end, anything
//     else is refused
// 12. the table is fixed at OPEN_MAX: the 21st fopen fails
// 13. the real glibc FILE, for comparison
//
//The book's names (FILE, _iob, getc, _fillbuf, _READ ...) belong to
//<stdio.h>, which is included here for printf -- so every name gets a
//my_ / M_ prefix. Otherwise it is the book's code line for line;
//anything added for the printfs is marked "not in the book".

#define MY_OPEN_MAX 20      //max #files open at once
#define MY_BUFSIZ   1024
#define PERMS       0666    //RW for owner, group, others
#define DEMO        "fopen-demo.txt"    //made in section 11, unlinked at the end

typedef struct my_iobuf {
    int   cnt;      //characters left
    char *ptr;      //next character position
    char *base;     //location of buffer
    int   flag;     //mode of file access
    int   fd;       //file descriptor
} MYFILE;

//IDIOM: flags as powers of two -- each one its own bit, so one int
//holds all of them: set with |=, test with &
enum my_flags {
    M_READ  = 01,   //file open for reading
    M_WRITE = 02,   //file open for writing
    M_UNBUF = 04,   //file is unbuffered
    M_EOF   = 010,  //EOF has occurred on this file
    M_ERR   = 020   //error occurred on this file
};

//IDIOM: partial array initializer -- the 3 listed slots get these
//values, the other 17 are all zeros: flag 0 means "free"
MYFILE my_iob[MY_OPEN_MAX] = {      //stdin, stdout, stderr
    { 0, (char *) 0, (char *) 0, M_READ, 0 },
    { 0, (char *) 0, (char *) 0, M_WRITE, 1 },
    { 0, (char *) 0, (char *) 0, M_WRITE | M_UNBUF, 2 }
};

#define my_stdin  (&my_iob[0])
#define my_stdout (&my_iob[1])
#define my_stderr (&my_iob[2])

int my_fillbuf(MYFILE *);

#define my_feof(p)   (((p)->flag & M_EOF) != 0)
#define my_ferror(p) (((p)->flag & M_ERR) != 0)
#define my_fileno(p) ((p)->fd)

//IDIOM: --cnt >= 0 ? fast : slow -- decrement first: cnt 1 becomes 0,
//still >= 0, so the last byte is taken; cnt 0 becomes -1: refill
#define my_getc(p) (--(p)->cnt >= 0 \
                   ? (unsigned char) *(p)->ptr++ : my_fillbuf(p))
#define my_getchar() my_getc(my_stdin)

//not in the book: the same macro without the cast, for section 7
#define nocast_getc(p) (--(p)->cnt >= 0 \
                       ? *(p)->ptr++ : my_fillbuf(p))

int nreads = 0;     //not in the book: how many times read() was called
int trace = 0;      //not in the book: 1 = my_fillbuf prints each read

//my_fopen:  open file, return file ptr
MYFILE *my_fopen(char *name, char *mode)
{
    int fd;
    MYFILE *fp;

    if (*mode != 'r' && *mode != 'w' && *mode != 'a')
        return NULL;
    //IDIOM: pointer walk over an array -- fp < my_iob + MY_OPEN_MAX is
    //"not past the end", the pointer form of i < MY_OPEN_MAX
    for (fp = my_iob; fp < my_iob + MY_OPEN_MAX; fp++)
        //IDIOM: (flag & (A | B)) == 0 -- "neither bit is set"
        if ((fp->flag & (M_READ | M_WRITE)) == 0)
            break;      //found free slot
    if (fp >= my_iob + MY_OPEN_MAX)     //no free slots
        return NULL;

    if (*mode == 'w')
        fd = creat(name, PERMS);
    else if (*mode == 'a') {
        //IDIOM: assign-in-test with -1 -- try open; only if that
        //fails, creat
        if ((fd = open(name, O_WRONLY, 0)) == -1)
            fd = creat(name, PERMS);
        lseek(fd, 0L, 2);
    } else
        fd = open(name, O_RDONLY, 0);
    if (fd == -1)       //couldn't access name
        return NULL;
    fp->fd = fd;
    fp->cnt = 0;
    fp->base = NULL;
    fp->flag = (*mode == 'r') ? M_READ : M_WRITE;
    return fp;
}

//my_fillbuf:  allocate and fill input buffer
int my_fillbuf(MYFILE *fp)
{
    int bufsize;

    //IDIOM: (flag & (A|B|C)) != A -- mask three bits, then demand
    //exactly one pattern: READ set, EOF and ERR both clear
    if ((fp->flag & (M_READ | M_EOF | M_ERR)) != M_READ)
        return EOF;
    bufsize = (fp->flag & M_UNBUF) ? 1 : MY_BUFSIZ;
    if (fp->base == NULL)       //no buffer yet
        if ((fp->base = (char *) malloc(bufsize)) == NULL)
            return EOF;         //can't get buffer
    fp->ptr = fp->base;
    nreads++;                   //not in the book
    fp->cnt = read(fp->fd, fp->ptr, bufsize);
    if (trace)                  //not in the book
        printf("   [my_fillbuf: read() returned %d]\n", fp->cnt);
    //IDIOM: one decrement sorts three cases -- n bytes: n-1 left after
    //this one; 0 (end of file) becomes -1; -1 (error) becomes -2
    if (--fp->cnt < 0) {
        if (fp->cnt == -1)
            fp->flag |= M_EOF;
        else
            fp->flag |= M_ERR;
        fp->cnt = 0;
        return EOF;
    }
    return (unsigned char) *fp->ptr++;
}

//not in the book: point a MYFILE at bytes already in memory, so a test
//can feed it exact bytes; M_EOF set, so when they run out my_fillbuf
//returns EOF without reading anything
void fake(MYFILE *fp, char *s, int n)
{
    fp->base = fp->ptr = s;
    fp->cnt = n;
    fp->flag = M_READ | M_EOF;
    fp->fd = -1;
}

int main(void)
{
    MYFILE *fp, *dp, *up, *ap;
    int c, i, n, r0;
    char line[200];
    struct stat st;

    //--- 1. the table --------------------------------------------------
    printf("1. sizeof(MYFILE) = %zu bytes; my_iob[] holds %d of them = %zu bytes\n",
           sizeof(MYFILE), MY_OPEN_MAX, sizeof(my_iob));
    for (i = 0; i < 4; i++)
        printf("   my_iob[%d]: fd %d, flag %02o%s\n", i, my_iob[i].fd, my_iob[i].flag,
               i == 0 ? "  READ          <- stdin" :
               i == 1 ? "  WRITE         <- stdout" :
               i == 2 ? "  WRITE|UNBUF   <- stderr" : "  (0 = free, like the 16 after it)");
    printf("   my_stdin == &my_iob[0]: %s -- a FILE * is a pointer into this table\n\n",
           my_stdin == &my_iob[0] ? "yes" : "no");

    //--- 2. fopen ------------------------------------------------------
    fp = my_fopen("zhouyi.txt", "r");
    if (fp == NULL) {
        fprintf(stderr, "can't open zhouyi.txt\n");
        return 1;
    }
    //IDIOM: fp - my_iob -- subtracting pointers into one array gives
    //the index; %td is the printf format for that difference
    printf("2. my_fopen(\"zhouyi.txt\", \"r\") -> &my_iob[%td]: the first free slot\n",
           fp - my_iob);
    printf("   fd %d (0, 1, 2 are taken), flag %02o, cnt %d, base %s -- nothing read yet\n\n",
           fp->fd, fp->flag, fp->cnt, fp->base == NULL ? "NULL" : "set");

    //--- 3. the first getc fills the buffer --------------------------------
    c = my_getc(fp);
    printf("3. first my_getc -> 0x%02x; read() calls so far: %d\n", c, nreads);
    printf("   now base is malloc'd, cnt %d, ptr - base = %td\n",
           fp->cnt, fp->ptr - fp->base);
    printf("   the kernel's position: %ld -- it moved %d, we used 1: two positions\n",
           (long) lseek(fp->fd, 0L, SEEK_CUR), MY_BUFSIZ);
    my_getc(fp);
    my_getc(fp);
    printf("   2 more my_getc: cnt %d, read() calls still %d; the 3 bytes: %.3s\n\n",
           fp->cnt, nreads, fp->base);

    //--- 4. the rest of the file: one read per 1024 ------------------------
    n = 3;
    //IDIOM: while ((c = getc(fp)) != EOF) -- c is an int, so it can
    //hold every byte 0..255 AND the -1 that isn't a byte
    while ((c = my_getc(fp)) != EOF) {
        n++;
        if (n == 263000)        //watch the last refills
            trace = 1;
    }
    trace = 0;
    printf("4. %d characters, %d read() calls (%d full + 1 short + 1 that got 0)\n",
           n, nreads, n / MY_BUFSIZ);
    printf("   a getc FUNCTION would be %d calls; the macro called my_fillbuf %d times\n\n",
           n, nreads);

    //--- 5. EOF ---------------------------------------------------------
    r0 = nreads;
    printf("5. my_feof(fp) %d, cnt %d\n", my_feof(fp), fp->cnt);
    c = my_getc(fp);
    printf("   my_getc again -> %d, read() calls %d: the flag test stopped it, no read\n",
           c, nreads - r0);
    c = my_getc(fp);
    printf("   and again -> %d, but now cnt is %d: the early return in my_fillbuf\n"
           "   doesn't reset cnt, so every call after EOF pushes it one lower\n\n",
           c, fp->cnt);

    //--- 6. ERR ---------------------------------------------------------
    //Linux lets you open() a directory for reading, but read() on it fails
    dp = my_fopen(".", "r");
    c = my_getc(dp);
    printf("6. my_fopen(\".\", \"r\") works, my_getc -> %d; my_ferror %d, my_feof %d\n"
           "   read() returned -1 (a directory), so ERR, not EOF\n\n",
           c, my_ferror(dp), my_feof(dp));

    //--- 7. the (unsigned char) cast --------------------------------------
    MYFILE f1, f2;
    char qian[] = "\xe4\xb9\xbe";       //乾 in UTF-8
    char ff[] = "\xff";
    fake(&f1, qian, 3);
    fake(&f2, qian, 3);
    //one call per statement: the order printf's arguments are evaluated
    //in is not fixed by C, so three my_getc in one printf could run in
    //any order
    int u[3], s[3];
    for (i = 0; i < 3; i++) {
        u[i] = my_getc(&f1);
        s[i] = nocast_getc(&f2);
    }
    printf("7. 乾 is e4 b9 be. my_getc: %d %d %d   nocast_getc: %d %d %d\n",
           u[0], u[1], u[2], s[0], s[1], s[2]);
    fake(&f1, ff, 1);
    fake(&f2, ff, 1);
    c = my_getc(&f1);
    printf("   byte ff: my_getc -> %d", c);
    c = nocast_getc(&f2);
    printf(", nocast_getc -> %d %s\n", c, c == EOF ? "== EOF: a loop would stop in the middle of the data" : "");
    printf("   (char is signed here, so every byte >= 0x80 -- all of zhouyi.txt's\n"
           "   Chinese -- comes back negative without the cast)\n\n");

    //--- 8. stdin needs no fopen ---------------------------------------
    if (isatty(0))
        printf("8. stdin is the terminal: skipped (run with < zhouyi.txt)\n\n");
    else {
        r0 = nreads;
        //IDIOM: i < sizeof(line) - 1 && ... -- && stops before the
        //call: never read a character there's no room to keep
        for (i = 0; i < (int) sizeof(line) - 1 && (c = my_getchar()) != EOF && c != '\n'; i++)
            line[i] = c;
        //zhouyi.txt has Windows line endings, \r\n: the loop stopped at
        //the \n but kept the \r. Printed, \r sends the cursor back to
        //the start of the line and the closing quote lands on the "8"
        //IDIOM: i > 0 && line[i-1] -- && guards the index: never look
        //at line[-1]
        n = (i > 0 && line[i - 1] == '\r');
        if (n)
            i--;
        line[i] = '\0';
        printf("8. my_getchar(), no my_fopen: \"%s\"\n", line);
        printf("   fd %d was opened by the shell; read() calls: %d, cnt left %d\n",
               my_fileno(my_stdin), nreads - r0, my_stdin->cnt);
        if (n)
            printf("   the line ended \\r\\n (Windows): getc hands back every byte, \\r\n"
                   "   too -- Unix stdio never translates, which is why a \"b\" in the\n"
                   "   mode does nothing here. The \\r was dropped before printing\n");
        printf("\n");
    }

    //--- 9. unbuffered: one read per character -----------------------------
    up = my_fopen("zhouyi.txt", "r");
    up->flag |= M_UNBUF;            //not in the book: make it like stderr
    r0 = nreads;
    for (i = 0; i < 100; i++)
        my_getc(up);
    printf("9. with M_UNBUF set: 100 my_getc -> %d read() calls (buffered: 1)\n\n",
           nreads - r0);

    //--- 10. a macro evaluates its argument more than once -------------------
    MYFILE *fps[2];
    char a[] = "AAAA", b[] = "bbbb";
    fake(&f1, a, 4);
    fake(&f2, b, 4);
    fps[0] = &f1;
    fps[1] = &f2;
    i = 0;
    c = my_getc(fps[i++]);
    printf("10. c = my_getc(fps[i++]): c '%c', i %d -- p appears twice in the macro:\n"
           "    --fps[0]->cnt (now %d), then *fps[1]->ptr++: the wrong file's byte\n"
           "    (fps[1]->cnt is still %d, so file 1 is now out of step too)\n\n",
           c, i, f1.cnt, f2.cnt);

    //--- 11. modes ----------------------------------------------------
    n = open(DEMO, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    write(n, "0123456789", 10);
    close(n);
    ap = my_fopen(DEMO, "a");
    printf("11. %s has 10 bytes. my_fopen \"a\": position %ld -- lseek put it at the end\n",
           DEMO, (long) lseek(ap->fd, 0L, SEEK_CUR));
    my_fopen(DEMO, "w");
    stat(DEMO, &st);
    printf("    my_fopen \"w\": creat truncated it, size now %ld\n", (long) st.st_size);
    printf("    my_fopen \"x\": %s\n", my_fopen(DEMO, "x") == NULL ? "NULL" : "opened?!");
    printf("    \"r+\" -> flag %02o: only the first char is looked at, so it's just \"r\"\n\n",
           my_fopen(DEMO, "r+")->flag);
    unlink(DEMO);

    //--- 12. the table fills up --------------------------------------------
    n = 0;
    while (my_fopen("zhouyi.txt", "r") != NULL)
        n++;
    printf("12. %d more my_fopen worked, then NULL: all %d slots taken.\n"
           "    No my_fclose to free one -- that's exercise 8-3. (The kernel's own\n"
           "    limit here is far bigger: ulimit -n)\n\n", n, MY_OPEN_MAX);

    //--- 13. the real FILE ----------------------------------------------
    FILE *rf = fopen("zhouyi.txt", "r");
    getc(rf);
    printf("13. glibc: sizeof(FILE) %zu (ours %zu), BUFSIZ %d (the book's 1024);\n"
           "    after one getc the kernel position is %ld -- glibc's real buffer size\n",
           sizeof(FILE), sizeof(MYFILE), BUFSIZ, (long) lseek(fileno(rf), 0L, SEEK_CUR));
    fclose(rf);
    return 0;
}

win@DESKTOP-MEIH88T:~$ cd webdev-projects
win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c < zhouyi.txt
1. sizeof(MYFILE) = 32 bytes; my_iob[] holds 20 of them = 640 bytes
   my_iob[0]: fd 0, flag 01  READ          <- stdin
   my_iob[1]: fd 1, flag 02  WRITE         <- stdout
   my_iob[2]: fd 2, flag 06  WRITE|UNBUF   <- stderr
   my_iob[3]: fd 0, flag 00  (0 = free, like the 16 after it)
   my_stdin == &my_iob[0]: yes -- a FILE * is a pointer into this table

2. my_fopen("zhouyi.txt", "r") -> &my_iob[3]: the first free slot
   fd 3 (0, 1, 2 are taken), flag 01, cnt 0, base NULL -- nothing read yet

3. first my_getc -> 0xe5; read() calls so far: 1
   now base is malloc'd, cnt 1023, ptr - base = 1
   the kernel's position: 1024 -- it moved 1024, we used 1: two positions
   2 more my_getc: cnt 1021, read() calls still 1; the 3 bytes: 厥

   [my_fillbuf: read() returned 1024]
   [my_fillbuf: read() returned 197]
   [my_fillbuf: read() returned 0]
4. 264389 characters, 260 read() calls (258 full + 1 short + 1 that got 0)
   a getc FUNCTION would be 264389 calls; the macro called my_fillbuf 260 times

5. my_feof(fp) 1, cnt 0
   my_getc again -> -1, read() calls 0: the flag test stopped it, no read
   and again -> -1, but now cnt is -2: the early return in my_fillbuf
   doesn't reset cnt, so every call after EOF pushes it one lower

6. my_fopen(".", "r") works, my_getc -> -1; my_ferror 1, my_feof 0
   read() returned -1 (a directory), so ERR, not EOF

7. 乾 is e4 b9 be. my_getc: 228 185 190   nocast_getc: -28 -71 -66
   byte ff: my_getc -> 255, nocast_getc -> -1 == EOF: a loop would stop in the middle of the data
   (char is signed here, so every byte >= 0x80 -- all of zhouyi.txt's
   Chinese -- comes back negative without the cast)

". my_getchar(), no my_fopen: "厥孚(integrity)    貞吉凶(ultimate caution)    大有(owner)
   fd 0 was opened by the shell; read() calls: 1, cnt left 954

9. with M_UNBUF set: 100 my_getc -> 100 read() calls (buffered: 1)

10. c = my_getc(fps[i++]): c 'b', i 2 -- p appears twice in the macro:
    --fps[0]->cnt (now 3), then *fps[1]->ptr++: the wrong file's byte
    (fps[1]->cnt is still 4, so file 1 is now out of step too)

11. fopen-demo.txt has 10 bytes. my_fopen "a": position 10 -- lseek put it at the end
    my_fopen "w": creat truncated it, size now 0
    my_fopen "x": NULL
    "r+" -> flag 01: only the first char is looked at, so it's just "r"

12. 11 more my_fopen worked, then NULL: all 20 slots taken.
    No my_fclose to free one -- that's exercise 8-3. (The kernel's own
    limit here is far bigger: ulimit -n)

13. glibc: sizeof(FILE) 216 (ours 32), BUFSIZ 8192 (the book's 1024);
    after one getc the kernel position is 4096 -- glibc's real buffer size
win@DESKTOP-MEIH88T:~/webdev-projects$ echo 乾為天 | ./cc-c
1. sizeof(MYFILE) = 32 bytes; my_iob[] holds 20 of them = 640 bytes
   my_iob[0]: fd 0, flag 01  READ          <- stdin
   my_iob[1]: fd 1, flag 02  WRITE         <- stdout
   my_iob[2]: fd 2, flag 06  WRITE|UNBUF   <- stderr
   my_iob[3]: fd 0, flag 00  (0 = free, like the 16 after it)
   my_stdin == &my_iob[0]: yes -- a FILE * is a pointer into this table

2. my_fopen("zhouyi.txt", "r") -> &my_iob[3]: the first free slot
   fd 3 (0, 1, 2 are taken), flag 01, cnt 0, base NULL -- nothing read yet

3. first my_getc -> 0xe5; read() calls so far: 1
   now base is malloc'd, cnt 1023, ptr - base = 1
   the kernel's position: 1024 -- it moved 1024, we used 1: two positions
   2 more my_getc: cnt 1021, read() calls still 1; the 3 bytes: 厥

   [my_fillbuf: read() returned 1024]
   [my_fillbuf: read() returned 197]
   [my_fillbuf: read() returned 0]
4. 264389 characters, 260 read() calls (258 full + 1 short + 1 that got 0)
   a getc FUNCTION would be 264389 calls; the macro called my_fillbuf 260 times

5. my_feof(fp) 1, cnt 0
   my_getc again -> -1, read() calls 0: the flag test stopped it, no read
   and again -> -1, but now cnt is -2: the early return in my_fillbuf
   doesn't reset cnt, so every call after EOF pushes it one lower

6. my_fopen(".", "r") works, my_getc -> -1; my_ferror 1, my_feof 0
   read() returned -1 (a directory), so ERR, not EOF

7. 乾 is e4 b9 be. my_getc: 228 185 190   nocast_getc: -28 -71 -66
   byte ff: my_getc -> 255, nocast_getc -> -1 == EOF: a loop would stop in the middle of the data
   (char is signed here, so every byte >= 0x80 -- all of zhouyi.txt's
   Chinese -- comes back negative without the cast)

8. my_getchar(), no my_fopen: "乾為天"
   fd 0 was opened by the shell; read() calls: 1, cnt left 0

9. with M_UNBUF set: 100 my_getc -> 100 read() calls (buffered: 1)

10. c = my_getc(fps[i++]): c 'b', i 2 -- p appears twice in the macro:
    --fps[0]->cnt (now 3), then *fps[1]->ptr++: the wrong file's byte
    (fps[1]->cnt is still 4, so file 1 is now out of step too)

11. fopen-demo.txt has 10 bytes. my_fopen "a": position 10 -- lseek put it at the end
    my_fopen "w": creat truncated it, size now 0
    my_fopen "x": NULL
    "r+" -> flag 01: only the first char is looked at, so it's just "r"

12. 11 more my_fopen worked, then NULL: all 20 slots taken.
    No my_fclose to free one -- that's exercise 8-3. (The kernel's own
    limit here is far bigger: ulimit -n)

13. glibc: sizeof(FILE) 216 (ours 32), BUFSIZ 8192 (the book's 1024);
    after one getc the kernel position is 4096 -- glibc's real buffer size
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
1. sizeof(MYFILE) = 32 bytes; my_iob[] holds 20 of them = 640 bytes
   my_iob[0]: fd 0, flag 01  READ          <- stdin
   my_iob[1]: fd 1, flag 02  WRITE         <- stdout
   my_iob[2]: fd 2, flag 06  WRITE|UNBUF   <- stderr
   my_iob[3]: fd 0, flag 00  (0 = free, like the 16 after it)
   my_stdin == &my_iob[0]: yes -- a FILE * is a pointer into this table

2. my_fopen("zhouyi.txt", "r") -> &my_iob[3]: the first free slot
   fd 3 (0, 1, 2 are taken), flag 01, cnt 0, base NULL -- nothing read yet

3. first my_getc -> 0xe5; read() calls so far: 1
   now base is malloc'd, cnt 1023, ptr - base = 1
   the kernel's position: 1024 -- it moved 1024, we used 1: two positions
   2 more my_getc: cnt 1021, read() calls still 1; the 3 bytes: 厥

   [my_fillbuf: read() returned 1024]
   [my_fillbuf: read() returned 197]
   [my_fillbuf: read() returned 0]
4. 264389 characters, 260 read() calls (258 full + 1 short + 1 that got 0)
   a getc FUNCTION would be 264389 calls; the macro called my_fillbuf 260 times

5. my_feof(fp) 1, cnt 0
   my_getc again -> -1, read() calls 0: the flag test stopped it, no read
   and again -> -1, but now cnt is -2: the early return in my_fillbuf
   doesn't reset cnt, so every call after EOF pushes it one lower

6. my_fopen(".", "r") works, my_getc -> -1; my_ferror 1, my_feof 0
   read() returned -1 (a directory), so ERR, not EOF

7. 乾 is e4 b9 be. my_getc: 228 185 190   nocast_getc: -28 -71 -66
   byte ff: my_getc -> 255, nocast_getc -> -1 == EOF: a loop would stop in the middle of the data
   (char is signed here, so every byte >= 0x80 -- all of zhouyi.txt's
   Chinese -- comes back negative without the cast)

8. stdin is the terminal: skipped (run with < zhouyi.txt)

9. with M_UNBUF set: 100 my_getc -> 100 read() calls (buffered: 1)

10. c = my_getc(fps[i++]): c 'b', i 2 -- p appears twice in the macro:
    --fps[0]->cnt (now 3), then *fps[1]->ptr++: the wrong file's byte
    (fps[1]->cnt is still 4, so file 1 is now out of step too)

11. fopen-demo.txt has 10 bytes. my_fopen "a": position 10 -- lseek put it at the end
    my_fopen "w": creat truncated it, size now 0
    my_fopen "x": NULL
    "r+" -> flag 01: only the first char is looked at, so it's just "r"

12. 11 more my_fopen worked, then NULL: all 20 slots taken.
    No my_fclose to free one -- that's exercise 8-3. (The kernel's own
    limit here is far bigger: ulimit -n)

13. glibc: sizeof(FILE) 216 (ours 32), BUFSIZ 8192 (the book's 1024);
    after one getc the kernel position is 4096 -- glibc's real buffer size
win@DESKTOP-MEIH88T:~/webdev-projects$ wc -c zhouyi.txt
264389 zhouyi.txt
win@DESKTOP-MEIH88T:~/webdev-projects$ tr -d '\r' < zhouyi.txt | wc -c
259932
```
