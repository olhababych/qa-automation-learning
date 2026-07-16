import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.sol]
"""
Тести базової торгівлі в Isolated-режимі на SOL-парі: відкриття Long і
Short позицій, коли акаунт перемкнено на Isolated margin.

Режим account-wide — фікстура нормалізує старт (Cross), перемикає на
Isolated, і ГАРАНТОВАНО повертає Cross у teardown.
"""
from playwright.sync_api import expect
from pages.sol_trading_page import SolTradingPage

TIMEOUT_MS = 10_000


@pytest.fixture
def isolated_mode_sol(authenticated_sol_trading_page: SolTradingPage):
    """Перемкнути акаунт на Isolated перед тестом, повернути Cross після."""
    page = authenticated_sol_trading_page
    page.open()
    page.cleanup_all()  # чистий акаунт — інакше 409
    expect(page.no_positions_text).to_be_visible(timeout=TIMEOUT_MS)
    page.ensure_cross_mode()     # нормалізувати старт
    page.ensure_isolated_mode()  # перемкнути на Isolated
    yield page
    page.cleanup_all()
    try:
        page.ensure_cross_mode()
    except Exception:
        pass


def test_open_long_position_in_isolated_mode_sol(isolated_mode_sol: SolTradingPage):
    """У Isolated-режимі Market Long SOL позиція відкривається успішно."""
    page = isolated_mode_sol
    page.open_long_position("150")
    expect(page.positions_tab_with_one).to_be_visible(timeout=20_000)


def test_open_short_position_in_isolated_mode_sol(isolated_mode_sol: SolTradingPage):
    """У Isolated-режимі Market Short SOL позиція відкривається успішно."""
    page = isolated_mode_sol
    page.open_short_position("150")
    expect(page.positions_tab_with_one).to_be_visible(timeout=20_000)
    expect(page.short_position_indicator).to_be_visible(timeout=20_000)


def test_create_limit_long_order_in_isolated_mode_sol(isolated_mode_sol: SolTradingPage):
    """У Isolated-режимі Limit Long SOL ордер (нижче ринку) створюється успішно."""
    page = isolated_mode_sol
    page.create_limit_long_order(price="60", size="150")  # нижче ринку (~76)
    page.orders_tab.click()
    expect(page.no_orders_text).to_be_hidden(timeout=20_000)


def test_create_limit_short_order_in_isolated_mode_sol(isolated_mode_sol: SolTradingPage):
    """У Isolated-режимі Limit Short SOL ордер (вище ринку) створюється успішно."""
    page = isolated_mode_sol
    page.create_limit_short_order(price="500", size="150")  # значно вище ринку
    page.orders_tab.click()
    expect(page.no_orders_text).to_be_hidden(timeout=20_000)
