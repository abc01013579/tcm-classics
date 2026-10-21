---
title: K&R2 Exercise 8-5. Modify the fsize program
date: 2026-10-21
---

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>               //localtime, strftime
#include <fcntl.h>              //flags for read and write
#include <unistd.h>             //open, close, syscall
#include <sys/syscall.h>        //SYS_getdents64
#include <sys/types.h>          //typedefs
#include <sys/stat.h>           //structure returned by stat
#include <sys/sysmacros.h>      //major, minor
//compile with: gcc -Wall -Wextra cc-c.c -o cc-c
//run with:     ./cc-c learning-unixcommands-cc
//              ./cc-c learning-unixcommands-cc    # compare
//              ./cc-c /usr/bin/passwd /dev/tty /dev/sda /dev/null zhouyi.txt
//              ./cc-c | tail -4      # the book's default "." -- walks .venv too: ~70,000 files

//K&R2 Exercise 8-5. Modify the fsize program to print the other
//information contained in the inode entry.
//
//In plain words: fsize prints only st_size. stat fills in the whole
//struct stat -- every field of the book's list is printed now, two
//lines per file:
//  line 1, like ls -lin:  ino  mode  nlink  uid  gid  size  mtime  name
//  line 2, the rest:      dev  rdev (devices only)  atime  ctime
//
//  mode  the type letter and the 9 rwx bits, as ls draws them:
//        - regular  d directory  c char special  b block special
//        s/S t/T for the setuid, setgid and sticky bits
//  size  for a char or block device, ls shows "major, minor" (the
//        driver number and which device) instead -- st_rdev; so does this
//  uid, gid  numbers: the inode holds only numbers; ls -l looks the
//        names up in /etc/passwd and /etc/group (ls -n doesn't)
//  times  atime: last read  mtime: contents last changed  ctime: the
//        INODE last changed (chmod, ln, mv...) -- the book's "time
//        originally created" is wrong: Unix keeps no creation time
//
//dirwalk, my_opendir, my_readdir, my_closedir are the 8.6 block's,
//unchanged; only fsize is new.

#define MY_NAME_MAX 255     //longest filename component on Linux (book: 14)
#define MAX_PATH    1024

typedef struct {            //portable directory entry
    long ino;                   //inode number
    char name[MY_NAME_MAX+1];   //name + '\0' terminator
} Dirent;

typedef struct {            //minimal DIR: one buffer of raw records
    int  fd;                    //file descriptor for the directory
    long long buf[512];         //records from getdents64; long long: 8-byte aligned
    int  nbuf;                  //bytes in buf
    int  pos;                   //where the next record starts
} MYDIR;

struct linux_dirent64 {     //what getdents64 fills in -- Linux's struct direct
    unsigned long long d_ino;   //inode number
    long long          d_off;   //where the NEXT entry is
    unsigned short     d_reclen;//length of this record, padded to 8
    unsigned char      d_type;  //file type: a Linux extra, saves a stat
    char               d_name[];//name + '\0' -- as long as it needs
};

MYDIR  *my_opendir(char *dirname);
Dirent *my_readdir(MYDIR *dfd);
void    my_closedir(MYDIR *dfd);
void fsize(char *);
void dirwalk(char *, void (*fcn)(char *));
void mode_string(mode_t m, char *s);
char *timestr(time_t t);

int main(int argc, char **argv)
{
    if (argc == 1)      //default: current directory
        fsize(".");
    else
        //IDIOM: while (--argc > 0) f(*++argv) -- visit each argument,
        //skipping argv[0], the program's name
        while (--argc > 0)
            fsize(*++argv);
    return 0;
}

//fsize: print the inode information of file "name"
void fsize(char *name)
{
    struct stat stbuf;
    char mode[11];
    int type;

    if (stat(name, &stbuf) == -1) {
        fprintf(stderr, "fsize: can't access %s\n", name);
        return;
    }
    type = stbuf.st_mode & S_IFMT;
    if (type == S_IFDIR)
        dirwalk(name, fsize);

    mode_string(stbuf.st_mode, mode);
    printf("%8lu %s %3lu %5u %5u ", (unsigned long) stbuf.st_ino, mode,
           (unsigned long) stbuf.st_nlink, stbuf.st_uid, stbuf.st_gid);
    if (type == S_IFCHR || type == S_IFBLK)     //a device: no size, a number
        printf("%3u, %3u", major(stbuf.st_rdev), minor(stbuf.st_rdev));
    else
        printf("%8ld", (long) stbuf.st_size);
    printf(" %s %s\n", timestr(stbuf.st_mtime), name);

    printf("%8s dev %u,%u  atime %s  ctime %s\n", "",
           major(stbuf.st_dev), minor(stbuf.st_dev),
           timestr(stbuf.st_atime), timestr(stbuf.st_ctime));
}

//mode_string: "drwxr-xr-x" for mode m into s, 11 chars with the '\0'
void mode_string(mode_t m, char *s)
{
    static char rwx[] = "rwxrwxrwx";
    int i;

    switch (m & S_IFMT) {
    case S_IFDIR:  s[0] = 'd'; break;
    case S_IFCHR:  s[0] = 'c'; break;
    case S_IFBLK:  s[0] = 'b'; break;
    case S_IFLNK:  s[0] = 'l'; break;
    case S_IFIFO:  s[0] = 'p'; break;
    case S_IFSOCK: s[0] = 's'; break;
    default:       s[0] = '-'; break;
    }
    //IDIOM: a sliding mask -- 0400 is owner-read; shifting right one bit
    //at a time walks owner rwx, group rwx, other rwx, in ls's order
    for (i = 0; i < 9; i++)
        s[i+1] = (m & (0400 >> i)) ? rwx[i] : '-';
    //the three special bits borrow an x slot: lowercase if x is set too
    if (m & S_ISUID)
        s[3] = (s[3] == 'x') ? 's' : 'S';
    if (m & S_ISGID)
        s[6] = (s[6] == 'x') ? 's' : 'S';
    if (m & S_ISVTX)
        s[9] = (s[9] == 'x') ? 't' : 'T';
    s[10] = '\0';
}

//timestr: t as "2026-10-21 14:03" -- in a static buffer, so each call
//overwrites the last: print it before calling again
char *timestr(time_t t)
{
    static char buf[3][20];
    static int next = 0;
    char *s;

    //IDIOM: a ring of static buffers -- three calls in one printf each
    //get their own; a single buffer would print the last time three times
    s = buf[next];
    next = (next + 1) % 3;
    strftime(s, sizeof(buf[0]), "%Y-%m-%d %H:%M", localtime(&t));
    return s;
}

//dirwalk: apply fcn to all files in dir
void dirwalk(char *dir, void (*fcn)(char *))
{
    char name[MAX_PATH];
    Dirent *dp;
    MYDIR *dfd;

    //IDIOM: assign in the test -- open and check for failure in one line
    if ((dfd = my_opendir(dir)) == NULL) {
        fprintf(stderr, "dirwalk: can't open %s\n", dir);
        return;
    }
    //IDIOM: while ((p = next()) != NULL) -- the iterator loop: next()
    //returns NULL when there is nothing left
    while ((dp = my_readdir(dfd)) != NULL) {
        if (strcmp(dp->name, ".") == 0
            || strcmp(dp->name, "..") == 0)     //book prints this without == 0
            continue;   //skip self and parent
        //IDIOM: +2 -- one for the '/', one for the '\0'
        if (strlen(dir)+strlen(dp->name)+2 > sizeof(name))
            fprintf(stderr, "dirwalk: name %s/%s too long\n",
                dir, dp->name);
        else {
            sprintf(name, "%s/%s", dir, dp->name);
            //IDIOM: (*fcn)(name) -- call through a function pointer;
            //dirwalk doesn't know or care that fcn is fsize
            (*fcn)(name);
        }
    }
    my_closedir(dfd);
}

//my_opendir: open a directory for my_readdir calls -- the book's, as printed
MYDIR *my_opendir(char *dirname)
{
    int fd;
    struct stat stbuf;
    MYDIR *dp;

    //IDIOM: || chain -- each step runs only if every one before it
    //succeeded; the first failure stops the chain and returns NULL
    if ((fd = open(dirname, O_RDONLY, 0)) == -1
     || fstat(fd, &stbuf) == -1
     || (stbuf.st_mode & S_IFMT) != S_IFDIR
     || (dp = (MYDIR *) malloc(sizeof(MYDIR))) == NULL)
        return NULL;            //fd stays open if a later test failed
    dp->fd = fd;
    dp->nbuf = dp->pos = 0;     //not in the book: its readdir has no buffer
    return dp;
}

//my_closedir: close directory opened by my_opendir
void my_closedir(MYDIR *dp)
{
    //IDIOM: if (p) -- closing NULL is harmless, like free(NULL)
    if (dp) {
        close(dp->fd);
        free(dp);
    }
}

//my_readdir: read directory entries in sequence -- getdents64 in place
//of the book's read() of one struct direct at a time
Dirent *my_readdir(MYDIR *dp)
{
    struct linux_dirent64 *rec;
    static Dirent d;            //return: portable structure

    for (;;) {
        if (dp->pos >= dp->nbuf) {          //buffer used up: refill it
            dp->nbuf = syscall(SYS_getdents64, dp->fd, dp->buf, sizeof(dp->buf));
            dp->pos = 0;
            if (dp->nbuf <= 0)              //0: end of directory; -1: error
                return NULL;
        }
        //IDIOM: walk variable-length records -- cast the byte position
        //to the record type, then step by the record's own length
        rec = (struct linux_dirent64 *) ((char *) dp->buf + dp->pos);
        dp->pos += rec->d_reclen;
        if (rec->d_ino == 0)    //slot not in use
            continue;
        d.ino = rec->d_ino;
        strncpy(d.name, rec->d_name, MY_NAME_MAX);
        d.name[MY_NAME_MAX] = '\0';         //ensure termination
        return &d;
    }
}

win@DESKTOP-MEIH88T:~/webdev-projects$ gcc -Wall -Wextra cc-c.c -o cc-c
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c learning-unixcommands-cc
   39265 -rw-r--r--   1  1000  1000   626584 2026-08-10 02:44 learning-unixcommands-cc/unix_for_programmer_manual.txt
         dev 8,48  atime 2026-09-25 19:21  ctime 2026-08-10 02:44
   39942 -rw-r--r--   1  1000  1000     5545 2026-09-25 19:25 learning-unixcommands-cc/top ten unix commands.txt
         dev 8,48  atime 2026-09-25 19:25  ctime 2026-09-25 19:25
   26207 -rw-r--r--   1  1000  1000    11103 2026-07-28 15:46 learning-unixcommands-cc/cc.html
         dev 8,48  atime 2026-09-25 19:21  ctime 2026-07-28 15:46
   63736 drwxr-xr-x   2  1000  1000     4096 2026-09-25 19:25 learning-unixcommands-cc
         dev 8,48  atime 2026-10-20 15:24  ctime 2026-09-25 19:25
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c /usr/bin/passwd /dev/tty /dev/sda /dev/null zhouyi.txt
    2010 -rwsr-xr-x   1     0     0    93640 2026-02-02 15:45 /usr/bin/passwd
         dev 8,48  atime 2026-07-25 20:16  ctime 2026-07-25 20:09
      10 crw-rw-rw-   1     0     5   5,   0 2026-10-20 02:46 /dev/tty
         dev 0,6  atime 2026-10-20 02:46  ctime 2026-10-20 02:46
     145 brw-rw----   1     0     6   8,   0 2026-10-20 02:46 /dev/sda
         dev 0,6  atime 2026-10-20 02:46  ctime 2026-10-20 02:46
       4 crw-rw-rw-   1     0     0   1,   3 2026-10-20 02:46 /dev/null
         dev 0,6  atime 2026-10-20 02:46  ctime 2026-10-20 02:46
   63696 -rwxr-xr-x   1  1000  1000   264389 2026-09-27 20:54 zhouyi.txt
         dev 8,48  atime 2026-10-20 15:30  ctime 2026-09-27 20:54
win@DESKTOP-MEIH88T:~/webdev-projects$ ./cc-c | tail -4
   63668 drwxr-xr-x   6  1000  1000     4096 2026-07-27 13:37 ./.venv
         dev 8,48  atime 2026-10-20 15:24  ctime 2026-07-27 13:37
   59978 drwxr-xr-x  11  1000  1000     4096 2026-10-21 08:44 .
         dev 8,48  atime 2026-10-21 08:44  ctime 2026-10-21 08:44
```
