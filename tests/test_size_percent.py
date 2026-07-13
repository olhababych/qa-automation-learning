import re
import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.btc]
"""
Тест поля відсотка розміру: ввід % задає Size як частку доступного notional.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 10_000


def test_percent_input_sets_size(
    authenticated_trading_page: TradingPage,
):
    """Ввід 50 у поле % робить поле Size ненульовим."""
    page = authenticated_trading_page
    page.open()

    page.select_long()
    # На старті Size порожній/нульовий
    page.size_percent_input.fill("50")

    # Size (USDC) стає ненульовим числом
    expect(page.size_input).to_have_value(
        re.compile(r"^[1-9]\d*$"), timeout=TIMEOUT_MS
    )
