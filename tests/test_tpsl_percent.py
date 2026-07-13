import re
import pytest

pytestmark = [pytest.mark.btc, pytest.mark.smoke]
"""
Тест TP/SL через відсотки: ввід Profit % автозаповнює TP Price.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 10_000
SIZE = "200"


def test_profit_percent_fills_tp_price(
    authenticated_trading_page: TradingPage,
):
    """Ввід Profit % (для Long) автозаповнює поле TP Price ненульовою ціною."""
    page = authenticated_trading_page
    page.open()

    page.select_long()
    page.fill_size(SIZE)
    page.tpsl_checkbox.check(force=True)
    expect(page.tpsl_checkbox).to_be_checked(timeout=5_000)

    # TP Price спочатку порожній
    expect(page.tp_price_input).to_have_value("", timeout=TIMEOUT_MS)

    # Вводимо 10% прибутку → TP Price має автозаповнитись
    page.tp_profit_percent_input.fill("10")
    expect(page.tp_price_input).not_to_have_value("", timeout=TIMEOUT_MS)
