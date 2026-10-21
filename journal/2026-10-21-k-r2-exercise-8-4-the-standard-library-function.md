---
title: K&R2 Exercise 8-4. The standard library function
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
//run with:     ./cc-c < zhouyi.txt         # stdin is a file: section 8 can seek it
//              echo 乾為天 | ./cc-c        # stdin is a pipe: section 8 can't
//              ./cc-c                      # stdin is the terminal: can't either

//K&R2 Exercise 8-4. The standard library function
//    int fseek(FILE *fp, long offset, int origin)
//is identical to lseek except that fp is a file pointer instead of a
//file descriptor and the return value is an int status, not a
//position. Write fseek. Make sure that your fseek coordinates properly
//with the buffering done for the other functions of the library.
//
//In plain words: fseek moves a file's position, like lseek does for an
//fd; it returns 0 if that worked, EOF if not. The catch is the buffer.
//With a buffer there are TWO positions: the kernel's (where the next
//read() or write() happens) and the program's (where the next getc or
//putc happens). Plain lseek moves only the kernel's:
//  reading: the kernel has read a whole buffer ahead -- the unread
//           bytes left in it must be thrown away, and origin 1 ("from
//           here") must mean from where the PROGRAM is
//  writing: the buffer holds bytes meant for the OLD position -- write
//           them out before moving
//
//The 8.5 and 8-3 code is here unchanged (my_ / M_ names); new:
//my_fseek, naive_fseek (plain lseek, to show what goes wrong), and
//my_ftell (where the program is -- ftell, not asked for, used by the
//printfs). main:
//  1. the two positions, after 3 getc
//  2. naive_fseek: back 3, and the file comes out 3 bytes too long
//  3. my_fseek: back to the start, back 3, the count comes out right
//  4. origin 2: from the end -- the last line of zhouyi.txt
//  5. fseek clears EOF; and the cnt < 0 trap left over from 8.5
//  6. writing: my_fseek flushes first; naive_fseek scrambles the file
//  7. a failed fseek leaves everything as it was
//  8. stdin: a file can seek, a pipe or terminal can't
//  9. fopen "a" is open + lseek here; the real one is O_APPEND

#define MY_OPEN_MAX 20
#define MY_BUFSIZ   1024
#define PERMS       0666
#define DEMO        "seek-demo.txt"     //made and unlinked by main

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

//=== 8-3: _flushbuf, fflush, fclose -- unchanged ===================

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


//=== the exercise ======================================================

//my_fseek:  move fp to offset from origin (0 start, 1 here, 2 end);
//return 0, or EOF if it can't
int my_fseek(MYFILE *fp, long offset, int origin)
{
    if ((fp->flag & (M_READ | M_WRITE)) == 0)
        return EOF;         //not an open file
    if (fp->flag & M_WRITE) {
        //DESIGN: writing -- the buffered bytes belong at the OLD
        //position: write them there first, then move
        if (my_fflush(fp) == EOF)
            return EOF;
    } else if (origin == 1 && fp->cnt > 0)
        //DESIGN: reading -- the kernel is cnt bytes ahead of the
        //program, so "from here" starts cnt bytes back.
        //The cnt > 0 test: after EOF, each extra getc leaves cnt one
        //lower (-1, -2 ... section 5 of 8.5); those aren't bytes
        offset -= fp->cnt;
    //DESIGN: lseek BEFORE touching the read buffer: if it fails, the
    //position hasn't moved and the buffer still matches it
    if (lseek(fp->fd, offset, origin) == -1)
        return EOF;
    if (fp->flag & M_READ) {
        fp->cnt = 0;            //drop the buffered bytes: next getc refills
        //IDIOM: flag &= ~A -- clear one bit, keep the rest
        fp->flag &= ~M_EOF;     //the standard: fseek clears end-of-file
    }
    return 0;
}

//=== not in the book: for main =========================================

//the obvious fseek, that forgets the buffer
int naive_fseek(MYFILE *fp, long offset, int origin)
{
    return (lseek(fp->fd, offset, origin) == -1) ? EOF : 0;
}

//my_ftell:  the program's position = the kernel's, corrected by the
//buffer: minus the unread bytes (reading), plus the unwritten (writing)
long my_ftell(MYFILE *fp)
{
    long k = lseek(fp->fd, 0L, 1);      //offset 0 from here: just ask

    if (k == -1)
        return -1;
    if (fp->flag & M_READ)
        return (fp->cnt > 0) ? k - fp->cnt : k;
    return (fp->base != NULL) ? k + (fp->ptr - fp->base) : k;
}

long size_on_disk(char *name)
{
    struct stat st;

    return (stat(name, &st) == -1) ? -1L : (long) st.st_size;
}

//read up to n-1 characters with my_getc into s, as a string
char *getn(MYFILE *fp, char *s, int n)
{
    int c, i;

    for (i = 0; i < n - 1 && (c = my_getc(fp)) != EOF; i++)
        s[i] = c;
    s[i] = '\0';
    return s;
}

//count the characters from here to EOF
long count_rest(MYFILE *fp)
{
    long n = 0;

    while (my_getc(fp) != EOF)
        n++;
    return n;
}

//a small file's whole contents, as a string; a 0 byte is shown as \0
char *contents(char *name, char *s, int n)
{
    int fd, i, j, k;
    char raw[100];

    if ((fd = open(name, O_RDONLY, 0)) == -1)
        return strcpy(s, "?");
    k = read(fd, raw, sizeof(raw));
    close(fd);
    for (i = j = 0; i < k && j < n - 3; i++)
        if (raw[i] == '\0') {
            s[j++] = '\\';
            s[j++] = '0';
        } else
            s[j++] = raw[i];
    s[j] = '\0';
    return s;
}

int main(void)
{
    MYFILE *fp, *wp;
    FILE *rf;
    int i, r;
    long n;
    char s[200], t[200];

    //--- 1. two positions ----------------------------------------------
    fp = my_fopen("zhouyi.txt", "r");
    getn(fp, s, 4);
    printf("1. 3 my_getc: \"%s\" (3 bytes of UTF-8)\n", s);
    printf("   program at %ld (my_ftell), kernel at %ld (lseek), %d bytes waiting\n\n",
           my_ftell(fp), (long) lseek(fp->fd, 0L, 1), fp->cnt);
    my_fclose(fp);

    //--- 2. naive ------------------------------------------------------
    fp = my_fopen("zhouyi.txt", "r");
    getn(fp, s, 4);
    naive_fseek(fp, -3L, 1);
    printf("2. naive_fseek(fp, -3, 1), meant \"back to 厥\": next 3 bytes \"%s\"\n",
           getn(fp, s, 4));
    printf("   the kernel went from 1024 back to 1021; the buffer didn't notice\n");
    n = 6 + count_rest(fp);
    printf("   reading on to EOF: %ld bytes in all, the file has %ld -- the next\n"
           "   refill started at 1021, so 3 bytes came twice\n\n",
           n, size_on_disk("zhouyi.txt"));
    my_fclose(fp);

    //--- 3. my_fseek ---------------------------------------------------
    fp = my_fopen("zhouyi.txt", "r");
    getn(fp, s, 4);
    r = my_fseek(fp, -3L, 1);
    //one printf per state: getn changes cnt and the position, and the
    //order printf's arguments are evaluated in isn't fixed
    printf("3. my_fseek(fp, -3, 1) -> %d: kernel to %ld (1024 - 1021 waiting - 3), cnt %d\n",
           r, (long) lseek(fp->fd, 0L, 1), fp->cnt);
    printf("   next 3 bytes \"%s\"\n", getn(fp, s, 4));
    n = 3 + count_rest(fp);
    printf("   reading on to EOF: %ld bytes in all, right\n", n);
    r = my_fseek(fp, 0L, 0);
    printf("   my_fseek(fp, 0, 0) -> %d: \"%s\" -- the start again\n\n",
           r, getn(fp, s, 4));

    //--- 4. from the end -----------------------------------------------
    //zhouyi.txt ends with its last line, then 7 empty lines (\r\n each):
    //the line starts 34 bytes before the end
    r = my_fseek(fp, -34L, 2);
    getn(fp, s, 40);
    s[strcspn(s, "\r")] = '\0';     //cut at the \r: the line alone
    printf("4. my_fseek(fp, -34, 2) -> %d: \"%s\" -- the last hexagram\n\n", r, s);

    //--- 5. EOF --------------------------------------------------------
    count_rest(fp);
    my_getc(fp);
    my_getc(fp);
    printf("5. read to EOF, then 2 more my_getc: feof %d, cnt %d, my_ftell %ld\n",
           my_feof(fp), fp->cnt, my_ftell(fp));
    r = my_fseek(fp, 0L, 1);
    printf("   my_fseek(fp, 0, 1) -> %d: kernel at %ld, not %ld -- the cnt > 0\n"
           "   test kept -2 from being taken as \"2 bytes ahead\"\n",
           r, (long) lseek(fp->fd, 0L, 1), size_on_disk("zhouyi.txt") + 2);
    printf("   feof now %d", my_feof(fp));
    printf(": so my_getc reads again, and gets %d (still the end)\n\n", my_getc(fp));
    my_fclose(fp);

    //--- 6. writing ----------------------------------------------------
    wp = my_fopen(DEMO, "w");
    for (i = 0; i < 10; i++)
        my_putc('0' + i, wp);
    printf("6. \"0123456789\" with my_putc: %ld bytes on disk, 10 in the buffer\n",
           size_on_disk(DEMO));
    r = my_fseek(wp, 2L, 0);
    printf("   my_fseek(wp, 2, 0) -> %d: %ld bytes on disk -- flushed first\n",
           r, size_on_disk(DEMO));
    my_putc('X', wp);
    my_putc('Y', wp);
    my_fclose(wp);
    printf("   2 my_putc, my_fclose: \"%s\"\n", contents(DEMO, s, sizeof(s)));
    wp = my_fopen(DEMO, "w");
    for (i = 0; i < 10; i++)
        my_putc('0' + i, wp);
    naive_fseek(wp, 2L, 0);
    my_putc('X', wp);
    my_putc('Y', wp);
    my_fclose(wp);
    printf("   the same with naive_fseek: \"%s\" (%ld bytes)\n",
           contents(DEMO, s, sizeof(s)), size_on_disk(DEMO));
    printf("   the digits were still in the buffer when lseek moved to 2, so all\n"
           "   12 bytes went out at close, starting at 2 -- and the 2 bytes never\n"
           "   written read back as zeros: a hole\n\n");

    //--- 7. a failed fseek -------------------------------------------
    fp = my_fopen("zhouyi.txt", "r");
    getn(fp, s, 4);
    r = my_fseek(fp, -10L, 0);
    printf("7. my_fseek(fp, -10, 0) -> %d: a position before the start\n", r);
    r = my_fseek(fp, 0L, 7);
    printf("   my_fseek(fp, 0, 7) -> %d: no origin 7\n", r);
    printf("   still at %ld, cnt %d", my_ftell(fp), fp->cnt);
    printf(": next 3 bytes \"%s\" as if nothing happened\n", getn(fp, s, 4));
    my_fclose(fp);
    printf("   my_fseek on it after my_fclose -> %d\n\n", my_fseek(fp, 0L, 0));

    //--- 8. stdin ------------------------------------------------------
    getn(my_stdin, s, 4);
    r = my_fseek(my_stdin, 0L, 0);
    if (r == 0)
        printf("8. stdin: read \"%s\", my_fseek(my_stdin, 0, 0) -> 0, read \"%s\"\n"
               "   again: stdin is a file, and a file has positions\n\n",
               s, getn(my_stdin, t, 4));
    else
        printf("8. stdin: my_fseek(my_stdin, 0, 0) -> %d: a pipe or a terminal has\n"
               "   no positions -- bytes go by once, and lseek fails\n\n", r);

    //--- 9. append ---------------------------------------------------
    wp = my_fopen(DEMO, "w");
    for (i = 0; i < 10; i++)
        my_putc('0' + i, wp);
    my_fclose(wp);
    wp = my_fopen(DEMO, "a");
    my_fseek(wp, 0L, 0);
    my_putc('A', wp);
    my_fclose(wp);
    printf("9. \"0123456789\", my_fopen \"a\", my_fseek(wp, 0, 0), my_putc('A'):\n"
           "   \"%s\" -- the A landed at the start\n", contents(DEMO, s, sizeof(s)));
    rf = fopen(DEMO, "a");
    fseek(rf, 0L, SEEK_SET);
    putc('B', rf);
    fclose(rf);
    printf("   the real fopen \"a\", fseek(rf, 0, SEEK_SET), putc('B'):\n"
           "   \"%s\" -- glibc opens with O_APPEND: every write() goes to the\n"
           "   end, wherever the position is\n", contents(DEMO, s, sizeof(s)));
    unlink(DEMO);
    return 0;
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c < zhouyi.txt
1. 3 my_getc: "厥" (3 bytes of UTF-8)
   program at 3 (my_ftell), kernel at 1024 (lseek), 1021 bytes waiting

2. naive_fseek(fp, -3, 1), meant "back to 厥": next 3 bytes "孚"
   the kernel went from 1024 back to 1021; the buffer didn't notice
   reading on to EOF: 264392 bytes in all, the file has 264389 -- the next
   refill started at 1021, so 3 bytes came twice

3. my_fseek(fp, -3, 1) -> 0: kernel to 0 (1024 - 1021 waiting - 3), cnt 0
   next 3 bytes "厥"
   reading on to EOF: 264389 bytes in all, right
   my_fseek(fp, 0, 0) -> 0: "厥" -- the start again

4. my_fseek(fp, -34, 2) -> 0: "64 未濟 (wèi jì)" -- the last hexagram

5. read to EOF, then 2 more my_getc: feof 1, cnt -3, my_ftell 264389
   my_fseek(fp, 0, 1) -> 0: kernel at 264389, not 264391 -- the cnt > 0
   test kept -2 from being taken as "2 bytes ahead"
   feof now 0: so my_getc reads again, and gets -1 (still the end)

6. "0123456789" with my_putc: 0 bytes on disk, 10 in the buffer
   my_fseek(wp, 2, 0) -> 0: 10 bytes on disk -- flushed first
   2 my_putc, my_fclose: "01XY456789"
   the same with naive_fseek: "\0\00123456789XY" (14 bytes)
   the digits were still in the buffer when lseek moved to 2, so all
   12 bytes went out at close, starting at 2 -- and the 2 bytes never
   written read back as zeros: a hole

7. my_fseek(fp, -10, 0) -> -1: a position before the start
   my_fseek(fp, 0, 7) -> -1: no origin 7
   still at 3, cnt 1021: next 3 bytes "孚" as if nothing happened
   my_fseek on it after my_fclose -> -1

8. stdin: read "厥", my_fseek(my_stdin, 0, 0) -> 0, read "厥"
   again: stdin is a file, and a file has positions

9. "0123456789", my_fopen "a", my_fseek(wp, 0, 0), my_putc('A'):
   "A123456789" -- the A landed at the start
   the real fopen "a", fseek(rf, 0, SEEK_SET), putc('B'):
   "A123456789B" -- glibc opens with O_APPEND: every write() goes to the
   end, wherever the position is
win@DESKTOP-MEIH88T:~/webdev-projects$ echo 乾為天 | ./cc-c
1. 3 my_getc: "厥" (3 bytes of UTF-8)
   program at 3 (my_ftell), kernel at 1024 (lseek), 1021 bytes waiting

2. naive_fseek(fp, -3, 1), meant "back to 厥": next 3 bytes "孚"
   the kernel went from 1024 back to 1021; the buffer didn't notice
   reading on to EOF: 264392 bytes in all, the file has 264389 -- the next
   refill started at 1021, so 3 bytes came twice

3. my_fseek(fp, -3, 1) -> 0: kernel to 0 (1024 - 1021 waiting - 3), cnt 0
   next 3 bytes "厥"
   reading on to EOF: 264389 bytes in all, right
   my_fseek(fp, 0, 0) -> 0: "厥" -- the start again

4. my_fseek(fp, -34, 2) -> 0: "64 未濟 (wèi jì)" -- the last hexagram

5. read to EOF, then 2 more my_getc: feof 1, cnt -3, my_ftell 264389
   my_fseek(fp, 0, 1) -> 0: kernel at 264389, not 264391 -- the cnt > 0
   test kept -2 from being taken as "2 bytes ahead"
   feof now 0: so my_getc reads again, and gets -1 (still the end)

6. "0123456789" with my_putc: 0 bytes on disk, 10 in the buffer
   my_fseek(wp, 2, 0) -> 0: 10 bytes on disk -- flushed first
   2 my_putc, my_fclose: "01XY456789"
   the same with naive_fseek: "\0\00123456789XY" (14 bytes)
   the digits were still in the buffer when lseek moved to 2, so all
   12 bytes went out at close, starting at 2 -- and the 2 bytes never
   written read back as zeros: a hole

7. my_fseek(fp, -10, 0) -> -1: a position before the start
   my_fseek(fp, 0, 7) -> -1: no origin 7
   still at 3, cnt 1021: next 3 bytes "孚" as if nothing happened
   my_fseek on it after my_fclose -> -1

8. stdin: my_fseek(my_stdin, 0, 0) -> -1: a pipe or a terminal has
   no positions -- bytes go by once, and lseek fails

9. "0123456789", my_fopen "a", my_fseek(wp, 0, 0), my_putc('A'):
   "A123456789" -- the A landed at the start
   the real fopen "a", fseek(rf, 0, SEEK_SET), putc('B'):
   "A123456789B" -- glibc opens with O_APPEND: every write() goes to the
   end, wherever the position is
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c
1. 3 my_getc: "厥" (3 bytes of UTF-8)
   program at 3 (my_ftell), kernel at 1024 (lseek), 1021 bytes waiting

2. naive_fseek(fp, -3, 1), meant "back to 厥": next 3 bytes "孚"
   the kernel went from 1024 back to 1021; the buffer didn't notice
   reading on to EOF: 264392 bytes in all, the file has 264389 -- the next
   refill started at 1021, so 3 bytes came twice

3. my_fseek(fp, -3, 1) -> 0: kernel to 0 (1024 - 1021 waiting - 3), cnt 0
   next 3 bytes "厥"
   reading on to EOF: 264389 bytes in all, right
   my_fseek(fp, 0, 0) -> 0: "厥" -- the start again

4. my_fseek(fp, -34, 2) -> 0: "64 未濟 (wèi jì)" -- the last hexagram

5. read to EOF, then 2 more my_getc: feof 1, cnt -3, my_ftell 264389
   my_fseek(fp, 0, 1) -> 0: kernel at 264389, not 264391 -- the cnt > 0
   test kept -2 from being taken as "2 bytes ahead"
   feof now 0: so my_getc reads again, and gets -1 (still the end)

6. "0123456789" with my_putc: 0 bytes on disk, 10 in the buffer
   my_fseek(wp, 2, 0) -> 0: 10 bytes on disk -- flushed first
   2 my_putc, my_fclose: "01XY456789"
   the same with naive_fseek: "\0\00123456789XY" (14 bytes)
   the digits were still in the buffer when lseek moved to 2, so all
   12 bytes went out at close, starting at 2 -- and the 2 bytes never
   written read back as zeros: a hole

7. my_fseek(fp, -10, 0) -> -1: a position before the start
   my_fseek(fp, 0, 7) -> -1: no origin 7
   still at 3, cnt 1021: next 3 bytes "孚" as if nothing happened
   my_fseek on it after my_fclose -> -1
```
