import pytest

pytestmark = [pytest.mark.deposit_withdraw, pytest.mark.smoke]

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


def test_deposit_modal_opens_and_closes(
    authenticated_trading_page: TradingPage,
    ):
    """
    Клік на кнопку Deposit відкриває модалку Deposit.
    Натискання Close закриває модалку без транзакції.
    """
    authenticated_trading_page.open()

    # Стартовий стан: модалка не видима
    expect(authenticated_trading_page.deposit_modal_subtitle).not_to_be_visible()

    # Відкриваємо
    authenticated_trading_page.open_deposit_modal()
    expect(authenticated_trading_page.deposit_modal_subtitle).to_be_visible()

    # Закриваємо
    authenticated_trading_page.close_deposit_modal()
    expect(authenticated_trading_page.deposit_modal_subtitle).not_to_be_visible()


def test_withdraw_modal_opens_and_closes(
    authenticated_trading_page: TradingPage,
    ):
    """
    Клік на кнопку Withdraw відкриває модалку Withdraw.
    Натискання Close закриває модалку без транзакції.
    """
    authenticated_trading_page.open()

    # Стартовий стан: модалка не видима
    expect(authenticated_trading_page.withdraw_modal_subtitle).not_to_be_visible()

    # Відкриваємо
    authenticated_trading_page.open_withdraw_modal()
    expect(authenticated_trading_page.withdraw_modal_subtitle).to_be_visible()

    # Закриваємо
    authenticated_trading_page.close_withdraw_modal()
    expect(authenticated_trading_page.withdraw_modal_subtitle).not_to_be_visible()