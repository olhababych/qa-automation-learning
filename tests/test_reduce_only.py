import pytest

pytestmark = [pytest.mark.reduce_only, pytest.mark.btc]

"""
Тести функціональності Reduce Only на BTCUSDC.

Reduce Only — це прапорець ордера, що обмежує його дію: ордер може ТІЛЬКИ
зменшувати або закривати існуючу позицію, але не може її збільшувати
чи відкривати нову. Якщо ордер з Reduce Only намагається збільшити позицію
(той самий напрямок) — платформа відхиляє його з тостом помилки.

ВАЖЛИВО про cleanup:
- Тести залишають відкриті позиції після першої дії, тому cleanup у finally
  обов'язковий — без нього наступний тест впаде на pre-condition.
- Якщо тест падає посередині — закривайте позиції вручну на платформі
  перед наступним запуском.
"""

from playwright.sync_api import expect

from pages.trading_page import TradingPage

# Затримка появи/закриття позиції в UI на повільному dev-бекенді.
POSITION_TIMEOUT_MS = 20_000

# Стандартний розмір для тестів — $200 USDC.
# Чому не $100: FE bug round-half-up на BTC equivalent відхиляє ордери
# близько мінімуму notional ($100). Bug зафіксовано — до фіксу беремо $200.
POSITION_SIZE_USDC = "200"


def test_reduce_only_blocks_position_increase(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо, що Reduce Only блокує спробу збільшити існуючу позицію.

    Сценарій:
    1. Pre-condition: позицій немає.
    2. Відкриваємо Long $200 (без Reduce Only).
    3. Намагаємось відкрити ще один Long $200 з УВІМКНЕНИМ Reduce Only.
    4. Перевіряємо:
       - з'являється тост "Reduce-only order cannot increase position size",
       - кількість позицій залишається 1 (нова не відкрилась),
       - margin позиції не змінився (позиція не збільшилась).
    5. Cleanup у finally: закрити позицію.

    Цей тест захищає ключову бізнес-логіку: користувач, що увімкнув
    Reduce Only для безпеки, не повинен випадково збільшити позицію.
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий
    expect(page.no_positions_text).to_be_visible()

    try:
        # Дія 1: відкриваємо Long $200 без Reduce Only
        page.open_long_position(POSITION_SIZE_USDC)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Фіксуємо margin до спроби збільшити — потім порівняємо
        margin_before = page.get_long_position_margin()

        # Дія 2: спроба відкрити ще один Long з Reduce Only
        page.select_long()
        page.enable_reduce_only()
        page.fill_size(POSITION_SIZE_USDC)
        page.buy_long_button.click()

        # Перевірка №1: з'явився тост помилки
        expect(page.reduce_only_error_toast).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Перевірка №2: кількість позицій не змінилась (досі 1)
        expect(page.positions_tab_with_one).to_be_visible()

        # Перевірка №3: margin позиції не змінився
        # (платформа не виконала ордер, тому розмір позиції тойсамий)
        margin_after = page.get_long_position_margin()
        assert margin_before == margin_after, (
            f"Margin changed after blocked Reduce Only order: "
            f"before={margin_before}, after={margin_after}. "
            f"Reduce Only мав ЗАБЛОКУВАТИ збільшення позиції."
        )
    finally:
        # Teardown: закриваємо позицію
        page.cleanup_all()  # cleanup_all: reduce-only лишає ордери, які close_position не скасовує


def test_reduce_only_does_not_flip_position_direction(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо, що Reduce Only + Short меншого розміру зменшує Long-позицію,
    але НЕ перевертає її в Short.

    Сценарій:
    1. Pre-condition: позицій немає.
    2. Відкриваємо Long $200.
    3. Відкриваємо Short $100 (половина) з УВІМКНЕНИМ Reduce Only.
    4. Перевіряємо:
       - позиція залишилась Long (img[alt='long'] видимий),
       - margin зменшився приблизно вдвічі.
    5. Cleanup у finally: закрити залишок Long.

    Без Reduce Only платформа теж зменшила б позицію через netting — але
    з Reduce Only ми отримуємо ДОДАТКОВУ гарантію: якщо Short помилково
    буде більший за Long, ордер відхилиться замість перевороту в Short.
    Цей тест перевіряє happy path: Reduce Only НЕ заважає коректному
    зменшенню позиції.
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий
    expect(page.no_positions_text).to_be_visible()

    try:
        # Дія 1: відкрити Long $200
        page.open_long_position(POSITION_SIZE_USDC)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        margin_before = page.get_long_position_margin()

        # Дія 2: відкрити Short $100 з Reduce Only (половина від Long)
        page.select_short()
        page.enable_reduce_only()
        page.fill_size(str(int(POSITION_SIZE_USDC) // 2))
        page.sell_short_button.click()

        # Перевірка №1: позиція все ще існує (Positions (1))
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Перевірка №2: позиція залишилась Long (не перевернулась у Short)
        long_indicator = page.page.get_by_role("img", name="long")
        expect(long_indicator).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Перевірка №3: margin зменшився приблизно вдвічі (±10%)
        margin_after = page.wait_for_long_position_margin_change(
            from_value=margin_before
        )
        expected_margin = margin_before / 2
        tolerance = expected_margin * 0.1
        assert abs(margin_after - expected_margin) <= tolerance, (
            f"Margin after Short with Reduce Only ({margin_after}) не входить у "
            f"±10% від очікуваного ({expected_margin:.2f}). "
            f"Margin до: {margin_before}, після: {margin_after}."
        )
    finally:
        # Teardown: закрити залишок Long
        page.cleanup_all()  # cleanup_all: reduce-only лишає ордери, які close_position не скасовує


def test_reduce_only_blocks_order_when_no_position_exists(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо, що Reduce Only ордер БЕЗ існуючої позиції відхиляється.

    Логіка платформи: без позиції розмір = 0; будь-який RO ордер його
    збільшить → блокується тостом "Reduce-only order cannot increase
    position size".

    Сценарій:
    1. Pre-condition: позицій немає (No open positions).
    2. Увімкнути Reduce Only.
    3. Спробувати Long $200.
    4. Перевірити: з'явився тост, позиція НЕ створена.

    Цей тест доповнює test_reduce_only_blocks_position_increase: там
    RO блокує ЗБІЛЬШЕННЯ існуючої позиції, тут — створення з нуля.
    """
    page = authenticated_trading_page
    page.open()
    expect(page.no_positions_text).to_be_visible()

    # Дія: Long $200 з увімкненим Reduce Only БЕЗ існуючої позиції
    page.select_long()
    page.enable_reduce_only()
    page.fill_size("200")
    page.buy_long_button.click()

    # Перевіряємо результат поведінки: reduce-only ордер без позиції
    # НЕ створює позицію. Раніше платформа показувала тост
    # "Reduce-only order cannot increase position size", але тепер
    # ордер тихо ігнорується без тосту (зміна поведінки платформи —
    # див. Jira). Перевірка результату (позиція не створена) надійніша
    # за очікування ефемерного тосту.
    expect(page.no_positions_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)
