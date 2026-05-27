"""
Тести керування позиціями на платформі TrueFinance.

ВАЖЛИВО про netting-модель платформи:
- Long $100 + Long $100 → Long $200 (накопичення)
- Long $100 + Short $50 → Long $50 (часткове закриття)
- Long $100 + Short $100 → 0 позицій (повне закриття)

ВАЖЛИВО про cleanup:
- На момент написання cleanup-фікстури немає (свідоме рішення для MVP).
- Якщо тест падає посередині — закривайте позиції вручну на платформі
  перед наступним запуском.
"""
from playwright.sync_api import expect

from pages.trading_page import TradingPage


# Затримка появи/закриття позиції в UI — спостерігалось до 5 секунд.
# Беремо 10 секунд для запасу на повільну мережу.
POSITION_TIMEOUT_MS = 10_000

# Мінімальний робочий розмір позиції для тестів.
# Конфіг ринку: min_order_notional = $100, але FE робить round-half-up
# на BTC equivalent, через що ордери близько до $100 відхиляються бекендом
# (~50% випадків, детерміновано від поточної ціни BTC).
# Bug зафіксовано — до фіксу використовуємо $200 як стабільну суму.
POSITION_SIZE_USDC = "200"

def test_close_position_via_ui_button(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо, що кнопка Close position закриває відкриту позицію.

    Сценарій:
    1. Стартовий стан — позицій немає (Positions (0) + "No open positions").
    2. Відкриваємо Long $100.
    3. Чекаємо появи позиції (Positions (1)).
    4. Клікаємо Close position.
    5. Перевіряємо cleanup через два незалежні індикатори:
       - текст "No open positions"
       - лічильник Positions (0)

    Примітка про UX: на платформі НЕМАЄ confirmation модалки при Close —
    клік закриває позицію одразу. Це задокументовано як потенційний UX-баг.
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий.
    # Якщо assertion впаде тут — означає, що залишились незакриті позиції
    # з попередніх запусків. Треба закрити вручну на платформі.
    expect(page.no_positions_text).to_be_visible()

    # Дія 1: відкрити Long $100
    page.open_long_position("200")

    # Перевірка появи позиції
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    # Дія 2: закрити позицію через UI-кнопку
    page.close_position()

    # Cleanup-перевірка через два незалежні індикатори
    expect(page.no_positions_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.positions_tab_generic).to_have_text(
        "Positions (0)", timeout=POSITION_TIMEOUT_MS
    )


def test_open_long_position_creates_position(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо, що відкриття Long-позиції створює запис у таблиці позицій.

    Сценарій:
    1. Стартовий стан — позицій немає (текст "No open positions" видимий).
    2. Відкриваємо Long $100.
    3. Перевіряємо появу позиції через два незалежні індикатори:
       - вкладка змінилась на "Positions (1)"
       - текст "No open positions" зник з UI
    4. Cleanup: закриваємо створену позицію через try/finally,
       щоб не залишити стан для наступних тестів.

    Cleanup у finally гарантує закриття позиції навіть при failure
    assertions. Це окрема дія від assertion'ів — teardown, не верифікація.
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий.
    # Якщо assertion впаде тут — означає, що залишились незакриті позиції
    # з попередніх запусків. Треба закрити вручну на платформі.
    expect(page.no_positions_text).to_be_visible()

    try:
        # Дія: відкрити Long $100
        page.open_long_position("200")

        # Перевірка №1: лічильник позицій оновився
        expect(page.positions_tab_with_one).to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )

        # Перевірка №2: текст "No open positions" зник
        expect(page.no_positions_text).not_to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )
    finally:
        # Teardown: закриваємо позицію незалежно від результату assertion'ів.
        # Це гарантує, що тест не залишить стан для наступних запусків.
        page.close_position()