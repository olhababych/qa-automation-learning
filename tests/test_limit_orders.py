import pytest

pytestmark = [pytest.mark.limit_orders, pytest.mark.btc]

"""
Тести створення та скасування Limit ордерів на BTCUSDC.

Limit ордер — ордер з фіксованою ціною, що НЕ виконується одразу,
а очікує досягнення вказаної ціни на ринку. Ми ставимо ціни далеко
від ринку (50000 для Long, 80000 для Short при BTC ~64000), щоб
ордери залишались відкритими для тестування лайфциклу.

ВАЖЛИВО про cleanup:
- Тести залишають ордер після створення, тому cleanup у finally обов'язковий.
- Pre-condition авто-cleanup: якщо ордер залишився з попереднього прогону —
  скасовується до початку тесту.
"""

from playwright.sync_api import expect

from pages.trading_page import TradingPage

POSITION_TIMEOUT_MS = 20_000
POSITION_SIZE_USDC = "200"

# Ціна Limit Long — нижче поточної ринкової ($64,000+), щоб ордер
# НЕ виконався одразу, а залишився у списку Orders для тестування.
LIMIT_LONG_PRICE = "50000"

# Ціна Limit Short — вище поточної ринкової, з тих самих міркувань.
LIMIT_SHORT_PRICE = "80000"


def _ensure_no_orders(page: TradingPage) -> None:
    """Гарантувати порожній стан Orders. Скасувати залишений ордер якщо є."""
    page.orders_tab.click()
    if not page.no_orders_text.is_visible():
        page.cancel_first_order()
    expect(page.no_orders_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_create_limit_long_order_appears_in_orders(
    authenticated_trading_page: TradingPage,
):
    """
    Створення Limit Long ордера: ордер з'являється у списку Orders.

    Сценарій:
    1. Pre-condition: ордерів немає.
    2. Створюємо Limit Long на $50000 (нижче ринку).
    3. Перевіряємо: "No open orders" зник.
    4. Cleanup у finally: скасувати ордер.
    """
    page = authenticated_trading_page
    page.open()
    _ensure_no_orders(page)

    try:
        page.create_limit_long_order(price=LIMIT_LONG_PRICE, size=POSITION_SIZE_USDC)
        page.orders_tab.click()
        expect(page.no_orders_text).not_to_be_visible(timeout=POSITION_TIMEOUT_MS)
    finally:
        page.cancel_first_order()


def test_create_limit_short_order_appears_in_orders(
    authenticated_trading_page: TradingPage,
):
    """
    Створення Limit Short ордера: ордер з'являється у списку Orders.

    Сценарій:
    1. Pre-condition: ордерів немає.
    2. Створюємо Limit Short на $80000 (вище ринку).
    3. Перевіряємо: "No open orders" зник.
    4. Cleanup у finally: скасувати ордер.
    """
    page = authenticated_trading_page
    page.open()
    _ensure_no_orders(page)

    try:
        page.create_limit_short_order(price=LIMIT_SHORT_PRICE, size=POSITION_SIZE_USDC)
        page.orders_tab.click()
        expect(page.no_orders_text).not_to_be_visible(timeout=POSITION_TIMEOUT_MS)
    finally:
        page.cancel_first_order()


def test_cancel_limit_long_order_removes_it(
    authenticated_trading_page: TradingPage,
):
    """
    Скасування Limit Long ордера: після cancel ордер зникає зі списку.

    Сценарій:
    1. Pre-condition: ордерів немає.
    2. Створюємо Limit Long на $50000.
    3. Скасовуємо через UI (× → confirm modal → Cancel order).
    4. Перевіряємо: "No open orders" знов видно.

    Cleanup не потрібен — тест сам закриває ордер як основну дію.
    """
    page = authenticated_trading_page
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


def test_limit_long_with_zero_price_shows_notional_error(
    authenticated_trading_page: TradingPage,
):
    """
    Створення Limit Long з Price = 0 показує помилку про мінімум notional.

    Платформа НЕ валідує ціну = 0 явно як "invalid price". Натомість
    трактує це як порушення мінімуму notional (бо 0 × Size = 0 USDC).
    Очікуємо toast "Order notional below minimum".

    ВАЖЛИВО: повідомлення помилки не зовсім точне з UX-погляду —
    у звіті для FE команди варто запропонувати окреме повідомлення
    для ціни = 0 (наприклад, "Price must be greater than 0").
    """
    page = authenticated_trading_page
    page.open()
    _ensure_no_orders(page)

    # Дія: Limit Long з ціною = 0 і Size = $200
    page.select_limit_order_type()
    page.select_long()
    page.price_input.fill("0")
    page.size_input_limit.fill(POSITION_SIZE_USDC)
    page.buy_long_button.click()

    # Перевірка: з'явився toast про notional below minimum
    expect(page.order_notional_below_minimum_toast).to_be_visible(timeout=10_000)

    # Перевірка: ордер НЕ створено
    page.orders_tab.click()
    expect(page.no_orders_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_limit_long_above_market_price_fills_immediately(
    authenticated_trading_page: TradingPage,
):
    """
    Limit Long з ціною ВИЩЕ ринку виконується одразу як Market.

    Логіка: Limit Long означає "купити за ціною X або кращою (нижчою)".
    Якщо X = $70000 при ринку $63000, умова вже задоволена — платформа
    виконує ордер миттєво за ринковою ціною.

    Сценарій:
    1. Pre-condition: позицій 0, ордерів 0.
    2. Створити Limit Long з ціною $70000 (вище ринку).
    3. Перевірити:
       - з'явилась позиція (Positions (1)),
       - ордер НЕ залишився в Orders (No open orders).
    4. Cleanup: закрити позицію.

    ВАЖЛИВО: entry price у позиції буде РИНКОВИЙ, не $70000. Платформа
    виконує за best available price, не за лімітом — це expected behavior.
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: чистий стан. Якщо залишилась позиція з попереднього
    # прогону — закриваємо її, аналогічно _ensure_no_orders для ордерів.
    if not page.no_positions_text.is_visible():
        page.close_position()
    expect(page.no_positions_text).to_be_visible()
    _ensure_no_orders(page)

    try:
        # Дія: Limit Long з ціною ВИЩЕ ринку — має виконатись одразу
        page.create_limit_long_order(price="70000", size=POSITION_SIZE_USDC)

        # Перевірка №1: з'явилась позиція
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Перевірка №2: ордер НЕ залишився в Orders
        page.orders_tab.click()
        expect(page.no_orders_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Перемикаємось назад на Positions для cleanup
        page.positions_tab_with_one.click()
    finally:
        # Якщо позиція встигла закритись автоматично (наприклад через попередній
        # cleanup), пропускаємо повторне закриття. Чекаємо до 3с щоб UI стабілізувався.
        try:
            expect(page.no_positions_text).to_be_visible(timeout=3_000)
        except AssertionError:
            page.close_position()
