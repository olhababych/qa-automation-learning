import pytest

pytestmark = [pytest.mark.positions, pytest.mark.sol]
"""
Тести вкладок історії (Order history, Positions history) на SOLUSDC
після реальної угоди.
"""
from playwright.sync_api import expect
from pages.sol_trading_page import SolTradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "200"


def test_filled_order_appears_in_order_history(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Після Market-угоди SOL виконаний ордер з'являється в Order history (Filled)."""
    page = authenticated_sol_trading_page
    page.open()
    expect(page.no_positions_text).to_be_visible()

    try:
        page.open_long_position(POSITION_SIZE_USDC)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    finally:
        page.close_position()

    page.order_history_tab.click()
    expect(page.order_history_filled_status).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_closed_position_appears_in_positions_history(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Після закриття SOL-позиції запис з'являється в Positions history (CLOSED)."""
    page = authenticated_sol_trading_page
    page.open()
    expect(page.no_positions_text).to_be_visible()

    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    page.close_position()

    page.positions_history_tab.click()
    expect(page.positions_history_closed_status).to_be_visible(timeout=POSITION_TIMEOUT_MS)
