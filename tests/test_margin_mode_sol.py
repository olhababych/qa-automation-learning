import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.sol]
"""
Тест блокування (409) перемикання режиму маржі при відкритій SOL-позиції.
Режим Cross/Isolated — account-wide, тож відкрита позиція в БУДЬ-ЯКОМУ
ринку (тут SOL) має блокувати перемикання. Це головна цінність SOL-дубля.
"""
from playwright.sync_api import expect
from pages.sol_trading_page import SolTradingPage

TIMEOUT_MS = 10_000


def test_switch_margin_mode_blocked_with_open_sol_position(
    authenticated_sol_trading_page: SolTradingPage,
):
    """При відкритій SOL-позиції перемикання на Isolated блокується:
    режим лишається Cross (модалка відкрита, кнопка Isolated не з'явилась).
    """
    page = authenticated_sol_trading_page
    page.open()
    # Прибрати можливі залишки перед pre-condition
    page.cleanup_all()
    expect(page.no_positions_text).to_be_visible(timeout=TIMEOUT_MS)

    try:
        page.open_long_position("150")
        expect(page.positions_tab_with_one).to_be_visible(timeout=20_000)

        page.switch_margin_mode_to_isolated()

        # Блокування: режим НЕ перемкнувся. Модалка лишається, Isolated немає.
        expect(page.margin_mode_heading).to_be_visible(timeout=TIMEOUT_MS)
        expect(page.margin_mode_button_isolated).to_be_hidden(timeout=TIMEOUT_MS)
    finally:
        try:
            if page.margin_mode_heading.is_visible():
                page.margin_mode_close.click(timeout=5_000)
                expect(page.margin_mode_heading).to_be_hidden(timeout=10_000)
        except Exception:
            pass
        page.cleanup_all()
