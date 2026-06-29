# QA Automation Learning — TrueFinance

UI automation tests for the **TrueFinance** perpetual DEX (BTC/USDC and SOL/USDC
markets), built with Playwright + pytest, following the Page Object Model (POM)
architecture.

---

## Tech Stack

- **Python** 3.13
- **Playwright** for browser automation
- **pytest** as the test framework
- **pytest-playwright** for integration
- **pytest-html** for self-contained HTML reports
- **pytest-rerunfailures** for automatic retries of flaky runs

---

## Test Coverage

67 end-to-end UI tests across both markets (BTC/USDC and SOL/USDC):

- **Smoke** — guest state: page load, Sign In, trading pair selector, auth modal, bottom-panel tabs, size input
- **Auth state** — authenticated session: balance, total equity, Sign In hidden
- **Trade form** — Buy/Long & Sell/Short buttons, size to asset-equivalent calc
- **Positions** — open/close (Long & Short), netting model, leverage edge cases (1x, 20x)
- **Limit orders** — create, cancel, notional validation, above-market fill behavior
- **Reduce Only** — blocks position increase, allows reduction, no direction flip
- **Leverage** — modal open/close, change without confirm does not persist
- **Deposit / Withdraw** — modals open/close, balance display, validation

---

## Setup

### Prerequisites

- Python 3.13+
- macOS / Linux / Windows

### Installation

```bash
git clone https://github.com/olhababych/qa-automation-learning.git
cd qa-automation-learning
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

---

## Authentication

Tests run against a pre-saved session (`auth_state.json`), not committed to git. Generate it locally:

```bash
python save_auth_state.py
```

The script opens a browser. Log in manually (Email / Google / Phantom), confirm you see your balance and positions, return to the terminal and press Enter. Sessions expire — regenerate if authenticated steps start failing.

---

## Environments

| Environment | URL | Balance | Test runs |
|---|---|---|---|
| dev | https://dex-dev.true.trading/ | testnet / demo | allowed |
| beta | https://beta-dex.truefinance.ai/ | demo (\$100K) | separate folder |
| prod | https://app.truefinance.ai/ | real funds | FORBIDDEN |

**Production Safety Guard.** `tests/conftest.py` contains a `SAFE_DOMAINS` whitelist. If `TradingPage.URL` does not contain an allowed domain, pytest aborts before running any tests. Tests place real orders, so non-testnet runs are blocked by design.

---

## Pre-condition Before EVERY Run

The platform must be in a clean state: BTC and SOL both Positions (0), Orders (0). If positions or orders remain from a previous run, close them manually — otherwise the first tests fail on the pre-condition, masking real issues. There is no cleanup fixture (intentional for MVP).

---

## Running Tests

```bash
pytest                  # full suite
pytest -v               # verbose, per-test status
pytest tests/test_positions.py -v
pytest -m smoke         # by marker
pytest -m "positions and btc"
```

On failure, tests embed a base64 screenshot into output, flooding the terminal. Write output to a file instead:

```bash
pytest -v > /tmp/out.txt 2>&1
tail -3 /tmp/out.txt
grep "PASSED\\|FAILED" /tmp/out.txt
```

---

## Markers

| Marker | Purpose |
|---|---|
| smoke | Basic UI sanity checks |
| positions | Open / close positions |
| limit_orders | Limit orders |
| reduce_only | Reduce Only functionality |
| deposit_withdraw | Deposit / Withdraw modals |
| leverage | Leverage changes |
| negative | Negative scenarios |
| btc | BTC/USDC market |
| sol | SOL/USDC market |

---

## Run Configuration

From `pytest.ini`: `--slowmo=500` (each action slowed 500ms for stability), `--reruns=2 --reruns-delay=3` (retry flaky tests), `--html=reports/report.html --self-contained-html`. A full run takes ~25-30 minutes due to slowmo.

---

## Project Structure

```
qa-automation-learning/
├── pages/
│   ├── base_page.py
│   ├── trading_page.py         # POM for BTC/USDC
│   └── sol_trading_page.py     # POM for SOL/USDC
├── tests/
│   ├── conftest.py             # fixtures, safety guard, screenshot hooks
│   └── test_*.py
├── pytest.ini
├── requirements.txt
├── save_auth_state.py
└── reports/
```

---

## Locator Strategy

Stable locators in order of preference:

1. `data-testid` attributes — most stable
2. ARIA roles via `get_by_role()` — semantic
3. Text content via `get_by_text()` — readable
4. CSS classes — last resort only

Where the platform lacks `data-testid`, positional locators are anchored from the end of the table row (`nth(-3)`) rather than the start, so they survive column-shift caused by DEF-001.

---

## Known Platform Defects

| # | Description | Status |
|---|---|---|
| DEF-001 | P&L column merges values without separator (`-0.08-0.78%`). Reproduces on dev and beta. | Margin locator anchored from row end `nth(-3)` |
| — | Leverage change on open position does not recalculate margin | Test marked `xfail` |
| — | Round-half-up on BTC conversion; orders near \$100 rejected | Use \$200 position size |
| — | Deposit/Withdraw submit not blocked on invalid amount | — |
| — | Withdraw validation lazy: error only after submit | — |
| — | Limit Long above market fills immediately at market price | accounted for |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| command not found: python | venv not activated | `source venv/bin/activate` |
| Failure on no_positions_text | dirty platform state | close positions/orders manually |
| Failure on authenticated steps | session expired | `python save_auth_state.py` |
| unrecognized arguments --reruns/--html | missing plugins | `pip install pytest-html pytest-rerunfailures` |
| Terminal flooded with base64 | screenshot in output | `pytest > /tmp/out.txt 2>&1` |

---

## Roadmap

- [ ] TP/SL (Take Profit / Stop Loss) test coverage
- [ ] Edit Limit order tests
- [ ] Order history / Positions history tab coverage
- [ ] Single-suite env config (ENV=dev / ENV=beta)
- [ ] GitHub Actions CI/CD
- [ ] API testing layer with httpx

---

## Author

Olha Babych
