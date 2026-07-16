import pytest

pytestmark = [pytest.mark.leverage, pytest.mark.btc]
"""
Leverage тести в ISOLATED-режимі на BTCUSDC. У моделі leverage[market] —
окреме per-market налаштування; перевіряємо, що зміна плеча з Confirm
застосовується й зберігається, коли акаунт у Isolated.
Фікстура перемикає на Isolated, повертає Cross у teardown.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 10_000


@pytest.fixture
def isolated_mode(authenticated_trading_page: TradingPage):
    page = authenticated_trading_page
    page.open()
    page.cleanup_all()
    expect(page.no_positions_text).to_be_visible(timeout=TIMEOUT_MS)
    page.ensure_cross_mode()
    page.ensure_isolated_mode()
    yield page
    page.cleanup_all()
    try:
        page.ensure_cross_mode()
    except Exception:
        pass


def test_set_leverage_persists_in_isolated_mode(isolated_mode: TradingPage):
    """Isolated: зміна плеча з Confirm застосовується й зберігається на кнопці."""
    page = isolated_mode
    # Встановлюємо відоме стартове значення, потім міняємо на інше з Confirm.
    page.set_leverage(50)
    expect(page.leverage_button).to_have_text("50x", timeout=TIMEOUT_MS)

    page.set_leverage(10)
    expect(page.leverage_button).to_have_text("10x", timeout=TIMEOUT_MS)
