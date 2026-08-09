#!/usr/bin/env bash
# One iteration of the paper-trading loop.
# Schedule THIS (e.g. every 3 hours) via a Claude Code routine or cron.
#
# Flow:
#   1. figure out which tickers we care about
#   2. fetch current prices
#   3. deterministic termination check (cheap; skips the model when we're done)
#   4. if still going, hand the decision to Claude Code with the skill
#
# Set SOURCE=stub to test offline; leave default (yfinance) on your machine.
set -euo pipefail
cd "$(dirname "$0")"

SOURCE="${SOURCE:-yfinance}"

SYMS="$(python3 scripts/portfolio.py symbols)"
PRICES="$(python3 scripts/market_data.py $SYMS --source "$SOURCE")"

echo "[$(date -u +%FT%TZ)] prices: $PRICES"

# Termination pre-check. status exits 10 when a STOP condition is hit.
if ! python3 scripts/portfolio.py status --prices "$PRICES"; then
  echo "Loop halting — stop condition met. No model call this run."
  exit 0
fi

# Still running: let Claude Code analyze and act, passing in the prices so it
# doesn't refetch. The /paper-trade skill defines exactly what it may do.
claude -p "/paper-trade current_prices=$PRICES" --output-format text
