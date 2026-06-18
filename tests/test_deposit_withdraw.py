"""
Тести функціональності Deposit / Withdraw модалок.

Модалки доступні з будь-якого торгового ринку (BTC / SOL) — поведінка
ідентична, тому тестуємо лише на BTCUSDC.

ВАЖЛИВО:
- Тести НЕ виконують реальних транзакцій — лише перевіряють UI/валідацію.
- Платформа НЕ блокує submit кнопку при невалідному amount — натомість
  показує inline-помилку під полем ("Enter a valid amount"). Це той патерн
  валідації, який ми тестуємо.
"""

from playwright.sync_api import expect

from pages.trading_page import TradingPage


def test_deposit_modal_opens(
    authenticated_trading_page: TradingPage,
):
    """
    Sanity check: Deposit модалка відкривається і показує очікувані елементи.
    """
    page = authenticated_trading_page
    page.open()

    page.open_deposit_modal()
    expect(page.deposit_modal_subtitle).to_be_visible(timeout=5_000)
    expect(page.deposit_amount_input).to_be_visible()
    expect(page.deposit_modal_submit).to_be_visible()


def test_withdraw_modal_opens(
    authenticated_trading_page: TradingPage,
):
    """
    Sanity check: Withdraw модалка відкривається і показує очікувані елементи.
    """
    page = authenticated_trading_page
    page.open()

    page.open_withdraw_modal()
    expect(page.withdraw_modal_subtitle).to_be_visible(timeout=5_000)
    expect(page.withdraw_amount_input).to_be_visible()
    expect(page.withdraw_modal_submit).to_be_visible()


def test_deposit_modal_shows_available_balance(
    authenticated_trading_page: TradingPage,
):
    """
    Deposit модалка показує доступний баланс зовнішнього wallet.

    Текст "Avail." має бути видимий — користувач має знати скільки може
    максимум депонувати.
    """
    page = authenticated_trading_page
    page.open()

    page.open_deposit_modal()
    expect(page.deposit_available_balance).to_be_visible(timeout=5_000)


def test_withdraw_modal_shows_withdrawable_balance(
    authenticated_trading_page: TradingPage,
):
    """
    Withdraw модалка показує доступний баланс trading account.

    Текст "Withdrawable" має бути видимий — користувач має знати скільки може
    максимум вивести з торгового рахунку.
    """
    page = authenticated_trading_page
    page.open()

    page.open_withdraw_modal()
    expect(page.withdraw_available_balance).to_be_visible(timeout=5_000)


def test_withdraw_below_minimum_shows_validation_error(
    authenticated_trading_page: TradingPage,
):
    """
    Withdraw з сумою нижче мінімуму показує inline-помилку.

    Мінімум на платформі = 1.00 USDC. Тест вводить 0.5 USDC і очікує
    появу тексту "Enter a valid amount" — захист від випадкового
    відправлення суми, нижчої за мінімум мережі.
    """
    page = authenticated_trading_page
    page.open()

    page.open_withdraw_modal()
    page.withdraw_amount_input.fill("0.5")
    # Платформа валідує LAZY — текст помилки з'являється тільки після
    # спроби натиснути Withdraw, не одразу під час введення.
    page.withdraw_modal_submit.click()
    expect(page.below_minimum_withdrawal_error).to_be_visible(timeout=5_000)
