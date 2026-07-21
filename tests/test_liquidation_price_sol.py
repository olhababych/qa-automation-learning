"""
Тести відображення ліквідаційної ціни (Liq. price) — SOLUSDC.

Дзеркало test_liquidation_price.py для SOL-пари.
СТАТУС: SKIP — на dev ліквідація ще не рахується (див. деталі в BTC-файлі).

Логіка: Long -> liq нижче entry; Short -> liq вище entry;
вище плече -> liq ближче до entry.
"""

import re

import pytest

pytestmark = [pytest.mark.liquidation, pytest.mark.sol]

from playwright.sync_api import expect

from pages.sol_trading_page import SolTradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "200"
NUMERIC_RE = re.compile(r"[\d,]+\.?\d*")

SKIP_REASON = (
    "Liquidation price not computed on dev yet: /v1/positions has no "
    "liquidation_price field, UI shows '-'. Remove skip when backend "
    "returns the field."
)


def _to_float(text: str) -> float:
    return float(text.replace(",", ""))


# --------------------------- Cross ---------------------------

@pytest.mark.skip(reason=SKIP_REASON)
def test_long_liquidation_price_below_entry_cross_sol(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Long/Cross/50x SOL: Liq. price — число, нижче entry."""
    page = authenticated_sol_trading_page
    page.ensure_cross_mode()
    page.set_leverage(50)
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    liq_text = page.long_position_liq_price.inner_text().strip()
    assert NUMERIC_RE.fullmatch(liq_text), f"очікувалось число, отримано {liq_text!r}"
    assert _to_float(liq_text) < page.get_long_position_entry_price()

    page.cleanup_all()


@pytest.mark.skip(reason=SKIP_REASON)
def test_short_liquidation_price_above_entry_cross_sol(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Short/Cross/50x SOL: Liq. price — число, вище entry."""
    page = authenticated_sol_trading_page
    page.ensure_cross_mode()
    page.set_leverage(50)
    page.open_short_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    liq_text = page.short_position_liq_price.inner_text().strip()
    assert NUMERIC_RE.fullmatch(liq_text), f"очікувалось число, отримано {liq_text!r}"
    assert _to_float(liq_text) > page.get_short_position_entry_price()

    page.cleanup_all()


@pytest.mark.skip(reason=SKIP_REASON)
def test_higher_leverage_moves_liq_closer_to_entry_cross_sol(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Long/Cross SOL: 50x-ліквідація ближче до entry, ніж 10x."""
    page = authenticated_sol_trading_page
    page.ensure_cross_mode()

    page.set_leverage(10)
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    dist_10x = page.get_long_position_entry_price() - _to_float(
        page.long_position_liq_price.inner_text()
    )
    page.cleanup_all()

    page.set_leverage(50)
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    dist_50x = page.get_long_position_entry_price() - _to_float(
        page.long_position_liq_price.inner_text()
    )
    page.cleanup_all()

    assert dist_50x < dist_10x, f"50x={dist_50x}, 10x={dist_10x}"


# --------------------------- Isolated ---------------------------

@pytest.mark.skip(reason=SKIP_REASON)
def test_long_liquidation_price_below_entry_isolated_sol(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Long/Isolated/50x SOL: Liq. price — число, нижче entry."""
    page = authenticated_sol_trading_page
    page.ensure_cross_mode()
    page.ensure_isolated_mode()
    page.set_leverage(50)
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    liq_text = page.long_position_liq_price.inner_text().strip()
    assert NUMERIC_RE.fullmatch(liq_text), f"очікувалось число, отримано {liq_text!r}"
    assert _to_float(liq_text) < page.get_long_position_entry_price()

    page.cleanup_all()
    page.ensure_cross_mode()


@pytest.mark.skip(reason=SKIP_REASON)
def test_short_liquidation_price_above_entry_isolated_sol(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Short/Isolated/50x SOL: Liq. price — число, вище entry."""
    page = authenticated_sol_trading_page
    page.ensure_cross_mode()
    page.ensure_isolated_mode()
    page.set_leverage(50)
    page.open_short_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    liq_text = page.short_position_liq_price.inner_text().strip()
    assert NUMERIC_RE.fullmatch(liq_text), f"очікувалось число, отримано {liq_text!r}"
    assert _to_float(liq_text) > page.get_short_position_entry_price()

    page.cleanup_all()
    page.ensure_cross_mode()


@pytest.mark.skip(reason=SKIP_REASON)
def test_higher_leverage_moves_liq_closer_to_entry_isolated_sol(
    authenticated_sol_trading_page: SolTradingPage,
):
    """Long/Isolated SOL: 50x-ліквідація ближче до entry, ніж 10x."""
    page = authenticated_sol_trading_page
    page.ensure_cross_mode()
    page.ensure_isolated_mode()

    page.set_leverage(10)
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    dist_10x = page.get_long_position_entry_price() - _to_float(
        page.long_position_liq_price.inner_text()
    )
    page.cleanup_all()

    page.set_leverage(50)
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    dist_50x = page.get_long_position_entry_price() - _to_float(
        page.long_position_liq_price.inner_text()
    )
    page.cleanup_all()
    page.ensure_cross_mode()

    assert dist_50x < dist_10x, f"50x={dist_50x}, 10x={dist_10x}"
