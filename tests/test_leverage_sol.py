import pytest

pytestmark = [pytest.mark.leverage, pytest.mark.sol]

"""
Тести зміни leverage (плеча).

Перевіряють модалку Adjust BTCUSDC Leverage:
- відкриття при кліку на кнопку leverage
- закриття через Close без застосування змін
"""
import re
from playwright.sync_api import expect
from pages.sol_trading_page import SolTradingPage


def test_leverage_modal_opens_and_closes(
    authenticated_sol_trading_page: SolTradingPage,
):
    """
    Клік на кнопку leverage відкриває модалку Adjust BTCUSDC Leverage.
    Натискання Close закриває модалку без застосування змін.
    """
    authenticated_sol_trading_page.open()

    # Стартовий стан: модалка не видима
    expect(authenticated_sol_trading_page.leverage_modal_heading).not_to_be_visible()

    # Відкриваємо модалку
    authenticated_sol_trading_page.open_leverage_modal()
    expect(authenticated_sol_trading_page.leverage_modal_heading).to_be_visible()
    expect(authenticated_sol_trading_page.leverage_modal_confirm).to_be_visible()

    # Закриваємо
    authenticated_sol_trading_page.close_leverage_modal()
    expect(authenticated_sol_trading_page.leverage_modal_heading).not_to_be_visible()

    
def test_decrease_leverage_without_confirm_does_not_persist(
    authenticated_sol_trading_page: SolTradingPage,
    ):
    """
    Зменшення leverage через "-" у модалці і закриття через Close
    НЕ повинно зберігати зміну.
    """
    authenticated_sol_trading_page.open()

    # Платформа зберігає leverage між сесіями (не скидає на 50x при reload),
    # тож стартове значення непередбачуване. Явно встановлюємо відоме 50.
    authenticated_sol_trading_page.set_leverage(50)
    expect(authenticated_sol_trading_page.leverage_button).to_have_text(
        "50x", timeout=5_000
    )

    # Запам'ятовуємо стартове значення на кнопці leverage (наприклад "50x")
    initial_text = authenticated_sol_trading_page.leverage_button.inner_text()
    
    # Відкриваємо модалку
    authenticated_sol_trading_page.open_leverage_modal()
    expect(authenticated_sol_trading_page.leverage_modal_value).to_be_visible()
    
    # Зменшуємо на 1
    authenticated_sol_trading_page.decrease_leverage()
    
    # Закриваємо через Close (не Confirm!)
    authenticated_sol_trading_page.close_leverage_modal()
    
    # Перевіряємо: значення на кнопці leverage НЕ змінилось
    expect(authenticated_sol_trading_page.leverage_button).to_have_text(initial_text)