import pytest

pytestmark = [pytest.mark.slow, pytest.mark.btc]
"""
ПОВІЛЬНІ інтеграційні тести реального спрацювання TP/SL за живим ринком.
Виключені з основного прогону: pytest -m "not slow".
Запускати окремо: pytest -m slow

Стратегія: TP і SL ставимо близько до ORACLE-ціни (±0.03%). TP/SL
тригеряться за Oracle, виконуються за Market. Oracle оновлюється, і за
кілька хвилин має зачепити один із рівнів, закривши позицію.
Перевіряємо, що позиція закрилась і потрапила в Positions history.

Недетермінованість: якщо ринок за 5 хв не зачепив жодного рівня, тест
падає з таймауту — це очікуваний ризик такого сценарію, не баг коду.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

POSITION_TIMEOUT_MS = 20_000
CLOSE_TIMEOUT_MS = 600_000  # 10 хв на спрацювання TP/SL
POSITION_SIZE_USDC = "200"


def test_tpsl_actually_triggers_and_closes_position(
    authenticated_trading_page: TradingPage,
):
    """Long з TP/SL близько до ринку: один із рівнів спрацьовує і закриває позицію."""
    page = authenticated_trading_page
    page.open()
    expect(page.no_positions_text).to_be_visible()

    try:
        # TP +0.03%, SL -0.03% від Oracle-ціни
        page.open_long_with_tpsl_near_market(POSITION_SIZE_USDC, offset_pct=0.03)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        # TP і SL ордери створені
        expect(page.tp_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)
        expect(page.sl_order_placed_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Чекаємо, поки ринок зачепить один із рівнів і закриє позицію
        page.wait_for_position_closed(timeout_ms=CLOSE_TIMEOUT_MS)

        # Позиція закрита → з'явилась у Positions history зі статусом CLOSED
        page.positions_history_tab.click()
        expect(page.positions_history_closed_status).to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )
    finally:
        # Повний teardown: скасувати залишкові TP/SL-ордери + закрити позицію.
        # cleanup_all безпечний — не валить тест, якщо вже чисто.
        page.cleanup_all()
