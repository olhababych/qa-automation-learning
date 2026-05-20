from playwright.sync_api import expect
from pages.trading_page import TradingPage


def test_sign_in_button_not_visible_when_authenticated(
    authenticated_trading_page: TradingPage,
):
    """Авторизований юзер не повинен бачити кнопку Sign In."""
    authenticated_trading_page.open()
    expect(authenticated_trading_page.sign_in_button).not_to_be_visible()


def test_header_balance_displayed_when_authenticated(
    authenticated_trading_page: TradingPage,
):
    """Авторизований юзер бачить баланс у header у форматі $X.XX."""
    authenticated_trading_page.open()
    expect(authenticated_trading_page.header_balance).to_be_visible()