import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.btc]
"""
Тести перемикання торгової пари через селектор.
"""
import re
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 15_000


def test_switch_pair_btc_to_sol_updates_url(
    authenticated_trading_page: TradingPage,
):
    """Перемикання BTC → SOL змінює URL на SOLUSDC."""
    page = authenticated_trading_page
    page.open()

    page.switch_to_pair("SOL")
    # URL оновлюється на SOLUSDC
    expect(page.page).to_have_url(
        re.compile(r"SOLUSDC"), timeout=TIMEOUT_MS
    )


def test_switch_pair_btc_to_sol_updates_header(
    authenticated_trading_page: TradingPage,
):
    """Перемикання BTC → SOL оновлює заголовок пари на SOL."""
    page = authenticated_trading_page
    page.open()

    page.switch_to_pair("SOL")
    # Кнопка пари тепер показує SOL
    expect(
        page.page.get_by_role("button", name=re.compile(r"^SOL \/USDC x\d+$"))
    ).to_be_visible(timeout=TIMEOUT_MS)
