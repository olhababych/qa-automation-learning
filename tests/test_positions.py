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

       
def test_opposite_position_with_same_size_closes_position(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо netting-модель: відкриття протилежної позиції такого ж
    розміру закриває оригінальну, а не створює другу.

    Сценарій:
    1. Стартовий стан — позицій немає.
    2. Відкриваємо Long на POSITION_SIZE_USDC.
    3. Перевіряємо, що з'явилась позиція (Positions (1)).
    4. Відкриваємо Short на ту саму суму (POSITION_SIZE_USDC).
    5. Перевіряємо, що netting спрацював:
       - лічильник Positions (0)
       - текст "No open positions" знов видимий

    БЕЗ cleanup-фікстури: якщо netting спрацював, позиції вже немає
    і закривати нічого. Якщо тест впав на середині — закривайте позицію
    вручну на платформі перед наступним запуском.

    Це свідомий компроміс: спрощує тест ціною ризику "брудного" стану
    при failure. Виправдане, бо netting — це і є те, що ми тестуємо.
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий.
    expect(page.no_positions_text).to_be_visible()

    # Дія 1: відкрити Long на тестову суму
    page.open_long_position(POSITION_SIZE_USDC)

    # Sanity check: позиція з'явилась перед спробою netting
    expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

    # Дія 2: відкрити Short на ту саму суму — має спрацювати netting
    page.open_short_position(POSITION_SIZE_USDC)

    # Головна перевірка №1: лічильник повернувся на (0)
    expect(page.positions_tab_generic).to_have_text(
        "Positions (0)", timeout=POSITION_TIMEOUT_MS
    )

    # Головна перевірка №2: текст "No open positions" знов видимий
    expect(page.no_positions_text).to_be_visible(timeout=POSITION_TIMEOUT_MS)


def test_open_short_reduces_long_position(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо netting-модель: відкриття Short меншого розміру зменшує
    Long-позицію, але не закриває її повністю.

    Сценарій:
    1. Стартовий стан — позицій немає.
    2. Відкриваємо Long $200 → margin ≈ $4.00 (BTC ціна × 4).
    3. Відкриваємо Short $100 (половина від Long).
    4. Netting: залишається Long $100 → margin ≈ $2.00.
    5. Перевіряємо, що margin зменшився приблизно вдвічі (±10%).

    Запас ±10% покриває:
    - округлення BTC equivalent (FE bug — див. round-half-up bug report)
    - природну зміну ціни BTC між кліками (зазвичай < 1%)
    - комісії

    Cleanup у finally: після успішного netting залишається Long $100 —
    закриваємо її через close_position(). Якщо тест впав на середині
    (наприклад, перший Long не пройшов через FE bug), finally однаково
    спробує close_position — це безпечно, бо метод закриває першу видиму.
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий
    expect(page.no_positions_text).to_be_visible()

    try:
        # Дія 1: відкриваємо Long $200
        page.open_long_position(POSITION_SIZE_USDC)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Читаємо margin початкової Long-позиції
        margin_before = page.get_long_position_margin()

        # Дія 2: відкриваємо Short на половину розміру — спрацьовує netting
        page.open_short_position(str(int(POSITION_SIZE_USDC) // 2))

       # Sanity check: позиція все ще існує (Positions (1)),
        # netting НЕ закрив її повністю
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Читаємо margin після netting — чекаємо ЗМІНИ значення в UI,
        # бо одразу після кліку Sell/Short таблиця ще показує старий рядок.
        # Без очікування зміни тест читає margin_before (старе) знов і assertion
        # падає з "margin не змінився".
        margin_after = page.wait_for_long_position_margin_change(
            from_value=margin_before
        )

        # Головна перевірка: margin зменшився приблизно вдвічі
        expected_margin = margin_before / 2
        tolerance = expected_margin * 0.1  # ±10%
        assert abs(margin_after - expected_margin) <= tolerance, (
            f"Margin after Short netting ({margin_after}) is not within ±10% "
            f"of expected ({expected_margin:.2f}). "
            f"Margin before: {margin_before}. "
            f"Difference: {abs(margin_after - expected_margin):.2f}, "
            f"tolerance: ±{tolerance:.2f}."
        )
    finally:
        # Teardown: закриваємо залишок позиції
        page.close_position()