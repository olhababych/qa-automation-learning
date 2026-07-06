import pytest

pytestmark = [pytest.mark.negative, pytest.mark.btc]
"""
Тести валідації форми ордера на BTCUSDC:
Buy/Long має бути неактивна при невалідному розмірі (порожній або 0).
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 10_000


def test_buy_long_enabled_with_valid_size(
    authenticated_trading_page: TradingPage,
):
    """Валідний розмір: кнопка Buy / Long активна (дизейбл керується валідністю)."""
    page = authenticated_trading_page
    page.open()

    page.select_long()
    page.fill_size("200")
    expect(page.buy_long_button).to_be_enabled(timeout=TIMEOUT_MS)


def test_buy_long_disabled_when_size_zero(
    authenticated_trading_page: TradingPage,
):
    """Нульовий розмір: кнопка Buy / Long неактивна (ордер нижче мінімуму)."""
    page = authenticated_trading_page
    page.open()

    page.select_long()
    page.fill_size("0")
    expect(page.buy_long_button).to_be_disabled(timeout=TIMEOUT_MS)
