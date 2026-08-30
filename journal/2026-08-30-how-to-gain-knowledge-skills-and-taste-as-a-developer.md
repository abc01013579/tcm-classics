---
title: How to gain knowledge skills and taste as a developer?
date: 2026-08-30
---

shuiming: as more people depend on Claude code to get jobs done. The issue is going to catch up with us.

cc: That’s a fair worry, and it’s not hypothetical — it’s already a live debate in CS education and hiring circles. A few concrete ways it could “catch up”:

The judgment gap widens over time. Right now, senior engineers directing Claude Code have decades of hard-won pattern recognition to catch subtle bugs — that’s exactly what made the AMD driver story work. But someone who starts their career leaning on the tool never builds that internal alarm bell in the first place. Ten years from now, the senior engineers with that instinct start retiring, and the pipeline behind them may be thinner on exactly the skill that made the tool safe to use.

Debugging becomes the bottleneck, not writing. When code is cheap to generate, the scarce skill shifts to knowing when generated code is wrong — but that skill is harder to build passively. You mostly learn to spot bugs by having written and broken things yourself first. If fewer people do that early, you could end up with more people who can prompt fluently but fewer who can actually diagnose a subtle race condition or memory corruption bug at 2am.

It’s already showing up in hiring signals. Some companies report junior engineers who can ship features fast with AI assistance but struggle in interviews or incident response that requires reasoning from first principles — because the tool handled the “productive struggle” that used to build that reasoning.

The counterweight, though: this isn’t unprecedented. Compilers, high-level languages, and IDEs all triggered the same fear — “nobody will understand assembly/memory management anymore” — and mostly what happened is the floor of required knowledge shifted, not disappeared. The people who go deep still exist, just proportionally fewer, and they become more valuable, not less. The real risk isn’t “the issue catches up with us” in some vague sense — it’s more specific: a widening gap between people who used AI to accelerate real understanding versus people who used it to avoid building it, with no obvious way to tell the two apart from a resume until something breaks.
