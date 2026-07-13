import pytest

pytestmark = [pytest.mark.negative, pytest.mark.btc]
"""
Негативні тести валідації SL та Short-TP на BTCUSDC.
Правила відносно ринку (BTC ~63000):
- Long:  TP вище ринку, SL нижче ринку.
- Short: TP нижче ринку, SL вище ринку.
Ввід "не з того боку" → помилка + кнопка дії disabled.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 15_000
SIZE = "200"
ABOVE_MARKET = "99999"   # завідомо вище ринку
BELOW_MARKET = "1000"    # завідомо нижче ринку


def test_long_sl_above_market_shows_error_and_disables_buy(
    authenticated_trading_page: TradingPage,
):
    """Long: SL вище ринку → 'SL must be below market' + Buy/Long disabled."""
    page = authenticated_trading_page
    page.open()

    page.select_long()
    page.fill_size(SIZE)
    page.tpsl_checkbox.check(force=True)
    expect(page.tpsl_checkbox).to_be_checked(timeout=5_000)
    page.sl_price_input.fill(ABOVE_MARKET)

    expect(page.sl_below_market_error).to_be_visible(timeout=TIMEOUT_MS)
    expect(page.buy_long_button).to_be_disabled(timeout=TIMEOUT_MS)


def test_short_tp_above_market_shows_error_and_disables_sell(
    authenticated_trading_page: TradingPage,
):
    """Short: TP вище ринку → 'TP must be below market' + Sell/Short disabled."""
    page = authenticated_trading_page
    page.open()

    page.select_short()
    page.fill_size(SIZE)
    page.tpsl_checkbox.check(force=True)
    expect(page.tpsl_checkbox).to_be_checked(timeout=5_000)
    page.tp_price_input.fill(ABOVE_MARKET)

    expect(page.tp_below_market_error).to_be_visible(timeout=TIMEOUT_MS)
    expect(page.sell_short_button).to_be_disabled(timeout=TIMEOUT_MS)


def test_short_sl_below_market_shows_error_and_disables_sell(
    authenticated_trading_page: TradingPage,
):
    """Short: SL нижче ринку → 'SL must be above market' + Sell/Short disabled."""
    page = authenticated_trading_page
    page.open()

    page.select_short()
    page.fill_size(SIZE)
    page.tpsl_checkbox.check(force=True)
    expect(page.tpsl_checkbox).to_be_checked(timeout=5_000)
    page.sl_price_input.fill(BELOW_MARKET)

    expect(page.sl_above_market_error).to_be_visible(timeout=TIMEOUT_MS)
    expect(page.sell_short_button).to_be_disabled(timeout=TIMEOUT_MS)
