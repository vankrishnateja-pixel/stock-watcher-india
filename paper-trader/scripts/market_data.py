#!/usr/bin/env python3
"""
market_data.py — fetch current prices for the paper-trading loop.

Prints a JSON object like {"AAPL": 190.12, "MSFT": 402.5}.

Sources:
  --source yfinance   (default) real quotes via the `yfinance` package.
                      Requires internet + `pip install yfinance`.
  --source stub       deterministic fake prices for offline testing of the
                      pipeline. Reads overrides from the STUB_PRICES env var
                      (JSON), otherwise makes up a stable pseudo-price per
                      ticker. NEVER use stub prices for anything you care about.

Note: this sandbox blocks finance domains, so `yfinance` only works when you
run this on your own machine inside Claude Code. Use --source stub here to
prove the wiring end-to-end.
"""
import argparse, hashlib, json, os, sys


def stub_price(sym):
    env = os.environ.get("STUB_PRICES")
    if env:
        overrides = json.loads(env)
        if sym in overrides:
            return float(overrides[sym])
    # Stable pseudo-price in ~[20, 520) derived from the ticker string.
    h = int(hashlib.sha256(sym.encode()).hexdigest(), 16)
    return round(20 + (h % 50000) / 100.0, 2)


def yfinance_prices(syms):
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("yfinance not installed. Run: pip install yfinance  "
                 "(or use --source stub for offline testing)")
    out = {}
    data = yf.download(syms, period="1d", interval="1m",
                       progress=False, auto_adjust=True)
    # yfinance returns a multi-index frame for >1 symbol; grab last close.
    try:
        closes = data["Close"]
        last = closes.ffill().iloc[-1]
        if hasattr(last, "items"):
            for sym, px in last.items():
                if px == px:  # not NaN
                    out[sym] = round(float(px), 2)
        else:  # single symbol
            out[syms[0]] = round(float(last), 2)
    except Exception as e:
        sys.exit(f"Could not parse yfinance data: {e}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("symbols", nargs="+", help="tickers, e.g. AAPL MSFT")
    ap.add_argument("--source", choices=["yfinance", "stub"], default="yfinance")
    a = ap.parse_args()
    syms = [s.upper() for grp in a.symbols for s in grp.split()]
    if a.source == "stub":
        prices = {s: stub_price(s) for s in syms}
    else:
        prices = yfinance_prices(syms)
    print(json.dumps(prices))


if __name__ == "__main__":
    main()
