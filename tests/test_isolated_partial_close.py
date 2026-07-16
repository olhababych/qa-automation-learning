import pytest

pytestmark = [pytest.mark.positions, pytest.mark.btc]
"""
Netting / часткове закриття (БЕЗ reduce-only) в ISOLATED-режимі на BTCUSDC —
дзеркало netting-тестів з test_positions.py. Три сценарії:
- протилежний Market того ж розміру закриває позицію повністю;
- менший протилежний зменшує позицію (в Isolated перевіряємо SIZE, бо
  margin — окремо алокований collateral, не пропорційний розміру);
- більший протилежний перевертає напрямок.
Фікстура перемикає на Isolated, повертає Cross у teardown.
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


def test_opposite_same_size_closes_position_isolated(isolated_mode: TradingPage):
    """Isolated: протилежний Market того ж розміру закриває позицію повністю."""
    page = isolated_mode
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    page.open_short_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_generic).to_have_text(
        "Positions (0)", timeout=POSITION_TIMEOUT_MS
    )
    expect(page.no_positions_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_smaller_opposite_reduces_position_isolated(isolated_mode: TradingPage):
    """Isolated: менший протилежний Market зменшує SIZE позиції (не закриває)."""
    page = isolated_mode
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    size_before = page.get_long_position_size()
    size_before_text = page.long_position_size.inner_text()

    page.open_short_position(str(int(POSITION_SIZE_USDC) // 2))
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    size_after = page.wait_for_long_position_size_change(from_text=size_before_text)
    expected_size = size_before / 2
    tolerance = expected_size * 0.15
    assert abs(size_after - expected_size) <= tolerance, (
        f"Size після netting ({size_after}) поза ±15% від очікуваного ({expected_size:.5f}). "
        f"Size до: {size_before}"
    )
    page.close_position()


def test_larger_opposite_flips_direction_isolated(isolated_mode: TradingPage):
    """Isolated: більший протилежний Market перевертає напрямок Long -> Short."""
    page = isolated_mode
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    page.open_short_position(str(int(POSITION_SIZE_USDC) * 2))
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    short_indicator = page.page.get_by_role("img", name="short")
    expect(short_indicator).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    page.close_position()
