import pytest

pytestmark = [pytest.mark.limit_orders, pytest.mark.sol]
"""
Тести редагування Limit ордерів на SOLUSDC (інлайн-редагування ціни).
"""
from playwright.sync_api import expect
from pages.sol_trading_page import SolTradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "200"
# SOL ~$70 — ставимо ціну НИЖЧЕ ринку, щоб Limit Long не виконався одразу.
LIMIT_LONG_PRICE = "30"
EDITED_PRICE = "35"


def _ensure_no_orders(page: SolTradingPage) -> None:
    page.orders_tab.click()
    page.page.wait_for_timeout(1_500)
    if page.edit_first_order_button.is_visible():
        page.cancel_first_order()
    expect(page.no_orders_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_edit_limit_order_changes_price(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Редагування ціни Limit Long на SOL: нова ціна зберігається й відображається."""
    page = authenticated_sol_trading_page
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
