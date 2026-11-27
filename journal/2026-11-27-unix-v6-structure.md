---
title: Unix V6 structure
date: 2026-11-27
tags: CS
---

Reading the Unix V6 kernel, 1975, PDP-11. About 11,600 lines, the whole thing.

Four parts:

ken/ — Ken Thompson's core. Processes, system calls, file system.

dmr/ — Dennis Ritchie's drivers. Disks, tapes, terminals, and bio.c, the buffer cache.

conf/ — assembly glue. Boot, traps, context switch, device tables.

*.h — shared structs. user.h, proc.h, inode.h, buf.h. No modules, no interfaces, just globals everyone touches.

One read() call:

user program → trap → trap.c → sysent[] → sys2.c → rdwri.c → bio.c → rk.c → disk → interrupt → wakeup.

The build links it all into one file, /rkunix. That file only ever lived on a real PDP-11.

Small enough to read in a week. Still the shape of every Unix since.
