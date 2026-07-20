import pytest

pytestmark = [pytest.mark.positions, pytest.mark.btc]
"""
Тест Take Profit / Stop Loss для Short-позиції на BTCUSDC.
Для Short: TP нижче ринку, SL вище ринку.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "150"
# BTC ~62000: TP нижче ринку, SL вище — з запасом.
TP_PRICE = "50000"
SL_PRICE = "75000"


def test_open_short_with_tpsl_shows_in_position(
    authenticated_trading_page: TradingPage,
):
    """Short з TP/SL: позиція відкривається, TP і SL відображаються в Auto close."""
    page = authenticated_trading_page
    page.open()
    expect(page.no_positions_text).to_be_visible()

    try:
        page.open_short_with_tpsl(
            size=POSITION_SIZE_USDC, tp_price=TP_PRICE, sl_price=SL_PRICE
        )
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        expect(page.tp_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        expect(page.sl_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    finally:
        # cleanup_all замість close_position: TP/SL лишає окремі
        # TP/SL-ордери в Orders — без їх скасування орфани валять сусідів.
        page.cleanup_all()
