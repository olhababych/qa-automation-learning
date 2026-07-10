import pytest

pytestmark = [pytest.mark.positions, pytest.mark.btc]
"""
Тести Take Profit / Stop Loss на BTCUSDC.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "150"
# TP вище ринку, SL нижче ринку — з запасом, щоб не спрацювали одразу.
TP_PRICE = "75000"
SL_PRICE = "56000"


def test_tpsl_checkbox_reveals_price_fields(
    authenticated_trading_page: TradingPage,
):
    """Увімкнення чекбока Take Profit / Stop Loss показує поля TP Price і SL Price."""
    page = authenticated_trading_page
    page.open()

    # TP/SL тепер увімкнений за замовчуванням — поля видимі одразу
    expect(page.tpsl_checkbox).to_be_checked(timeout=5_000)
    expect(page.tp_price_input).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.sl_price_input).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    # Після зняття галки поля зникають
    page.tpsl_checkbox.uncheck(force=True)
    expect(page.tpsl_checkbox).not_to_be_checked(timeout=5_000)
    expect(page.tp_price_input).to_be_hidden(timeout=POSITION_TIMEOUT_MS)


def test_open_long_with_tpsl_shows_in_position(
    authenticated_trading_page: TradingPage,
):
    """Long з TP/SL: позиція відкривається, TP і SL відображаються в Auto close."""
    page = authenticated_trading_page
    page.open()
    expect(page.no_positions_text).to_be_visible()

    try:
        page.open_long_with_tpsl(
            size=POSITION_SIZE_USDC, tp_price=TP_PRICE, sl_price=SL_PRICE
        )
        # Позиція створилась
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        # Тости підтвердження TP і SL ордерів
        expect(page.tp_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        expect(page.sl_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        # У рядку позиції (Auto close) видно TP і SL значення
        expect(page.page.get_by_text("TP", exact=False).first).to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )
    finally:
        page.close_position()
