---
title: how to dig deeper on  hardware?
date: 2026-09-05
---

shuiming: i got three top hardware book, including  The elements of computer systems;  How do it know; the hidden language of computer hareware and software; computer organization design, etc. how to use them.

cc: Nice haul — those three are genuinely the best complementary set for this (you'd already flagged nand2tetris as your "hardware-up" track, so this fills it out well). Here's how they stack, and why they don't overlap as much as they look like they should:

Layer	But How Do It Know?	Elements of Computing Systems (nand2tetris)	Computer Organization & Design
OS / apps	—	✓ (project 12)	—
Compiler / VM	—	✓ (projects 7–11)	touches compiled-code-to-asm
Assembly / ISA	✓ (toy "SAP" asm)	✓ (toy "Hack" asm)	✓✓ real ISA (RISC-V/MIPS), deep
CPU	✓	✓ (project 5)	✓✓ pipelining, hazards, control
Memory	✓	✓ (project 3)	✓✓ cache hierarchy, virtual memory
ALU	✓	✓ (project 2)	✓ arithmetic circuits, floating point
Logic gates	✓✓ (from relays up, plain language)	✓✓ (project 1, you build them)	assumed background, not taught
Why three books, not one: But How Do It Know? and nand2tetris climb the same ladder (gates → ALU → memory → CPU → assembly), but the first is a fast conceptual read with zero code, and the second makes you actually build every one of those pieces yourself in an HDL simulator. Computer Organization & Design barely bothers with gates — it assumes you already have that picture — and instead goes deep on the parts the other two wave their hands at: real instruction sets, why pipelining causes hazards, why caches exist and how they're organized, how performance is actually measured.

Recommended order:

Read But How Do It Know? first, straight through, no code. It's short and builds the whole mental picture (relay → gate → ALU → memory → CPU → assembly) fast. This is your "scan pass" for the whole subject — same move you already use on K&R before going line-by-line.
Then do nand2tetris projects 1–6 (the hardware track) using the free HDL simulator from nand2tetris.org — the book's chapters 1–6 are the instructions, the projects are where the actual learning happens. You're not reading about a NAND-to-CPU climb anymore, you're wiring it.
Projects 7–12 (VM translator → Jack compiler → OS) are a real multi-week programming project — and you can write all of it in C, which turns this into a capstone for your K&R work rather than a separate track.
Use Computer Organization & Design as a standing reference alongside/after nand2tetris, not cover-to-cover — read it chapter by chapter for whatever nand2tetris's toy Hack computer doesn't cover: number representation, real ISA design, pipelining, the cache/virtual-memory hierarchy, performance measurement. It's the "this is how it actually has to work at scale" layer on top of the toy machine you just built.
That order matches your established pattern: primary-source-style overview first (BHDIK), then hands-on line-by-line building (nand2tetris, same rigor as your K&R method), then the rigorous reference text you dip into as needed rather than read linearly (COD).

shuiming: what to do with Code: the hidden language of computer hareware and software?

cc: Good catch — that's actually a separate, very well-known book (Charles Petzold's Code), not the same as But How Do It Know? It covers almost the same ground (telegraphs → Morse/binary → relays → logic gates → ALU → memory → a working CPU) but gets there through a slower, narrative/historical route, and it goes deeper on information encoding — Morse code, Braille, telegraph relay systems, ASCII/character encoding — which the other three barely touch.

Given the overlap, here's where it slots in:

Read Code first, before But How Do It Know? — its narrative build-up from telegraphs/encoding is the gentlest on-ramp of the four books, and it's the one place you'll get real depth on how information (not just numbers) gets represented in bits.
Then But How Do It Know? covers the same relay→gate→ALU→CPU climb again, but in its stripped-down, diagram-heavy style — given you said you're "more of a visualizer" than a word-by-word reader, this works well as a second, faster pass that nails down in pictures what Code just told you in prose. Not wasted repetition — it's the same climb from two angles, which tends to stick better than either alone.
Then straight into nand2tetris (build it), with Computer Organization & Design as your standing reference, as laid out before.
So the order becomes: Code → But How Do It Know? → nand2tetris (build) → Computer Organization & Design (reference, as needed).

shuiming: what is nand2tetris?

cc: Nand2Tetris is the nickname for a free course + book (The Elements of Computing Systems, Nisan & Schocken) built around one idea: start with nothing but a single NAND gate, and build, project by project, all the way up to a working computer that can run a simple Tetris-like game — hence "NAND to Tetris."

You do it as 12 hands-on projects, split into two halves:
#	Project	What you build	From
1	Boolean logic	AND, OR, NOT, MUX, etc.	out of NAND alone
2	Boolean arithmetic	half-adder, full-adder, ALU	out of the gates from #1
3	Memory	1-bit register → RAM	out of flip-flops/gates
4	Machine language	write programs in Hack assembly	—
5	Computer architecture	the full CPU + memory, wired together	chips from #1–3
— hardware half ends here —			
6	Assembler	translates Hack assembly → binary	you write this in any language
7–8	VM translator	stack-machine VM → Hack assembly	—
9	High-level language	write a simple app (e.g. Tetris) in "Jack"	—
10–11	Compiler	Jack source → VM code	—
12	Operating system	basic OS services (math, strings, memory alloc, screen, I/O)	—

You never use real transistors or a real compiler toolchain — there's a free browser/desktop simulator where you wire chips together in a simple hardware description language (HDL), and each project builds strictly on the ones before it. By project 12 you've personally built every layer between a single logic gate and a program running on "your" computer.

That's why it fits your plan well: projects 1–5 are the hands-on version of what Code and But How Do It Know? explain in prose/diagrams, and projects 6–12 are a real programming project you could write in C, tying straight into your K&R work.

shuiming: great suggestion, we are going to have tons of fun.

cc:  Looking forward to it — the moment in project 5 where the CPU you built out of your own gates actually runs a program is a genuinely great one. Whenever you start project 1, bring the questions here same as with K&R.
