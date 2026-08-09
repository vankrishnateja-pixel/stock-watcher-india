#!/usr/bin/env python3
"""
market_data.py — fetch current prices for the paper-trading loop.

Prints a JSON object like {"AAPL": 190.12, "MSFT": 402.5}.

Sources:
  --source yfinance   (default) real quotes fetched directly from Yahoo
                      Finance's public chart API over plain HTTPS. Requires
                      internet + the `requests` package. (Despite the source
                      name, this no longer goes through the `yfinance`
                      package/`curl_cffi` — see note below.)
  --source stub       deterministic fake prices for offline testing of the
                      pipeline. Reads overrides from the STUB_PRICES env var
                      (JSON), otherwise makes up a stable pseudo-price per
                      ticker. NEVER use stub prices for anything you care about.

Note: the `yfinance` package fetches through `curl_cffi`, which impersonates
a browser TLS fingerprint to get past Yahoo's bot detection. That fingerprint
doesn't survive being relayed through a TLS-intercepting proxy (connection
resets on every request), which is exactly the environment this often runs
in. A plain `requests` call with a normal User-Agent hits the same Yahoo
endpoint yfinance uses under the hood and works fine, so that's what this
does now — real Yahoo quotes, no proxy-breaking impersonation layer.
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


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
}


def yfinance_prices(syms):
    try:
        import requests
    except ImportError:
        sys.exit("requests not installed. Run: pip install requests  "
                 "(or use --source stub for offline testing)")
    out = {}
    for sym in syms:
        try:
            r = requests.get(YAHOO_CHART_URL.format(sym=sym), headers=YAHOO_HEADERS,
                             timeout=15)
            r.raise_for_status()
            result = r.json()["chart"]["result"][0]
            price = result["meta"]["regularMarketPrice"]
            out[sym] = round(float(price), 2)
        except Exception as e:
            sys.exit(f"Could not fetch price for {sym} from Yahoo Finance: {e}")
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
