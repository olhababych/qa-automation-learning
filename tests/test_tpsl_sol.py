import pytest

pytestmark = [pytest.mark.positions, pytest.mark.sol]
"""
Тести Take Profit / Stop Loss на SOLUSDC.
"""
from playwright.sync_api import expect
from pages.sol_trading_page import SolTradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "150"
# SOL ~$70 — TP вище ринку, SL нижче, з запасом щоб не спрацювали одразу.
TP_PRICE = "90"
SL_PRICE = "50"


def test_tpsl_checkbox_reveals_price_fields(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Увімкнення чекбока TP/SL показує поля TP Price і SL Price на SOL."""
    page = authenticated_sol_trading_page
    page.open()

    expect(page.tp_price_input).to_be_hidden()

    page.tpsl_checkbox.check(force=True)
    expect(page.tpsl_checkbox).to_be_checked(timeout=5_000)

    expect(page.tp_price_input).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.sl_price_input).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_open_long_with_tpsl_shows_in_position(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Long SOL з TP/SL: позиція відкривається, TP і SL у Auto close."""
    page = authenticated_sol_trading_page
    page.open()
    expect(page.no_positions_text).to_be_visible()

    try:
        page.open_long_with_tpsl(
            size=POSITION_SIZE_USDC, tp_price=TP_PRICE, sl_price=SL_PRICE
        )
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        expect(page.tp_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        expect(page.sl_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        expect(page.page.get_by_text("TP", exact=False).first).to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )
    finally:
        page.close_position()
