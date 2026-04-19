# Weekly Income Engine

An automation toolkit that runs once a week and produces a prioritized
action list across four realistic, low-time-per-week income streams:

1. **Dividend cashflow** — track a portfolio, project next 12 months of
   payouts, flag ex-dividend dates you should not miss.
2. **Covered-call scanner** — for shares you already own, surface the
   highest-premium strikes that collect weekly income without giving up
   your cost basis.
3. **Cash-secured put scanner (the wheel)** — sell weekly puts on
   tickers you'd be happy to own, sized to fit your cash budget.
4. **Affiliate content pipeline** — generate SEO-ready product review
   drafts from a keyword list you can publish on a blog / Medium / a
   newsletter.
5. **High-interest cash sweep** — compare current HYSA / T-bill / money
   market rates so idle cash keeps earning.

The engine runs in ~60 seconds a week and emits a single digest you can
act on in 15 minutes.

## Reality check

No software guarantees income. What this project *does* guarantee is
that the repetitive weekly work — scanning dividends, pricing options,
drafting posts, rate-shopping cash — is reduced to a single command.
Capital at risk and market outcomes are yours.

## Install

```bash
pip install -e .              # offline mode (sample data)
pip install -e '.[live]'      # live data via yfinance
```

## Run the weekly digest

```bash
income-engine run --portfolio examples/portfolio.yaml --out digest.md
```

Add `--live` to pull real prices/options/dividends from yfinance.

### Delivery

```bash
income-engine run --portfolio p.yaml --notify email --notify slack
```

Configure via environment:

| Variable | Purpose |
|----------|---------|
| `INCOME_SMTP_HOST` / `_PORT` / `_USER` / `_PASS` | SMTP auth |
| `INCOME_EMAIL_FROM` / `INCOME_EMAIL_TO`          | Sender / recipient |
| `INCOME_SLACK_WEBHOOK`                           | Incoming webhook URL |

## Schedule it

Add to crontab to run every Sunday at 6pm and email the digest:

```
0 18 * * 0 cd /path/to/repo && income-engine run \
    --portfolio portfolio.yaml --live --notify email
```

## Modules

| Command                    | What it does                                         |
| -------------------------- | ---------------------------------------------------- |
| `income-engine dividends`  | Project dividend cashflow + upcoming ex-div dates    |
| `income-engine options`    | Scan covered-call candidates on owned positions      |
| `income-engine wheel`      | Scan cash-secured puts within your cash budget       |
| `income-engine content`    | Draft affiliate review posts from a keyword file     |
| `income-engine cash`       | Compare HYSA / T-bill / MMF rates                    |
| `income-engine run`        | Run everything and write a consolidated digest       |

## Adapters

All market data flows through pluggable adapters in
`income_engine/adapters/`. The default adapters use deterministic sample
data so the tool runs offline. Swap in a real data provider (yfinance,
Polygon, Tradier, etc.) by implementing the adapter interface.
