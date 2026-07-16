import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.btc]
"""
Тести базової торгівлі в Isolated-режимі: відкриття позиції та створення
ордера, коли акаунт перемкнено на Isolated margin.

Режим account-wide, тож фікстура isolated_mode перемикає на Isolated перед
тестом і ГАРАНТОВАНО повертає Cross після (навіть при падінні), щоб не
лишати акаунт в Isolated для інших тестів.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 10_000
LIMIT_PRICE_FAR_BELOW = "30000"  # значно нижче ринку — ордер не виконається


@pytest.fixture
def isolated_mode(authenticated_trading_page: TradingPage):
    """Перемкнути акаунт на Isolated перед тестом, повернути Cross після."""
    page = authenticated_trading_page
    page.open()
    page.cleanup_all()  # чистий акаунт — інакше 409 при перемиканні
    expect(page.no_positions_text).to_be_visible(timeout=TIMEOUT_MS)
    page.ensure_cross_mode()   # привести до відомого стану Cross
    page.ensure_isolated_mode()  # потім перемкнути на Isolated
    yield page
    # Teardown: прибрати позиції/ордери, потім гарантовано повернути Cross
    page.cleanup_all()
    try:
        page.ensure_cross_mode()
    except Exception:
        pass


def test_open_position_in_isolated_mode(isolated_mode: TradingPage):
    """У Isolated-режимі Market Long позиція відкривається успішно."""
    page = isolated_mode
    page.open_long_position("200")
    expect(page.positions_tab_with_one).to_be_visible(timeout=20_000)


def test_create_limit_order_in_isolated_mode(isolated_mode: TradingPage):
    """У Isolated-режимі Limit-ордер (нижче ринку) створюється успішно."""
    page = isolated_mode
    page.create_limit_long_order(price=LIMIT_PRICE_FAR_BELOW, size="200")
    page.orders_tab.click()
    expect(page.no_orders_text).to_be_hidden(timeout=20_000)


def test_open_short_position_in_isolated_mode(isolated_mode: TradingPage):
    """У Isolated-режимі Market Short позиція відкривається успішно."""
    page = isolated_mode
    page.open_short_position("200")
    expect(page.positions_tab_with_one).to_be_visible(timeout=20_000)
    expect(page.short_position_indicator).to_be_visible(timeout=20_000)
