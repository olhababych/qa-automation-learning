import pytest

pytestmark = [pytest.mark.negative, pytest.mark.btc]
"""
Негативні тести валідації TP/SL на BTCUSDC.
Для Long: TP має бути ВИЩЕ ринку. TP нижче ринку → помилка + Buy/Long disabled.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 15_000
POSITION_SIZE_USDC = "200"
# TP далеко НИЖЧЕ ринку BTC (~62000) — невалідно для Long.
INVALID_TP_BELOW_MARKET = "1000"


def test_tp_below_market_shows_error_and_disables_buy(
    authenticated_trading_page: TradingPage,
):
    """Long: TP нижче ринку показує помилку і блокує Buy / Long."""
    page = authenticated_trading_page
    page.open()

    page.select_long()
    page.fill_size(POSITION_SIZE_USDC)
    page.tpsl_checkbox.check(force=True)
    expect(page.tpsl_checkbox).to_be_checked(timeout=5_000)
    page.tp_price_input.fill(INVALID_TP_BELOW_MARKET)

    # Помилка з'являється, кнопка Buy/Long стає неактивною
    expect(page.tp_above_market_error).to_be_visible(timeout=TIMEOUT_MS)
    expect(page.buy_long_button).to_be_disabled(timeout=TIMEOUT_MS)
