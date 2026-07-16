import pytest

pytestmark = [pytest.mark.positions, pytest.mark.sol]
"""
Take Profit / Stop Loss тести в ISOLATED-режимі на SOLUSDC — дзеркало
test_isolated_tpsl.py. Фікстура перемикає акаунт на Isolated, повертає Cross.
"""
from playwright.sync_api import expect
from pages.sol_trading_page import SolTradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "150"
# SOL ~76: для Long TP вище/SL нижче; для Short навпаки.
LONG_TP_PRICE = "150"
LONG_SL_PRICE = "30"
SHORT_TP_PRICE = "30"
SHORT_SL_PRICE = "150"


@pytest.fixture
def isolated_mode_sol(authenticated_sol_trading_page: SolTradingPage):
    page = authenticated_sol_trading_page
    page.open()
    page.cleanup_all()
    expect(page.no_positions_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    page.ensure_cross_mode()
    page.ensure_isolated_mode()
    yield page
    page.cleanup_all()
    try:
        page.ensure_cross_mode()
    except Exception:
        pass


def test_open_long_with_tpsl_isolated_sol(isolated_mode_sol: SolTradingPage):
    """Isolated SOL: Long з TP/SL відкривається, TP і SL ордери підтверджені."""
    page = isolated_mode_sol
    page.open_long_with_tpsl(
        size=POSITION_SIZE_USDC, tp_price=LONG_TP_PRICE, sl_price=LONG_SL_PRICE
    )
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.tp_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.sl_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_open_short_with_tpsl_isolated_sol(isolated_mode_sol: SolTradingPage):
    """Isolated SOL: Short з TP/SL відкривається, TP і SL ордери підтверджені."""
    page = isolated_mode_sol
    page.open_short_with_tpsl(
        size=POSITION_SIZE_USDC, tp_price=SHORT_TP_PRICE, sl_price=SHORT_SL_PRICE
    )
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.tp_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.sl_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
