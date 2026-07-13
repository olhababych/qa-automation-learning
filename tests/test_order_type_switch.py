import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.btc]
"""
Тести перемикання типу ордера Market <-> Limit.
Поле Price існує тільки в Limit; у Market його немає.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 10_000


def test_limit_shows_price_field(
    authenticated_trading_page: TradingPage,
):
    """Вибір Limit показує поле Price."""
    page = authenticated_trading_page
    page.open()

    page.select_limit_order_type()
    expect(page.price_input).to_be_visible(timeout=TIMEOUT_MS)


def test_market_hides_price_field(
    authenticated_trading_page: TradingPage,
):
    """Повернення на Market ховає поле Price."""
    page = authenticated_trading_page
    page.open()

    # Спершу Limit → Price видиме
    page.select_limit_order_type()
    expect(page.price_input).to_be_visible(timeout=TIMEOUT_MS)

    # У Limit два поля з placeholder='0' (Price + Size)
    price_like = page.page.locator("input[placeholder='0']")
    expect(price_like).to_have_count(2, timeout=TIMEOUT_MS)

    # Назад на Market → поле Price зникає, лишається лише Size (одне поле)
    page.select_market_order_type()
    expect(price_like).to_have_count(1, timeout=TIMEOUT_MS)
