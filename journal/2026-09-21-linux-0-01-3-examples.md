---
title: Linux 0.01 3 examples
date: 2026-09-21
---

win@DESKTOP-MEIH88T:~/webdev-projects/git$ ds
Enter your prompt: do you know Linux 0.01? show me 3 code examples?
Yes! Linux 0.01 is the very first public release of the Linux kernel, posted by Linus Torvalds to `comp.os.minix` on September 17, 1991. It was tiny (~10,000 lines of C + assembly), required MINIX to compile, and only supported the 80386 with an AT-compatible hard disk and a Finnish keyboard layout. It couldn't even print anything useful — it just booted to a shell.

Here are 3 real code examples from that source tree (paths relative to `linux-0.01/`):

---
```c

### 1. `init/main.c` — the boot entry point

This is the very first C code that runs after the assembly setup. It initializes memory, traps, and forks `init`.

```c
void main(void)         /* This really IS void, no error here. */
{                       /* The startup routine assumes (well, ...) this */
/*
 * Interrupts are still disabled. Do necessary setups, then
 * enable them
 */
        time_init();
        tty_init();
        trap_init();
        sched_init();
        buffer_init(buffer_memory_end);
        hd_init();
        sti();
        move_to_user_mode();
        if (!fork()) {          /* we count on this going ok */
                init();
        }
/*
 *   NOTE!!   For any other task 'pause()' would mean we have to get a
 *  signal to awaken, but task0 is the sole exception (see 'schedule()')
 *  as task 0 gets activated at every idle moment (when no other tasks
 *  can run).  For task 0 we use a 'for(;;)' instead.
 */
        for(;;) pause();
}
```

Notice the classic Linus comment style ("This really IS void, no error here") — he was already leaving snarky notes in the source.

---

### 2. `kernel/fork.c` — the very first `copy_process`

Fork in 0.01 was called `copy_process` and used `get_free_page()` to grab a raw page of memory (no `kmalloc`/SLAB yet — those came later). It copies the parent's page directory entries and duplicates the task struct byte-for-byte.

```c
int copy_process(int nr, long ebp, long edi, long esi,
                 long gs, long fs, long es, long ds,
                 long eip, long cs, long eflags,
                 long esp, long ss)
{
        struct task_struct *p;
        int i;
        struct file *f;

        p = (struct task_struct *) get_free_page();
        if (!p)
                return -EAGAIN;
        task[nr] = p;
        *p = *current;  /* NOTE! this doesn't copy the supervisor stack */
        p->state = TASK_UNINTERRUPTIBLE;
        p->pid = last_pid;
        p->counter = p->priority;
        p->signal = 0;
        p->alarm = 0;
        p->leader = 0;          /* process leadership doesn't inherit */
        p->utime = p->stime = 0;
        p->cutime = p->cstime = 0;
        p->start_time = jiffies;
        p->tss.back_link = 0;
        p->tss.esp0 = PAGE_SIZE + (long) p;
        p->tss.ss0 = 0x10;
        p->tss.eip = eip;
        p->tss.eflags = eflags;
        ...
        for (i=0; i<NR_OPEN;i++)
                if ((f=p->filp[i]))
                        f->f_count++;
        ...
}
```

Every line screams "this is how you'd write it if you had to do it in an afternoon."

---

### 3. `include/linux/sched.h` — `struct task_struct` (the whole process model!)

The entire process descriptor in 0.01 was about 25 fields. Compare that to `struct task_struct` in modern Linux (hundreds of fields).

```c
struct task_struct {
/* these are hardcoded - don't touch */
        long state;     /* -1 unrunnable, 0 runnable, >0 stopped */
        long counter;
        long priority;
        long signal;
        struct sigaction sigaction[32];
        long blocked;   /* bitmap of masked signals */
/* various fields */
        int exit_code;
        unsigned long start_code,end_code,end_data,brk,start_stack;
        long pid,father,pgrp,session,leader;
        unsigned short uid,euid,suid;
        unsigned short gid,egid,sgid;
        long alarm;
        long utime,stime,cutime,cstime,start_time;
        unsigned short used_math;
/* file system info */
        int tty;                /* -1 if no tty, so it must be signed */
        unsigned short umask;
        struct m_inode * pwd;
        struct m_inode * root;
        struct m_inode * executable;
        unsigned long close_on_exec;
        struct file * filp[NR_OPEN];
/* ldt for this task 0 - zero 1 - cs 2 - ds&ss */
        struct desc_struct ldt[3];
/* tss for this task */
        struct tss_struct tss;
};
```

That last bit is the giveaway: in 0.01 there was **no proper LDT allocator** — every task struct just embedded its own `ldt[3]` and `tss`. The "modern" concept of allocating per-process GDT/LDT slots came a few releases later.

---

### Fun historical facts
- The whole kernel was ~10k lines, compressed to ~60KB.
- No networking, no SCSI, no loadable modules, no ELF (only `a.out`).
- It required a 386 with an AT-compatible hard drive and a Minix filesystem.
- Linus charged nothing and asked for postcards instead of money.

If you want to dig into it yourself, the original tarball is still mirrored (e.g. on `kernel.org` mirrors under `pub/linux/kernel/Historic/old-versions/`), and there are GitHub mirrors like `github.com/oldlinux/linux-0.01` with the full tree.
``````c

```
