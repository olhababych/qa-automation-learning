import pytest

pytestmark = [pytest.mark.positions, pytest.mark.btc]
"""
Take Profit / Stop Loss тести в ISOLATED-режимі на BTCUSDC — дзеркало
test_tpsl.py + test_tpsl_short.py. Фікстура перемикає акаунт на Isolated,
повертає Cross у teardown.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "150"
# BTC ~64000: для Long TP вище/SL нижче; для Short навпаки.
LONG_TP_PRICE = "75000"
LONG_SL_PRICE = "56000"
SHORT_TP_PRICE = "50000"
SHORT_SL_PRICE = "75000"


@pytest.fixture
def isolated_mode(authenticated_trading_page: TradingPage):
    page = authenticated_trading_page
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


def test_open_long_with_tpsl_isolated(isolated_mode: TradingPage):
    """Isolated: Long з TP/SL відкривається, TP і SL ордери підтверджені."""
    page = isolated_mode
    page.open_long_with_tpsl(
        size=POSITION_SIZE_USDC, tp_price=LONG_TP_PRICE, sl_price=LONG_SL_PRICE
    )
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.tp_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.sl_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_open_short_with_tpsl_isolated(isolated_mode: TradingPage):
    """Isolated: Short з TP/SL відкривається, TP і SL ордери підтверджені."""
    page = isolated_mode
    page.open_short_with_tpsl(
        size=POSITION_SIZE_USDC, tp_price=SHORT_TP_PRICE, sl_price=SHORT_SL_PRICE
    )
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.tp_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.sl_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
