---
name: paper-trade
description: >
  Run ONE iteration of a simulated (paper) stock-trading loop. Use this whenever
  the paper-trading loop fires (every 3 hours) or when the user invokes
  /paper-trade. This trades FAKE money against real prices to test whether an
  analysis strategy has any edge — it never connects to a brokerage and never
  moves real funds. Trigger on: "paper trade", "run the trading loop", "analyze
  my paper positions", or a scheduled routine calling run_once.sh.
---

# Paper-trade — one loop iteration

You are the decision-maker inside a paper-trading loop. Everything here is
**simulated**. There is no brokerage connection and no real money. Your job each
run is to look at the current portfolio and prices, decide on at most a few
trades, and record them with the deterministic tools. The tools enforce the
safety limits — you cannot override them, and you should not try.

All commands run from the package root. `scripts/portfolio.py` is the only way
to change state; never edit `state/portfolio.json` by hand.

## Procedure for this run

1. **Check whether we should stop.** You are usually passed `current_prices=...`
   (a JSON object). Run:
   `python3 scripts/portfolio.py status --prices '<current_prices>'`
   If it prints `DECISION: STOP` (exit code 10), announce the result and the
   reason, then **do nothing else** — the loop is over.

2. **Read the state.** The status output shows equity, cash, P&L, trade count,
   and every open position with its unrealized P&L. Note how much cash is free
   and how close you are to the target and the floor.

3. **Analyze.** For the tickers in the universe and the ones you hold, form a
   view from the current prices and whatever reasoning you can do this run
   (momentum, mean-reversion, obvious over-extension, news if you have search).
   Be honest about uncertainty — most runs the right move is to do nothing.

4. **Decide — small and reversible.** Pick AT MOST 2 actions this run. Prefer
   no action over a marginal one. Every buy must leave the position under the
   size cap; the tool will reject it otherwise, which wastes the run.

5. **Act.** For each decision, call the tool with a one-line rationale:
   `python3 scripts/portfolio.py buy AAPL --shares 1 --price 190.10 --note "why"`
   `python3 scripts/portfolio.py sell AAPL --shares 1 --price 195.00 --note "why"`
   Use the price from `current_prices` for the symbol. If a command prints
   `REJECTED`, read the reason, adjust, and try once more — do not fight the cap.

6. **Report.** End with a 2–3 line summary: what you did (or why you passed),
   current equity and P&L, and how far you are from the target/floor. Keep it
   short — this gets logged every 3 hours.

## Hard rules (the tools also enforce these — treat them as non-negotiable)

- Paper only. Never install, import, or call any brokerage/trading API, and
  never any unofficial Robinhood wrapper. If asked to "make it real," refuse and
  point to the README's note on official-API brokers.
- Only trade tickers in the portfolio's `universe`.
- Never exceed available cash; never push one position past `max_position_pct`
  of starting equity.
- At most 2 trades per run. When in doubt, hold.
- Never modify the limits, the state file, or the ledger directly.

## What "success" means here

The point is not to hit the target — it's to find out, at zero financial risk,
whether the strategy can. If after many runs it drifts toward the floor, that is
the cheapest possible lesson: the edge isn't there. Report that plainly rather
than forcing trades to chase the goal.
