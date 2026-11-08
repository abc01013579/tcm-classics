---
title: SPY-RSI backtest
date: 2026-11-07
---

Backtest of the rules in the introduction: buy SPY when RSI(14) < 30, sell when RSI(14) > 50. Fill at the signal bar's close, no costs.

| | 1h | 4h | Daily (~3 yr) | Daily (25 yr) |
|---|---|---|---|---|
| Period | Dec 2023 – Nov 2026 | same | same | 2001 – 2026 |
| Trades | 42 (~14/yr) | 7 (~2/yr) | 3 (~1/yr) | 31 (~1/yr) |
| Wins | 36/42 | 6/7 | 3/3 | 28/31 |
| Avg per trade | +0.7% | +1.6% | +6.2% | +2.2% |
| Worst trade | −1.4% | −2.1% | +3.8% | −11.8% |
| Worst dip while holding | −4.4% | −7.6% | −1.7% | −28.3% |
| Avg hold | ~2 days | ~6 days | 10 days | 13 days |
| Time in market | 12% | 6% | 4% | 6% |
| Strategy total | +34.7% | +11.9% | +19.8% | +94% |
| Buy & hold SPY | +58% | +55% | +61% | +918% |

## Takeaways

- The signal works on all three time frames: 85–100% wins, losses mostly small.
- None beat buy & hold, because the money is in cash most of the time. It is a tool for spare cash, not a replacement for the core.
- 1h gives the most return for the time invested, but needs watching during market hours.
- The 25-year daily run shows the real risk: one trade fell 28% before RSI got back above 50 (COVID crash, Feb–Apr 2020).

## Caveats

- The intraday data covers only ~3 years, all of it a bull market.
- Real fills will be slightly worse; intraday buy & hold excludes dividends.
