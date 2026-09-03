---
title: How does computer do math? #2
date: 2026-09-03
---

shuiming: i have studied math for years and python and JS, but no one metioned that. it is weird. so fundamental, it is ignored by the public.

cc:That's not a coincidence — it's because Python and JS are specifically designed to hide exactly this. Python ints are arbitrary-precision (they silently grow instead of overflowing), and JS numbers are all IEEE-754 doubles under the hood, not fixed-width binary integers you're meant to think about at the bit level. Neither language ever forces you to confront "how many slots does this number actually live in" — that's the entire point of them as high-level languages: let you think in terms of values and never in terms of representation.

C is almost the last widely-used language where that abstraction is deliberately stripped away. An unsigned char is 8 physical bits, full stop, and the language makes you feel every consequence of that — overflow, shifts falling off the end, signed vs unsigned right-shift behavior. It's not that math educators or Python/JS teachers are hiding a secret; it's that the entire value proposition of those tools is "you shouldn't have to know this." You only run into it in C, or in a computer architecture / digital logic course, or if you write in assembly, or if you hit a real bug caused by it (integer overflow, bit-packed protocol parsing, etc.).

So the thing you just rediscovered isn't obscure trivia — it's the actual physical substrate that every abstraction you've used in Python/JS is quietly running on top of and hiding from you. That's arguably the single biggest thing K&R-style C teaches that other language study doesn't: not "how to code," but "what a computer literally is doing," with nothing between you and the bits. It's a legitimately rare thing to have actually sat with, even among people who've programmed for years in higher-level languages.

shuiming:how do computers do math?

cc: This is the natural next question, and it closes the loop on what you just realized — because if shifting is "just" repositioning bits, addition is the one operation that's doing genuinely new work, and everything else (subtraction, multiplication, division) is built on top of it.

The actual bottom layer: logic gates

A CPU is built from transistors wired into a small set of logic gates — AND, OR, XOR (exclusive-or), NOT — each of which takes one or two single bits in and produces one bit out, based on a fixed truth table. These gates are physical circuits; there's no "computation" happening in any abstract sense, just voltage patterns propagating through wires. Every arithmetic operation a CPU performs is built by wiring a bunch of these tiny gates together.

Addition: the actual working operation

Take two single bits, a and b. Binary addition of one bit-column needs two outputs: the sum bit, and a carry bit (like carrying the 1 in grade-school addition). It turns out:

sum = a XOR b (1 exactly when the bits differ — matches 0+1=1, 1+0=1, but 0+0=0 and 1+1=0-with-carry)
carry = a AND b (1 only when both bits are 1 — matches 1+1=10 in binary, i.e. a carry)
That two-gate circuit is called a half adder. To add multi-bit numbers you need a full adder per column, which also takes a carry-in from the column to its right, and produces sum + carry-out — just the half-adder idea done twice and OR'd together. Chain 8 of these in a row (one per bit position) and you can add two 8-bit numbers, with each column's carry-out feeding the next column's carry-in — a "ripple-carry adder." That's it. That's the circuit. No multiplication tables, no understanding of quantity — just XOR/AND gates wired in a row.

Concrete trace: 0110 (6) + 0101 (5)


carry:   0 1 1 0
  a:     0 1 1 0
  b:     0 1 0 1
------------------
sum:     1 0 1 1   = 11
Column by column, right to left: 0+1=1,c0; 1+0=1,c0; 1+1=0,c1; 0+0+1(carry)=1,c0. Result 1011 = 11. Every step was just XOR and AND on single bits, nothing more.

Subtraction: piggybacks on addition, doesn't get its own circuit

This is where your earlier ~/two's-complement work (from the UMAX/SMAX exercise archived in your file) pays off directly: computers don't build a separate "subtract" circuit. a - b is computed as a + (~b + 1) — negate b via two's complement, then just run it through the same adder circuit as addition. That's the entire reason two's complement representation was chosen for negative numbers: it makes subtraction free once you have an adder.

Multiplication: shift-and-add, using the circuits you already have

This is where your <</>> insight comes back in directly. a * b (for whole numbers) can be computed as: for each 1-bit in b, take a shifted left by that bit's position, and add all those shifted copies together. That's literally binary long multiplication, and it's built from nothing but the shift circuitry and the adder circuitry you already have — no separate "multiply" primitive at the gate level (modern CPUs have dedicated faster multiplier circuits for speed, but conceptually it decomposes to exactly this).

Division is the mirror image — shift-and-subtract, repeatedly testing whether the divisor fits and subtracting it off, which is again just the adder circuit (negated) plus shifts.

Floating point (float/double) is the one place this whole picture gets genuinely more complicated — it's not simple positional binary, it's closer to scientific notation (sign, exponent, mantissa) with its own dedicated hardware. Worth its own conversation if you want to go there, but the integer picture above — gates → adder → everything else reuses the adder — is the real foundation, and it's exactly the "shockingly simple" thing you were sensing with the shifts.
