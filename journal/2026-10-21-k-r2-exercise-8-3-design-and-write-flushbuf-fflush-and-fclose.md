---
title: K&R2 Exercise 8-3. Design and write _flushbuf, fflush, and fclose
date: 2026-10-21
---

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c

//K&R2 Exercise 8-3. Design and write _flushbuf, fflush, and fclose.
//
//In plain words: 8.5 built the READING half of stdio (getc and
//_fillbuf). This is the WRITING half:
//  _flushbuf  what the putc macro calls when the output buffer is full
//             -- the mirror of _fillbuf
//  fflush     write out whatever is waiting in the buffer, now
//  fclose     flush, give back the buffer, close the fd, free the slot
//             in the table (8.5 had no way to free one: full after 20)
//"Design" means the book leaves the decisions to you. Each one is
//marked DESIGN: below.
//
//The 8.5 code (fopen, _fillbuf, getc) is here unchanged, with the
//my_ / M_ names; the book's putc macro is added. main:
//  1. the first putc: cnt 0 sends it to _flushbuf, which mallocs
//  2. 2500 putc: write() runs at 1025 and 2049 -- the file on disk is
//     behind what the program has "written"
//  3. fflush catches the file up
//  4. unbuffered (stderr): one write() per putc, at once
//  5. buffered stdout: a line sits in the buffer until fflush
//  6. without fclose the bytes never reach the file -- the real exit()
//     flushes every FILE; it doesn't know our table exists
//  7. fclose frees the slot: 100 fopen/fclose pairs, same fd every time
//  8. fclose on a read file, fclose twice, fflush(NULL)
//  9. errors: putc on a read file; /dev/full makes every write() fail
// 10. the book's putc macro returns -1 for byte 0xff (the 8.5 cast
//     problem, from the writing side)

#define MY_OPEN_MAX 20
#define MY_BUFSIZ   1024
#define PERMS       0666
#define DEMO        "flush-demo.txt"    //made and unlinked by main

typedef struct my_iobuf {
    int   cnt;      //reading: characters left; writing: space left
    char *ptr;      //next character position
    char *base;     //location of buffer
    int   flag;     //mode of file access
    int   fd;       //file descriptor
} MYFILE;

enum my_flags {
    M_READ  = 01,
    M_WRITE = 02,
    M_UNBUF = 04,
    M_EOF   = 010,
    M_ERR   = 020
};

MYFILE my_iob[MY_OPEN_MAX] = {
    { 0, (char *) 0, (char *) 0, M_READ, 0 },
    { 0, (char *) 0, (char *) 0, M_WRITE, 1 },
    { 0, (char *) 0, (char *) 0, M_WRITE | M_UNBUF, 2 }
};

#define my_stdin  (&my_iob[0])
#define my_stdout (&my_iob[1])
#define my_stderr (&my_iob[2])

int my_fillbuf(MYFILE *);
int my_flushbuf(int, MYFILE *);
int my_fflush(MYFILE *);

#define my_feof(p)   (((p)->flag & M_EOF) != 0)
#define my_ferror(p) (((p)->flag & M_ERR) != 0)

#define my_getc(p) (--(p)->cnt >= 0 \
                   ? (unsigned char) *(p)->ptr++ : my_fillbuf(p))
//the book's putc, from 8.5. For writing, cnt counts SPACE left: while
//there is room, store x and move on; when cnt goes below 0, the buffer
//is full and _flushbuf takes over
#define my_putc(x,p) (--(p)->cnt >= 0 \
                     ? *(p)->ptr++ = (x) : my_flushbuf((x),p))
#define my_putchar(x) my_putc((x), my_stdout)

int nwrites = 0;    //not in the book: how many times write() was called

//my_fopen:  open file, return file ptr -- 8.5, unchanged
MYFILE *my_fopen(char *name, char *mode)
{
    int fd;
    MYFILE *fp;

    if (*mode != 'r' && *mode != 'w' && *mode != 'a')
        return NULL;
    for (fp = my_iob; fp < my_iob + MY_OPEN_MAX; fp++)
        if ((fp->flag & (M_READ | M_WRITE)) == 0)
            break;
    if (fp >= my_iob + MY_OPEN_MAX)
        return NULL;

    if (*mode == 'w')
        fd = creat(name, PERMS);
    else if (*mode == 'a') {
        if ((fd = open(name, O_WRONLY, 0)) == -1)
            fd = creat(name, PERMS);
        lseek(fd, 0L, 2);
    } else
        fd = open(name, O_RDONLY, 0);
    if (fd == -1)
        return NULL;
    fp->fd = fd;
    fp->cnt = 0;
    fp->base = NULL;
    fp->flag = (*mode == 'r') ? M_READ : M_WRITE;
    return fp;
}

//my_fillbuf:  allocate and fill input buffer -- 8.5, unchanged
int my_fillbuf(MYFILE *fp)
{
    int bufsize;

    if ((fp->flag & (M_READ | M_EOF | M_ERR)) != M_READ)
        return EOF;
    bufsize = (fp->flag & M_UNBUF) ? 1 : MY_BUFSIZ;
    if (fp->base == NULL)
        if ((fp->base = (char *) malloc(bufsize)) == NULL)
            return EOF;
    fp->ptr = fp->base;
    fp->cnt = read(fp->fd, fp->ptr, bufsize);
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

//=== the exercise ======================================================

//my_flushbuf:  allocate or flush output buffer, then store c in it
int my_flushbuf(int c, MYFILE *fp)
{
    unsigned char uc = c;

    //IDIOM: (flag & (A|B)) != A -- "A set, B clear", the _fillbuf test
    //for writing: open for writing, and no error so far
    if ((fp->flag & (M_WRITE | M_ERR)) != M_WRITE)
        return EOF;
    //DESIGN: unbuffered means no buffer at all -- write c right now.
    //(Giving it a 1-byte buffer, like _fillbuf does, would leave every
    //character sitting there until the NEXT putc: stderr would always
    //be one character behind)
    if (fp->flag & M_UNBUF) {
        nwrites++;                          //not in the book
        if (write(fp->fd, &uc, 1) != 1) {
            fp->flag |= M_ERR;
            return EOF;
        }
        fp->cnt = 0;        //so the next putc comes straight back here
        return uc;
    }
    //DESIGN: first time, get a buffer; after that, a full buffer is
    //exactly what fflush empties -- so call it, don't write it twice
    if (fp->base == NULL) {
        if ((fp->base = (char *) malloc(MY_BUFSIZ)) == NULL) {
            fp->flag |= M_ERR;
            return EOF;
        }
    } else if (my_fflush(fp) == EOF)
        return EOF;
    fp->ptr = fp->base;
    *fp->ptr++ = uc;
    fp->cnt = MY_BUFSIZ - 1;    //one place used by c
    //DESIGN: return c as unsigned char, like _fillbuf -- so byte 0xff
    //is 255 here, never EOF (section 10: the macro's other path isn't)
    return uc;
}

//my_fflush:  write out a file's buffered output; NULL means all files
int my_fflush(MYFILE *fp)
{
    int n, rc;

    //DESIGN: fflush(NULL) flushes every file open for writing, as in
    //Appendix B; one failure makes the whole call return EOF, but the
    //loop still tries every file
    if (fp == NULL) {
        rc = 0;
        for (fp = my_iob; fp < my_iob + MY_OPEN_MAX; fp++)
            if ((fp->flag & M_WRITE) && my_fflush(fp) == EOF)
                rc = EOF;
        return rc;
    }
    //DESIGN: on a file open for reading the standard says the effect is
    //undefined; here it does nothing and succeeds. A slot that isn't
    //open at all is an error
    if ((fp->flag & M_WRITE) == 0)
        return (fp->flag & M_READ) ? 0 : EOF;
    if (fp->flag & M_ERR)
        return EOF;
    //IDIOM: ptr - base -- two pointers into one buffer: subtracting
    //them counts the characters stored so far
    if (fp->base != NULL && (n = fp->ptr - fp->base) > 0) {
        nwrites++;                          //not in the book
        if (write(fp->fd, fp->base, n) != n) {
            fp->flag |= M_ERR;
            return EOF;
        }
    }
    fp->ptr = fp->base;
    //no buffer yet (or unbuffered): cnt 0, so the next putc calls
    //_flushbuf; otherwise the whole buffer is free again
    fp->cnt = (fp->base == NULL) ? 0 : MY_BUFSIZ;
    return 0;
}

//my_fclose:  flush, free the buffer, close the fd, free the slot
int my_fclose(MYFILE *fp)
{
    int rc = 0;

    //DESIGN: refuse anything that isn't an open slot of the table --
    //NULL, a stray pointer, or a file already closed
    if (fp == NULL || fp < my_iob || fp >= my_iob + MY_OPEN_MAX
            || (fp->flag & (M_READ | M_WRITE)) == 0)
        return EOF;
    //DESIGN: a failed flush or close still frees the slot -- the file
    //is closed either way; the EOF tells the caller data may be lost
    if ((fp->flag & M_WRITE) && my_fflush(fp) == EOF)
        rc = EOF;
    if (close(fp->fd) == -1)
        rc = EOF;
    //IDIOM: free(NULL) is allowed and does nothing -- no need to test
    //base first
    free(fp->base);
    fp->base = fp->ptr = NULL;
    fp->cnt = 0;
    fp->flag = 0;       //flag 0: the slot is free for my_fopen again
    fp->fd = -1;
    return rc;
}

//=== not in the book: for main =========================================

long size_on_disk(char *name)
{
    struct stat st;

    return (stat(name, &st) == -1) ? -1L : (long) st.st_size;
}

int main(void)
{
    MYFILE *fp, *rp;
    int c, i, n, w0, fd;
    char *s;

    //the real stdout has its own buffer, separate from ours. Turn it
    //off, so printf output and our write()s reach the screen in the
    //order the program makes them
    setbuf(stdout, NULL);

    //--- 1. the first putc --------------------------------------------
    fp = my_fopen(DEMO, "w");
    printf("1. my_fopen(\"%s\", \"w\"): cnt %d, base %s\n",
           DEMO, fp->cnt, fp->base == NULL ? "NULL" : "set");
    my_putc('A', fp);
    printf("   my_putc('A'): --cnt is -1, so my_flushbuf: malloc, 'A' stored,\n"
           "   cnt now %d, ptr - base %td, write() calls %d\n\n",
           fp->cnt, fp->ptr - fp->base, nwrites);

    //--- 2. 2500 putc --------------------------------------------------
    for (i = 1; i < 2500; i++) {
        w0 = nwrites;
        my_putc('A' + i % 26, fp);
        if (nwrites != w0)
            printf("2. putc #%d found the buffer full: write() #%d, %ld bytes on disk\n",
                   i + 1, nwrites, size_on_disk(DEMO));
    }
    printf("   2500 putc done: %ld bytes on disk, %td still in the buffer\n\n",
           size_on_disk(DEMO), fp->ptr - fp->base);

    //--- 3. fflush ---------------------------------------------------
    n = my_fflush(fp);
    printf("3. my_fflush -> %d: %ld bytes on disk, write() calls %d, cnt %d (all free)\n\n",
           n, size_on_disk(DEMO), nwrites, fp->cnt);
    my_fclose(fp);

    //--- 4. unbuffered -----------------------------------------------
    w0 = nwrites;
    printf("4. \"zhouyi\\n\" to my_stderr, 7 my_putc: ");
    for (s = "zhouyi\n"; *s; s++)
        my_putc(*s, my_stderr);
    printf("   write() calls %d -- one per character, nothing waits\n\n",
           nwrites - w0);

    //--- 5. buffered stdout ------------------------------------------
    printf("5. \"hidden until fflush\\n\" to my_stdout with my_putchar...\n");
    for (s = "   hidden until fflush\n"; *s; s++)
        my_putchar(*s);
    printf("   ...done, and nothing on the screen yet: %td bytes in the buffer\n",
           my_stdout->ptr - my_stdout->base);
    printf("   now my_fflush(my_stdout):\n");
    my_fflush(my_stdout);
    printf("   (a real stdout on a terminal also flushes at every \\n --\n"
           "   line buffering, which this version doesn't have)\n\n");

    //--- 6. no fclose, no data ---------------------------------------
    fp = my_fopen(DEMO, "w");
    for (i = 0; i < 100; i++)
        my_putc('x', fp);
    printf("6. 100 my_putc, no fclose: %ld bytes on disk. If main returned\n"
           "   now, they'd be gone: the real exit() flushes the real FILEs,\n"
           "   and our my_iob means nothing to it\n", size_on_disk(DEMO));
    n = my_fclose(fp);
    printf("   my_fclose -> %d: %ld bytes on disk\n\n", n, size_on_disk(DEMO));

    //--- 7. slots come back ------------------------------------------
    printf("7. 100 x (my_fopen + 3 my_getc + my_fclose) on zhouyi.txt:");
    for (i = 0; i < 100; i++) {
        if ((rp = my_fopen("zhouyi.txt", "r")) == NULL)
            break;
        my_getc(rp);
        my_getc(rp);
        my_getc(rp);
        if (i < 3)
            printf(" &my_iob[%td] fd %d,", rp - my_iob, rp->fd);
        fd = rp->fd;
        my_fclose(rp);
    }
    printf(" ...\n   all %d worked (8.5 ran out at 20), the last one: fd %d too --\n"
           "   the kernel reuses the lowest free number, like my_fopen's slots\n\n",
           i, fd);

    //--- 8. the other cases -------------------------------------------
    rp = my_fopen("zhouyi.txt", "r");
    my_getc(rp);
    printf("8. my_fflush on a read file -> %d (does nothing)\n", my_fflush(rp));
    //two calls, two statements: in one printf their order isn't fixed
    n = my_fclose(rp);
    c = my_fclose(rp);
    printf("   my_fclose on it -> %d, nothing to flush; again -> %d: already closed\n",
           n, c);
    printf("   my_fclose(NULL) -> %d\n", my_fclose(NULL));
    fp = my_fopen(DEMO, "a");
    for (s = "|appended"; *s; s++)
        my_putc(*s, fp);
    w0 = nwrites;
    n = my_fflush(NULL);
    printf("   9 bytes appended, my_fflush(NULL) -> %d: %d write() for the whole\n"
           "   table, %ld bytes on disk\n", n, nwrites - w0, size_on_disk(DEMO));
    my_fclose(fp);
    printf("\n");

    //--- 9. errors ---------------------------------------------------
    rp = my_fopen("zhouyi.txt", "r");
    c = my_putc('x', rp);
    printf("9. my_putc on a file opened \"r\" -> %d: no M_WRITE, so EOF\n", c);
    my_fclose(rp);
    //Linux's /dev/full accepts open, and every write() fails: "no
    //space left on device" -- a full disk, on demand
    fp = my_fopen("/dev/full", "w");
    for (i = 0; i < 1024; i++)
        my_putc('x', fp);
    printf("   /dev/full: 1024 my_putc all fit in the buffer, ferror %d -- no\n"
           "   write() yet, so nothing has failed yet\n", my_ferror(fp));
    c = my_putc('x', fp);
    printf("   putc #1025 -> %d, ferror %d: the flush failed\n", c, my_ferror(fp));
    c = my_putc('x', fp);
    printf("   putc #1026 -> %d: M_ERR stops every write from now on\n", c);
    my_fclose(fp);
    fp = my_fopen("/dev/full", "w");
    my_putc('x', fp);
    n = my_fclose(fp);
    printf("   another file on /dev/full, 1 putc, my_fclose -> %d: the putc\n"
           "   \"worked\", the data was lost at close -- only fclose's return\n"
           "   value says so\n\n", n);

    //--- 10. the book's putc and byte 0xff ----------------------------
    fp = my_fopen(DEMO, "w");
    c = my_putc('\xff', fp);
    printf("10. first my_putc('\\xff') -> %d (via my_flushbuf: unsigned char)\n", c);
    c = my_putc('\xff', fp);
    printf("    second one -> %d (via the macro's *(p)->ptr++ = (x): char is\n"
           "    signed here, so 0xff is -1 == EOF). A loop doing\n"
           "    if (putc(c, fp) == EOF) would call a good write an error.\n"
           "    The fix: (unsigned char) (*(p)->ptr++ = (x)), as in 8.5's getc\n", c);
    my_fclose(fp);
    unlink(DEMO);
    return 0;
}


win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
1. my_fopen("flush-demo.txt", "w"): cnt 0, base NULL
   my_putc('A'): --cnt is -1, so my_flushbuf: malloc, 'A' stored,
   cnt now 1023, ptr - base 1, write() calls 0

2. putc #1025 found the buffer full: write() #1, 1024 bytes on disk
2. putc #2049 found the buffer full: write() #2, 2048 bytes on disk
   2500 putc done: 2048 bytes on disk, 452 still in the buffer

3. my_fflush -> 0: 2500 bytes on disk, write() calls 3, cnt 1024 (all free)

4. "zhouyi\n" to my_stderr, 7 my_putc: zhouyi
   write() calls 7 -- one per character, nothing waits

5. "hidden until fflush\n" to my_stdout with my_putchar...
   ...done, and nothing on the screen yet: 23 bytes in the buffer
   now my_fflush(my_stdout):
   hidden until fflush
   (a real stdout on a terminal also flushes at every \n --
   line buffering, which this version doesn't have)

6. 100 my_putc, no fclose: 0 bytes on disk. If main returned
   now, they'd be gone: the real exit() flushes the real FILEs,
   and our my_iob means nothing to it
   my_fclose -> 0: 100 bytes on disk

7. 100 x (my_fopen + 3 my_getc + my_fclose) on zhouyi.txt: &my_iob[3] fd 3, &my_iob[3] fd 3, &my_iob[3] fd 3, ...
   all 100 worked (8.5 ran out at 20), the last one: fd 3 too --
   the kernel reuses the lowest free number, like my_fopen's slots

8. my_fflush on a read file -> 0 (does nothing)
   my_fclose on it -> 0, nothing to flush; again -> -1: already closed
   my_fclose(NULL) -> -1
   9 bytes appended, my_fflush(NULL) -> 0: 1 write() for the whole
   table, 109 bytes on disk

9. my_putc on a file opened "r" -> -1: no M_WRITE, so EOF
   /dev/full: 1024 my_putc all fit in the buffer, ferror 0 -- no
   write() yet, so nothing has failed yet
   putc #1025 -> -1, ferror 1: the flush failed
   putc #1026 -> -1: M_ERR stops every write from now on
   another file on /dev/full, 1 putc, my_fclose -> -1: the putc
   "worked", the data was lost at close -- only fclose's return
   value says so

10. first my_putc('\xff') -> 255 (via my_flushbuf: unsigned char)
    second one -> -1 (via the macro's *(p)->ptr++ = (x): char is
    signed here, so 0xff is -1 == EOF). A loop doing
    if (putc(c, fp) == EOF) would call a good write an error.
    The fix: (unsigned char) (*(p)->ptr++ = (x)), as in 8.5's getc
```
