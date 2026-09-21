---
title: all by accident?
date: 2026-09-21
---

shuiming.....NVDA is an accident too. GPU was for gamers for a long time before it found its way in neural network.

cc.....Exactly right, and the mechanism behind it is a nice payoff of the "it's all bits and parallel wires" model you've been building. A GPU was built to do one very specific thing millions of times per frame: compute the color of a pixel, independently of every other pixel. That's the same computational shape as a matrix multiplication — apply the same simple arithmetic to millions of independent numbers at once. A CPU is optimized for doing one complicated thing fast in sequence; a GPU is optimized for doing one simple thing to a huge pile of numbers simultaneously. Neural nets turned out to be almost entirely matrix multiplication, so gamers had unknowingly been funding, for over a decade, the exact hardware architecture deep learning needed.

The actual inflection point was 2012: AlexNet, a neural net trained on two consumer NVIDIA GTX 580 gaming cards, blew away every prior computer-vision approach in the ImageNet competition (15% error rate vs. 26% for the runner-up, which used decades of hand-tuned traditional techniques). NVIDIA had released CUDA back in 2006 specifically to let programmers use the GPU for general math, not just graphics — mostly aimed at scientists doing physics simulations at the time — but almost nobody outside a niche used it seriously until AlexNet proved it could win the most important benchmark in AI overnight. Within a few years NVIDIA went from "the gaming GPU company" to the company every AI lab on Earth depends on.

Same shape of story as Torvalds, honestly: build something for one narrow, personal reason (Linus wanted a better Minix for himself; Jensen Huang wanted better game graphics), with zero plan for what it would actually become — the eventual, world-changing use case wasn't foreseen, it fell out of the underlying architecture being unexpectedly general-purpose.

shuiming.....so is unix: out of needs to play games.

cc.....Correct, and it's an even better fit for the pattern than you might expect. Ken Thompson (Bell Labs) wrote a game called Space Travel — a little rocket-through-the-solar-system simulator — while working on the Multics project. When Bell Labs pulled out of Multics in 1969, he lost the mainframe it ran on. Rather than let the game die, he scrounged up a spare, unused PDP-7 minicomputer sitting around the lab just to have somewhere to keep playing it — but the PDP-7 had no real operating system, no file system, nothing to build on. So to get his game running properly, he (with Dennis Ritchie) started writing one from scratch. That fledgling OS became Unix.

So the actual lineage is: a guy wants to keep playing his own video game → builds an OS to make that possible → that OS becomes Unix → Unix's design philosophy directly shapes Linux 22 years later → Linux plus GNU tools becomes the foundation nearly all of today's servers, phones (Android), and cloud infrastructure run on, including whatever's hosting DeepSeek and me right now.

Three "accidental revolutionary" stories in a row, same shape every time: narrow personal itch, zero grand plan, general-purpose result nobody could have predicted from the starting motive. That's arguably the actual pattern worth remembering, more than any one of the individual facts.
