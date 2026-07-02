import pytest

pytestmark = [pytest.mark.limit_orders, pytest.mark.btc]

"""
Тести редагування Limit ордерів на BTCUSDC (інлайн-редагування ціни).
"""

from playwright.sync_api import expect
from pages.trading_page import TradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "200"
LIMIT_LONG_PRICE = "50000"
EDITED_PRICE = "55000"


def _ensure_no_orders(page: TradingPage) -> None:
    page.orders_tab.click()
    # Стабілізація таблиці після create/edit. Критерій наявності ордера —
    # видимість олівця (надійніше за гонку з текстом-плейсхолдером).
    page.page.wait_for_timeout(1_500)
    if page.edit_first_order_button.is_visible():
        page.cancel_first_order()
    expect(page.no_orders_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_edit_limit_order_changes_price(
    authenticated_trading_page: TradingPage,
):
    """Редагування ціни Limit Long: нова ціна зберігається й відображається."""
    page = authenticated_trading_page
    page.open()
    _ensure_no_orders(page)

    try:
        page.create_limit_long_order(
            price=LIMIT_LONG_PRICE, size=POSITION_SIZE_USDC
        )
        page.orders_tab.click()
        expect(page.edit_first_order_button).to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )

        page.edit_first_order_price(EDITED_PRICE)

        expect(page.order_updated_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        expect(page.page.get_by_text(EDITED_PRICE, exact=True).first).to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )
    finally:
        _ensure_no_orders(page)
