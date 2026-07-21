"""
Тести відображення ліквідаційної ціни (Liq. price) для відкритої позиції.

СТАТУС: SKIP — на dev-стенді ліквідація ще не реалізована.
Розслідування (липень 2026):
- UI показує Liq. price = "-" у рядку позиції та "TBD" у формі,
  для Cross і Isolated, при leverage 10x і 50x.
- API /v1/positions повертає позицію БЕЗ поля liquidation_price
  (лише size, entryPrice, leverage, margin, realizedPnl, unrealizedPnl,
  fundingCumulativeIndex).
- Market config /v1/markets має mm_ratio та liquidation_fee,
  але risk_factor=0 і status="New".
Тобто бекенд поки не рахує й не віддає liquidation_price.

Коли фічу активують: прибрати @pytest.mark.skip і перевірити,
що значення проходять (тест уже містить робочу логіку перевірки).
"""

import re

import pytest

pytestmark = [pytest.mark.liquidation, pytest.mark.btc]

from playwright.sync_api import expect

from pages.trading_page import TradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "200"

SKIP_REASON = (
    "Liquidation price not computed on dev yet: /v1/positions has no "
    "liquidation_price field, UI shows '-'. Remove skip when backend "
    "returns the field."
)


@pytest.mark.skip(reason=SKIP_REASON)
def test_long_position_shows_numeric_liquidation_price(
    authenticated_trading_page: TradingPage,
):
    """
    Long-позиція має показувати числову Liq. price, нижчу за entry price.

    Для Long ліквідація завжди НИЖЧЕ ціни входу (ціна падає → втрати →
    ліквідація). Перевіряємо, що Liq. price:
    1. не плейсхолдер ("-", "TBD"), а число;
    2. строго менша за entry price.
    """
    page = authenticated_trading_page
    page.ensure_cross_mode()
    page.set_leverage(50)
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(
        timeout=POSITION_TIMEOUT_MS
    )

    liq_text = page.long_position_liq_price.inner_text().strip()

    # Має бути число у форматі "58432.10", не "-"/"TBD".
    assert re.fullmatch(r"[\d,]+\.?\d*", liq_text), (
        f"Liq. price очікувалось число, отримано {liq_text!r}"
    )

    liq_value = float(liq_text.replace(",", ""))
    entry_value = page.get_long_position_entry_price()
    assert liq_value < entry_value, (
        f"Для Long ліквідація ({liq_value}) має бути нижче entry "
        f"({entry_value})"
    )

    page.cleanup_all()


@pytest.mark.skip(reason=SKIP_REASON)
def test_higher_leverage_moves_liquidation_closer_to_entry(
    authenticated_trading_page: TradingPage,
):
    """
    Вищий leverage → ліквідація ближче до entry price.

    Позиція 10x має ліквідацію далі від entry, ніж 50x
    (менше плече = більший буфер до ліквідації).
    """
    page = authenticated_trading_page

    page.ensure_cross_mode()
    page.set_leverage(10)
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(
        timeout=POSITION_TIMEOUT_MS
    )
    entry_10x = page.get_long_position_entry_price()
    liq_10x = float(
        page.long_position_liq_price.inner_text().replace(",", "")
    )
    distance_10x = entry_10x - liq_10x
    page.cleanup_all()

    page.set_leverage(50)
    page.open_long_position(POSITION_SIZE_USDC)
    expect(page.positions_tab_with_one).to_be_visible(
        timeout=POSITION_TIMEOUT_MS
    )
    entry_50x = page.get_long_position_entry_price()
    liq_50x = float(
        page.long_position_liq_price.inner_text().replace(",", "")
    )
    distance_50x = entry_50x - liq_50x
    page.cleanup_all()

    assert distance_50x < distance_10x, (
        f"50x-ліквідація має бути ближче до entry, ніж 10x: "
        f"50x-дистанція={distance_50x}, 10x-дистанція={distance_10x}"
    )
