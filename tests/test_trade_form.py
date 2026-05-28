"""
Тести форми торгівлі (Trade form).

Перевіряють інтерактивну поведінку Trade-форми:
- Buy/Long як action button за замовчуванням
- Перемикач Long↔Short змінює action button
- Поле Size конвертує USDC у BTC еквівалент
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage


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

    # Стартовий стан: Buy / Long видимий
    expect(authenticated_trading_page.buy_long_button).to_be_visible()

    # Перемикаємо на Short
    authenticated_trading_page.select_short()

    # Sell / Short з'явився, Buy / Long зник
    expect(authenticated_trading_page.sell_short_button).to_be_visible()
    expect(authenticated_trading_page.buy_long_button).not_to_be_visible()


def test_size_input_updates_btc_equivalent(
    authenticated_trading_page: TradingPage,
):
    """
    При введенні значення у поле Size платформа конвертує суму у BTC
    і показує "~X BTC" еквівалент.

    Примітка про новий UX (dex-dev.true.trading): на свіжо завантаженій
    сторінці текст "~0 BTC" БІЛЬШЕ не показується (на старому домені
    показувався). BTC equivalent з'являється тільки після введення
    ненульового значення. Тест адаптовано: перевіряємо тільки появу
    BTC equivalent після введення.
    """
    authenticated_trading_page.open()
    # Вводимо 100 USDC у поле Size
    authenticated_trading_page.fill_size("100")
    # BTC equivalent з'явився і показує НЕ-нульове значення
    expect(authenticated_trading_page.size_btc_equivalent).to_be_visible()
    expect(authenticated_trading_page.size_btc_equivalent).not_to_have_text("~0 BTC")