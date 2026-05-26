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
    page.open_long_position("100")

    # Перевірка появи позиції
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    # Дія 2: закрити позицію через UI-кнопку
    page.close_position()

    # Cleanup-перевірка через два незалежні індикатори
    expect(page.no_positions_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    expect(page.positions_tab_generic).to_have_text(
        "Positions (0)", timeout=POSITION_TIMEOUT_MS
    )