---
title: SPY-RSI introduction
date: 2026-11-07
---

A separate bucket, apart from the DCA core (TSM, AMZN, BRK/B, Vanguard Target 2045). The core compounds and is never timed. This bucket tests one rule: buy SPY when it is oversold, sell when it recovers.

## Rules

- **Time frames:** daily, 4h, 1h, each tracked separately.
- **Entry:** RSI(14) < 30.
- **Exit:** RSI(14) > 50.
- **Size:** start with 10 shares; add only as profits grow.
- **No leverage.**
- **No post, no trade:** every entry and exit is posted here in real time.

## Log format

```
SPY entry — 10 sh @ ___
RSI(14): __ · time frame: daily / 4h / 1h
```

Exit post: price, RSI, profit or loss, whether the rules were followed.

## What it tests

Whether a simple oversold signal beats just holding the index, which time frame works best, and whether I follow my own rules. The log will answer all three.
