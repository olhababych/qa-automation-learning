# QA Automation Learning

UI automation tests for a Solana-based trading platform built with Playwright + pytest, following Page Object Model architecture.

## Tech Stack

- **Python** 3.13
- **Playwright** for browser automation
- **pytest** as the test framework
- **pytest-playwright** for integration

## Project Structure
## Test Coverage

Current smoke test suite covers the guest (unauthenticated) state of the trading page:

- Page loads with correct URL
- Sign In button is present
- Trading pair selector is visible
- Sign In opens authentication modal (Dynamic SDK)
- Authentication modal can be closed
- Bottom panel tabs work (Positions, Orders, Positions history, Order history)
- Positions tab is active by default
- Size input field accepts numeric values

## Setup

### Prerequisites

- Python 3.11+
- macOS / Linux / Windows

### Installation

```bash
# Clone the repository
git clone https://github.com/olhababych/qa-automation-learning.git
cd qa-automation-learning

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Running Tests

```bash
# Run all tests with browser visible
pytest tests/test_smoke.py --headed -v

# Run in headless mode (faster, no browser window)
pytest tests/test_smoke.py -v

# Run a specific test
pytest tests/test_smoke.py::test_sign_in_opens_auth_modal --headed -v
```

## Locator Strategy

Tests use stable locators in order of preference:

1. `data-testid` attributes — most stable
2. ARIA roles via `get_by_role()` — semantic
3. Text content via `get_by_text()` — readable
4. CSS classes — only as last resort

## Roadmap

- [ ] Add parameterized tests for input validation
- [ ] Set up GitHub Actions CI/CD
- [ ] Web3 wallet authentication (Phantom via Dynamic SDK sandbox)
- [ ] Authenticated user scenarios (positions, orders, deposits)
- [ ] API testing layer with httpx

## Author

Olha Babych
