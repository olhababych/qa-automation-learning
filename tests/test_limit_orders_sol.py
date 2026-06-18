"""
Тести створення та скасування Limit ордерів на SOLUSDC.

Limit ордер — ордер з фіксованою ціною, що НЕ виконується одразу,
а очікує досягнення вказаної ціни на ринку. Ми ставимо ціни далеко
від ринку (30 для Long, 100 для Short при SOL ~65), щоб
ордери залишались відкритими для тестування лайфциклу.

ВАЖЛИВО про cleanup:
- Тести залишають ордер після створення, тому cleanup у finally обов'язковий.
- Pre-condition авто-cleanup: якщо ордер залишився з попереднього прогону —
  скасовується до початку тесту.
"""

from playwright.sync_api import expect

from pages.sol_trading_page import SolTradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "200"

# Ціна Limit Long — нижче поточної ринкової ($65+), щоб ордер
# НЕ виконався одразу, а залишився у списку Orders для тестування.
LIMIT_LONG_PRICE = "30"

# Ціна Limit Short — вище поточної ринкової, з тих самих міркувань.
LIMIT_SHORT_PRICE = "80"


def _ensure_no_orders(page: SolTradingPage) -> None:
    """Гарантувати порожній стан Orders. Скасувати залишений ордер якщо є."""
    page.orders_tab.click()
    if not page.no_orders_text.is_visible():
        page.cancel_first_order()
    expect(page.no_orders_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_create_limit_long_order_appears_in_orders(
    authenticated_sol_trading_page: SolTradingPage,
):
    """
    Створення Limit Long ордера: ордер з'являється у списку Orders.

    Сценарій:
    1. Pre-condition: ордерів немає.
    2. Створюємо Limit Long на $30 (нижче ринку).
    3. Перевіряємо: "No open orders" зник.
    4. Cleanup у finally: скасувати ордер.
    """
    page = authenticated_sol_trading_page
    page.open()
    _ensure_no_orders(page)

    try:
        page.create_limit_long_order(price=LIMIT_LONG_PRICE, size=POSITION_SIZE_USDC)
        page.orders_tab.click()
        expect(page.no_orders_text).not_to_be_visible(timeout=POSITION_TIMEOUT_MS)
    finally:
        page.cancel_first_order()


def test_create_limit_short_order_appears_in_orders(
    authenticated_sol_trading_page: SolTradingPage,
):
    """
    Створення Limit Short ордера: ордер з'являється у списку Orders.

    Сценарій:
    1. Pre-condition: ордерів немає.
    2. Створюємо Limit Short на $100 (вище ринку).
    3. Перевіряємо: "No open orders" зник.
    4. Cleanup у finally: скасувати ордер.
    """
    page = authenticated_sol_trading_page
    page.open()
    _ensure_no_orders(page)

    try:
        page.create_limit_short_order(price=LIMIT_SHORT_PRICE, size=POSITION_SIZE_USDC)
        page.orders_tab.click()
        expect(page.no_orders_text).not_to_be_visible(timeout=POSITION_TIMEOUT_MS)
    finally:
        page.cancel_first_order()


def test_cancel_limit_long_order_removes_it(
    authenticated_sol_trading_page: SolTradingPage,
):
    """
    Скасування Limit Long ордера: після cancel ордер зникає зі списку.

    Сценарій:
    1. Pre-condition: ордерів немає.
    2. Створюємо Limit Long на $30.
    3. Скасовуємо через UI (× → confirm modal → Cancel order).
    4. Перевіряємо: "No open orders" знов видно.

    Cleanup не потрібен — тест сам закриває ордер як основну дію.
    """
    page = authenticated_sol_trading_page
    page.open()
    _ensure_no_orders(page)

    # Дія 1: створити Limit Long
    page.create_limit_long_order(price=LIMIT_LONG_PRICE, size=POSITION_SIZE_USDC)
    page.orders_tab.click()
    expect(page.no_orders_text).not_to_be_visible(timeout=POSITION_TIMEOUT_MS)

    # Дія 2: скасувати ордер
    page.cancel_first_order()

    # Перевірка: ордер зник зі списку
    expect(page.no_orders_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)
