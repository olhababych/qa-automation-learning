"""
Тести зміни leverage (плеча).

Перевіряють модалку Adjust BTCUSDC Leverage:
- відкриття при кліку на кнопку leverage
- закриття через Close без застосування змін
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage


def test_leverage_modal_opens_and_closes(
    authenticated_trading_page: TradingPage,
):
    """
    Клік на кнопку leverage відкриває модалку Adjust BTCUSDC Leverage.
    Натискання Close закриває модалку без застосування змін.
    """
    authenticated_trading_page.open()

    # Стартовий стан: модалка не видима
    expect(authenticated_trading_page.leverage_modal_heading).not_to_be_visible()

    # Відкриваємо модалку
    authenticated_trading_page.open_leverage_modal()
    expect(authenticated_trading_page.leverage_modal_heading).to_be_visible()
    expect(authenticated_trading_page.leverage_modal_confirm).to_be_visible()

    # Закриваємо
    authenticated_trading_page.close_leverage_modal()
    expect(authenticated_trading_page.leverage_modal_heading).not_to_be_visible()