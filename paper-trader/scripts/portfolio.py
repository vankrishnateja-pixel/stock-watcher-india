#!/usr/bin/env python3
"""
portfolio.py — deterministic paper-trading ledger with hard guardrails.

This is the "tools" layer of the loop. It does NO thinking about which stocks
to buy — that's the agent's job. Its ONLY jobs are:
  1. Hold the simulated portfolio state (cash, positions, P&L, trade log).
  2. Refuse any trade that violates the safety limits (position cap, cash,
     max trades). The agent literally cannot break these rules.
  3. Compute a two-sided STOP/CONTINUE decision every run (profit target
     reached OR loss floor hit OR max trades OR deadline passed).

No real money is ever touched. There is no brokerage connection anywhere in
this file — "buying" just decrements a number in a JSON file.

Usage:
  portfolio.py init  --cash 300 --target-equity 500 --floor-equity 210 \
                     --max-trades 40 --max-position-pct 0.4 [--deadline ISO8601]
  portfolio.py symbols                       # universe + held tickers, space-separated
  portfolio.py status  --prices '{"AAPL":190.1}'   # prints report, exit 10 if STOP
  portfolio.py buy  AAPL --shares 2 --price 190.10 --note "reason"
  portfolio.py sell AAPL --shares 1 --price 195.00 --note "reason"
"""
import argparse, json, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "..", "state", "portfolio.json")
LEDGER = os.path.join(HERE, "..", "state", "trade_log.md")

# Default watchlist the agent is allowed to consider. Keep it small & liquid.
DEFAULT_UNIVERSE = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "SPY", "QQQ"]


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load():
    if not os.path.exists(STATE):
        sys.exit("No portfolio yet. Run: portfolio.py init ...")
    with open(STATE) as f:
        return json.load(f)


def save(p):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(p, f, indent=2)


def log_line(text):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    new = not os.path.exists(LEDGER)
    with open(LEDGER, "a") as f:
        if new:
            f.write("# Paper trading ledger\n\n")
        f.write(f"- {now_iso()}  {text}\n")


def equity(p, prices):
    """Mark-to-market total account value = cash + sum(shares * price)."""
    val = p["cash"]
    missing = []
    for sym, pos in p["positions"].items():
        px = prices.get(sym)
        if px is None:
            missing.append(sym)
            px = pos["avg_cost"]  # fall back to cost so a missing quote can't fake a gain
        val += pos["shares"] * px
    return val, missing


def cmd_init(a):
    if os.path.exists(STATE) and not a.force:
        sys.exit(f"{STATE} already exists. Use --force to overwrite.")
    p = {
        "created_at": now_iso(),
        "cash": a.cash,
        "start_equity": a.cash,
        "positions": {},
        "realized_pnl": 0.0,
        "trade_count": 0,
        "limits": {
            "target_equity": a.target_equity,
            "floor_equity": a.floor_equity,
            "max_trades": a.max_trades,
            "max_position_pct": a.max_position_pct,
            "deadline": a.deadline,
        },
        "universe": a.universe or DEFAULT_UNIVERSE,
        "history": [],
    }
    save(p)
    if os.path.exists(LEDGER):
        os.remove(LEDGER)
    log_line(f"INIT cash=${a.cash:.2f} target=${a.target_equity:.2f} "
             f"floor=${a.floor_equity:.2f} max_trades={a.max_trades} "
             f"max_position={a.max_position_pct:.0%}")
    print(f"Initialized paper portfolio with ${a.cash:.2f}.")
    print(f"  STOP on WIN  when equity >= ${a.target_equity:.2f}")
    print(f"  STOP on LOSS when equity <= ${a.floor_equity:.2f}")
    print(f"  STOP also after {a.max_trades} trades" +
          (f" or at {a.deadline}" if a.deadline else ""))


def cmd_symbols(a):
    p = load()
    syms = list(dict.fromkeys(p["universe"] + list(p["positions"].keys())))
    print(" ".join(syms))


def stop_reason(p, eq, missing):
    lim = p["limits"]
    if eq >= lim["target_equity"]:
        return f"WIN — equity ${eq:.2f} >= target ${lim['target_equity']:.2f}"
    if eq <= lim["floor_equity"]:
        return f"STOP-LOSS — equity ${eq:.2f} <= floor ${lim['floor_equity']:.2f}"
    if p["trade_count"] >= lim["max_trades"]:
        return f"MAX-TRADES — {p['trade_count']} trades reached"
    if lim["deadline"] and now_iso() >= lim["deadline"]:
        return f"DEADLINE — {lim['deadline']} passed"
    return None


def cmd_status(a):
    p = load()
    prices = json.loads(a.prices) if a.prices else {}
    eq, missing = equity(p, prices)
    start = p["start_equity"]
    pnl = eq - start
    print(f"Equity: ${eq:.2f}   Cash: ${p['cash']:.2f}   "
          f"P&L: ${pnl:+.2f} ({pnl/start:+.1%})   Trades: {p['trade_count']}")
    if p["positions"]:
        print("Positions:")
        for sym, pos in p["positions"].items():
            px = prices.get(sym, pos["avg_cost"])
            mv = pos["shares"] * px
            upnl = (px - pos["avg_cost"]) * pos["shares"]
            print(f"  {sym}: {pos['shares']} @ avg ${pos['avg_cost']:.2f} "
                  f"-> ${px:.2f}  mv ${mv:.2f}  uP&L ${upnl:+.2f}")
    if missing:
        print(f"  (no live price for {', '.join(missing)}; used cost basis)")
    reason = stop_reason(p, eq, missing)
    if reason:
        print(f"DECISION: STOP — {reason}")
        sys.exit(10)
    print("DECISION: CONTINUE")


def _position_cost_basis(pos):
    return pos["shares"] * pos["avg_cost"]


def cmd_buy(a):
    p = load()
    if a.symbol not in p["universe"]:
        sys.exit(f"REJECTED: {a.symbol} not in allowed universe {p['universe']}")
    if a.shares <= 0 or a.price <= 0:
        sys.exit("REJECTED: shares and price must be positive")
    cost = a.shares * a.price
    # Guardrail 1: can't spend cash you don't have.
    if cost > p["cash"] + 1e-9:
        sys.exit(f"REJECTED: cost ${cost:.2f} exceeds cash ${p['cash']:.2f}")
    # Guardrail 2: no single position larger than max_position_pct of START equity.
    existing = _position_cost_basis(p["positions"].get(a.symbol, {"shares": 0, "avg_cost": 0}))
    cap = p["limits"]["max_position_pct"] * p["start_equity"]
    if existing + cost > cap + 1e-9:
        sys.exit(f"REJECTED: position in {a.symbol} would be ${existing+cost:.2f}, "
                 f"over cap ${cap:.2f} ({p['limits']['max_position_pct']:.0%} of start)")
    # Apply.
    pos = p["positions"].get(a.symbol, {"shares": 0, "avg_cost": 0.0})
    total_shares = pos["shares"] + a.shares
    pos["avg_cost"] = (existing + cost) / total_shares
    pos["shares"] = total_shares
    p["positions"][a.symbol] = pos
    p["cash"] -= cost
    p["trade_count"] += 1
    p["history"].append({"ts": now_iso(), "action": "BUY", "symbol": a.symbol,
                         "shares": a.shares, "price": a.price, "note": a.note})
    save(p)
    log_line(f"BUY  {a.shares} {a.symbol} @ ${a.price:.2f} (${cost:.2f}) — {a.note}")
    print(f"OK: bought {a.shares} {a.symbol} @ ${a.price:.2f}. Cash now ${p['cash']:.2f}.")


def cmd_sell(a):
    p = load()
    pos = p["positions"].get(a.symbol)
    if not pos or pos["shares"] < a.shares:
        held = pos["shares"] if pos else 0
        sys.exit(f"REJECTED: hold only {held} {a.symbol}, can't sell {a.shares}")
    if a.price <= 0:
        sys.exit("REJECTED: price must be positive")
    proceeds = a.shares * a.price
    realized = (a.price - pos["avg_cost"]) * a.shares
    pos["shares"] -= a.shares
    if pos["shares"] == 0:
        del p["positions"][a.symbol]
    else:
        p["positions"][a.symbol] = pos
    p["cash"] += proceeds
    p["realized_pnl"] += realized
    p["trade_count"] += 1
    p["history"].append({"ts": now_iso(), "action": "SELL", "symbol": a.symbol,
                         "shares": a.shares, "price": a.price,
                         "realized": realized, "note": a.note})
    save(p)
    log_line(f"SELL {a.shares} {a.symbol} @ ${a.price:.2f} "
             f"(realized ${realized:+.2f}) — {a.note}")
    print(f"OK: sold {a.shares} {a.symbol} @ ${a.price:.2f}. "
          f"Realized ${realized:+.2f}. Cash now ${p['cash']:.2f}.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init", help="create a fresh paper portfolio")
    pi.add_argument("--cash", type=float, default=300.0)
    pi.add_argument("--target-equity", type=float, default=500.0,
                    help="STOP when total account value reaches this (WIN)")
    pi.add_argument("--floor-equity", type=float, default=210.0,
                    help="STOP when total account value drops to this (LOSS)")
    pi.add_argument("--max-trades", type=int, default=40)
    pi.add_argument("--max-position-pct", type=float, default=0.40,
                    help="max fraction of starting equity in any one name")
    pi.add_argument("--deadline", type=str, default=None,
                    help="ISO8601 UTC time to force-stop, e.g. 2026-09-01T00:00:00+00:00")
    pi.add_argument("--universe", nargs="*", default=None)
    pi.add_argument("--force", action="store_true")
    pi.set_defaults(func=cmd_init)

    ps = sub.add_parser("symbols", help="print tickers to fetch prices for")
    ps.set_defaults(func=cmd_symbols)

    pst = sub.add_parser("status", help="print report + STOP/CONTINUE (exit 10 = STOP)")
    pst.add_argument("--prices", type=str, default=None, help='JSON like {"AAPL":190.1}')
    pst.set_defaults(func=cmd_status)

    pb = sub.add_parser("buy")
    pb.add_argument("symbol"); pb.add_argument("--shares", type=int, required=True)
    pb.add_argument("--price", type=float, required=True); pb.add_argument("--note", default="")
    pb.set_defaults(func=cmd_buy)

    psl = sub.add_parser("sell")
    psl.add_argument("symbol"); psl.add_argument("--shares", type=int, required=True)
    psl.add_argument("--price", type=float, required=True); psl.add_argument("--note", default="")
    psl.set_defaults(func=cmd_sell)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
