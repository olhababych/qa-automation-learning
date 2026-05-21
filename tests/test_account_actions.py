"""
Тести фінансових операцій акаунту.

Перевіряють доступність кнопок управління балансом
для авторизованого користувача.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage


def test_deposit_and_withdraw_buttons_visible(
    authenticated_trading_page: TradingPage,
):
    """Авторизований юзер бачить кнопки Deposit і Withdraw для управління балансом."""
    authenticated_trading_page.open()
    expect(authenticated_trading_page.deposit_button).to_be_visible()
    expect(authenticated_trading_page.withdraw_button).to_be_visible()