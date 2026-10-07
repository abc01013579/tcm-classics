---
title: how to skim cs books?
date: 2026-10-07
---

shuiming.....i know i can not digging into each one deeply. i am going to skim them in order to have a bird view of programming and cs in general.

cc.....That's a sound plan: go deep in one place and skim everywhere else. Your library is already arranged for it. Your deep track is K&R, Lions and the real source in ~/unix-v6 and ~/linux-0.01, with cc-c.c to work in. The rest of your cc-c collection covers every layer of computing, so skimming it gives you the bird's-eye view:

Layer	Your books
Hardware, from logic gates up -->    Code (004), How Do It Know (005), Elements of Computing Systems (006), Patterson & Hennessy (003, 029), Harris (030), CMOS VLSI (046)
Hardware ↔ programmer -->	Computer Systems: A Programmer's Perspective (018)
Operating systems	OSTEP (002), Tanenbaum (021, 022), Silberschatz (034), Bach (049), Lions (063), Bedtime Stories (071)
Unix and C in practice-->APUE (042), The Linux Programming Interface (028), The UNIX Programming Environment (050), The Art of UNIX Programming (075)
Languages and thinking	K&R (000), SICP (019, 072), Stroustrup (031)
Algorithms-->	Knuth (064–068), CLRS (011, 073), Sedgewick (041), Kleinberg–Tardos (013), Skiena (033)
Software craft	--> Code Complete (008), Pragmatic Programmer (070), Mythical Man-Month (016), Refactoring (009)
Systems at scale -->Kleppmann (015), networking (017), distributed systems (036)
History and ideas	Ritchie's papers (052, 062), Just for Fun (020), Turing (050, 051), PageRank (053, 057), the AI papers (055–061)

Three good books to skim first, for the overall picture:
->Petzold's Code (004): one book that goes from a flashlight to a working computer. The best single overview there is.
->CS:APP (018): shows what your C code becomes inside the machine. It connects directly to what you're learning now.
->Ritchie's The Development of the C Language (062): short, and written by the language's creator. It explains why C looks the way it does.

Skimming gives you the overall map. The deep track is how you actually learn to read and write code.
