import pytest

pytestmark = [pytest.mark.reduce_only, pytest.mark.btc]
"""
Reduce Only тести в ISOLATED-режимі на BTCUSDC — дзеркало test_reduce_only.py.
Isolated тримає margin позиції окремо, тож reduce-only поведінка перевіряється
окремо від Cross. Фікстура перемикає акаунт на Isolated і повертає Cross.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "200"


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


def test_reduce_only_blocks_position_increase_isolated(isolated_mode: TradingPage):
    """Isolated: Reduce Only блокує збільшення існуючої позиції."""
    page = isolated_mode
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    margin_before = page.get_long_position_margin()

    page.select_long()
    page.enable_reduce_only()
    page.fill_size(POSITION_SIZE_USDC)
    page.buy_long_button.click()

    expect(page.reduce_only_error_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.positions_tab_with_one).to_be_visible()
    margin_after = page.get_long_position_margin()
    assert margin_before == margin_after, (
        f"Margin змінився після заблокованого RO: before={margin_before}, after={margin_after}"
    )


def test_reduce_only_does_not_flip_position_direction_isolated(isolated_mode: TradingPage):
    """Isolated: Reduce Only + менший Short зменшує Long, не перевертає в Short."""
    page = isolated_mode
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    # В Isolated margin — окремо алокований collateral (isolated_margin[market]),
    # він НЕ пропорційний розміру. Тому перевіряємо position.size, не margin:
    # reduce-only Short зменшує розмір позиції, напрямок лишається Long.
    size_before = page.get_long_position_size()
    size_before_text = page.long_position_size.inner_text()

    page.select_short()
    page.enable_reduce_only()
    page.fill_size(str(int(POSITION_SIZE_USDC) // 2))
    page.sell_short_button.click()

    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    long_indicator = page.page.get_by_role("img", name="long")
    expect(long_indicator).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    # Чекаємо реальної зміни size (без очікування читаємо старе значення),
    # потім перевіряємо: зменшився приблизно вдвічі (200-100=~100, ±15%).
    size_after = page.wait_for_long_position_size_change(from_text=size_before_text)
    expected_size = size_before / 2
    tolerance = expected_size * 0.15
    assert abs(size_after - expected_size) <= tolerance, (
        f"Size після RO Short ({size_after}) поза ±15% від очікуваного ({expected_size:.5f}). "
        f"Size до: {size_before}"
    )


def test_reduce_only_blocks_order_when_no_position_exists_isolated(isolated_mode: TradingPage):
    """Isolated: Reduce Only ордер без позиції відхиляється."""
    page = isolated_mode
    expect(page.no_positions_text).to_be_visible()

    page.select_long()
    page.enable_reduce_only()
    page.fill_size("200")
    page.buy_long_button.click()

    expect(page.reduce_only_error_toast).to_be_visible(timeout=10_000)
    expect(page.no_positions_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)
