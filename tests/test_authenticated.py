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


def test_buy_long_button_visible_by_default(
    authenticated_trading_page: TradingPage,
):
    """
    Після авторизації за замовчуванням обрано Long,
    тому action button має бути "Buy / Long".
    """
    authenticated_trading_page.open()
    expect(authenticated_trading_page.buy_long_button).to_be_visible()


def test_action_button_changes_when_short_selected(
    authenticated_trading_page: TradingPage,
):
    """
    При перемиканні з Long на Short action button міняється:
    "Buy / Long" зникає, "Sell / Short" з'являється.
    """
    authenticated_trading_page.open()
    
    # Перевіряємо стартовий стан: Buy / Long видимий
    expect(authenticated_trading_page.buy_long_button).to_be_visible()
    
    # Перемикаємо на Short
    authenticated_trading_page.select_short()
    
    # Перевіряємо: Sell / Short з'явився, Buy / Long зник
    expect(authenticated_trading_page.sell_short_button).to_be_visible()
    expect(authenticated_trading_page.buy_long_button).not_to_be_visible()


def test_deposit_and_withdraw_buttons_visible(
    authenticated_trading_page: TradingPage,
):
    """Авторизований юзер бачить кнопки Deposit і Withdraw для управління балансом."""
    authenticated_trading_page.open()
    expect(authenticated_trading_page.deposit_button).to_be_visible()
    expect(authenticated_trading_page.withdraw_button).to_be_visible()


def test_total_equity_shows_value_when_authenticated(
    authenticated_trading_page: TradingPage,
):
    """
    Авторизований юзер бачить Total equity у форматі "X.XX USDC".
    Для гостьового стану там буде "-".
    """
    authenticated_trading_page.open()
    expect(authenticated_trading_page.total_equity_value).to_be_visible()


def test_size_input_updates_btc_equivalent(
    authenticated_trading_page: TradingPage,
):
    """
    При введенні значення у поле Size платформа на льоту
    конвертує суму у BTC і показує "~X BTC" еквівалент.
    """
    authenticated_trading_page.open()
    
    # Стартовий стан: ~0 BTC видно (поле Size порожнє)
    expect(authenticated_trading_page.size_btc_equivalent).to_be_visible()
    expect(authenticated_trading_page.size_btc_equivalent).to_have_text("~0 BTC")
    
    # Вводимо 100 USDC у поле Size
    authenticated_trading_page.fill_size("100")
    
    # Перевіряємо: значення BTC еквіваленту змінилось
    # (НЕ "~0 BTC" — це означає, що відбулась конвертація)
    expect(authenticated_trading_page.size_btc_equivalent).not_to_have_text("~0 BTC")