# paper-trader

A **simulated** stock-trading loop for Claude Code. It tests the idea from our
conversation — "analyze every 3 hours and make calls until you hit a target" —
with **fake money against real prices**. No brokerage is ever connected and no
real funds move. The point is to find out, at zero financial risk, whether the
strategy has any edge before you'd ever consider real capital.

This is the honest first version of any trading loop. If it can't reliably clear
the target in simulation, that's the cheapest possible thing to learn.

## What's inside

```
paper-trader/
├── .claude/skills/paper-trade/SKILL.md   # the policy the agent follows each run (analyze → decide → act)
├── run_once.sh           # one loop iteration — schedule THIS every 3h
├── scripts/
│   ├── portfolio.py      # deterministic ledger + hard guardrails + STOP/CONTINUE logic
│   └── market_data.py    # price fetch (real Yahoo Finance quotes, or --source stub offline)
├── state/                # portfolio.json + trade_log.md (created on init; the loop's memory)
└── routine.example.yaml  # example Claude Code routine (every 3 hours)
```

## Setup

```bash
# from the package root
pip install requests          # real quotes (skip if you'll only use stub prices)
python3 scripts/portfolio.py init \
    --cash 300 --target-equity 500 --floor-equity 210 \
    --max-trades 40 --max-position-pct 0.40
```

**About `--target-equity 500`:** this stops the loop when your *total account
value* reaches $500 (i.e. +$200 on a $300 start). If by "make $500" you meant
+$500 *profit*, set `--target-equity 800`. The floor ($210) is the two-sided
exit we added — a hard stop-loss so the loop can't just bleed to zero chasing
the goal. Tune all of it.

## Run it once (test offline first)

```bash
SOURCE=stub ./run_once.sh     # fake prices, proves the wiring without internet
./run_once.sh                 # real prices from Yahoo Finance
```

The mid-run pre-check skips the model entirely when a stop condition is already
met, so a finished loop costs nothing.

## Schedule it every 3 hours

**Option A — Claude Code Routine (runs in Anthropic's cloud, survives your laptop
closing).** See `routine.example.yaml`, or create it with `/schedule` inside
Claude Code. Requires Claude Code on the web on a Pro/Max/Team/Enterprise plan.

**Option B — cron (runs on your machine while it's on):**
```cron
0 */3 * * *  cd /path/to/paper-trader && ./run_once.sh >> state/loop.log 2>&1
```

## The safety model

The agent picks stocks; it does **not** get to touch the rules. `portfolio.py`
enforces, in code:

- **Paper only** — there is no trading API anywhere in this package.
- **Universe cap** — only the tickers in `state/portfolio.json → universe`.
- **Cash cap** — can't spend money it doesn't have.
- **Position cap** — no single name over `max_position_pct` of starting equity.
- **Trade cap** — halts after `max_trades`.
- **Two-sided exit** — STOP on WIN (`target-equity`) *and* STOP on LOSS
  (`floor-equity`) or deadline. This is the fix for the original design, whose
  only exit was success.

Any trade that breaks a rule is rejected with a reason; the agent adjusts.

## Honest caveats

- Simulated fills are optimistic: they assume you trade exactly at the quoted
  price with no slippage, spread, or partial fills. Real results are worse.
- An LLM re-reasoning every 3 hours is **not** a validated edge. Good simulation
  results are necessary, not sufficient — the next step would be a proper
  backtest on historical data with out-of-sample checks, not going live.
- Not financial advice. This is an engineering test harness, not a
  recommendation to trade.

## If you later want *real* automated trading

Don't bolt a Robinhood equities wrapper onto this — Robinhood has no official
public stock API (only crypto), and unofficial wrappers violate their terms and
risk your account. Use a broker with an **official** trading API that offers a
paper endpoint first (e.g. Alpaca), keep the same guardrails, and consider a
human-approval gate on the actual order. That's a separate build — ask when
you're there.
