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
import pytest
from playwright.sync_api import expect
from pages.trading_page import TradingPage


# Затримка появи/закриття позиції в UI — спостерігалось до 5 секунд.
# Беремо 10 секунд для запасу на повільну мережу.
# Timeout для дій, що залежать від бекенду (відкриття/закриття позицій,
# отримання position state). Dev-платформа іноді повільна, тому
# беремо запас — 20 секунд замість дефолтних 10.
POSITION_TIMEOUT_MS = 20_000

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


def test_close_position_modal_cancel_keeps_position_open(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо, що Cancel у модалці підтвердження закриття залишає позицію
    відкритою.

    Це окрема перевірка від test_close_position_via_ui_button: там ми
    тестуємо, що Confirm у модалці реально закриває позицію. Тут — що
    Cancel НЕ закриває (тобто модалка — функціональна, а не декоративна).

    Сценарій:
    1. Стартовий стан — позицій немає.
    2. Відкриваємо Long на POSITION_SIZE_USDC.
    3. Клікаємо "Close position" біля позиції → модалка з'являється.
    4. Перевіряємо, що в модалці видно: заголовок, кнопка Cancel, кнопка
       Close position (confirm).
    5. Клікаємо Cancel → модалка зникає, позиція залишається.
    6. Cleanup у finally: закриваємо позицію (на цей раз через Confirm).

    Захист цього тесту: якщо платформа повернеться до instant-close без
    модалки, тест впаде на кроці 4 — і ми одразу побачимо, що поведінка
    змінилась.
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий
    expect(page.no_positions_text).to_be_visible()

    try:
        # Підготовка: відкрити Long, на якому будемо тестувати модалку
        page.open_long_position(POSITION_SIZE_USDC)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Дія: клік на маленьку кнопку Close position біля позиції
        page.close_position_button.click()

        # Перевірка №1: модалка з'явилась з усіма очікуваними елементами
        expect(page.close_position_modal_heading).to_be_visible(timeout=5_000)
        expect(page.close_position_modal_cancel).to_be_visible()
        expect(page.close_position_modal_confirm).to_be_visible()

        # Дія: клік Cancel → модалка має зникнути
        page.close_position_modal_cancel.click()

        # Перевірка №2: модалка зникла
        expect(page.close_position_modal_heading).not_to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )

        # Перевірка №3: позиція досі відкрита (Cancel НЕ закрив її)
        expect(page.positions_tab_with_one).to_be_visible()
    finally:
        # Teardown: закриваємо позицію по-справжньому
        page.close_position() 


def test_open_long_position_with_min_leverage(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо коректну роботу платформи на мінімальному leverage (1x).

    Edge case: leverage 1x — це край діапазону (max_leverage=50 за конфігом
    ринку, min не зафіксовано). При 1x margin = notional, тобто весь
    введений Size фактично "заморожується" як забезпечення.

    Сценарій:
    1. Pre-condition: позицій немає, leverage 50x (default).
    2. Встановлюємо leverage = 1.
    3. Відкриваємо Long на POSITION_SIZE_USDC.
    4. Перевіряємо універсальну формулу: margin / Size ≈ 1/leverage (±10%).
       Для leverage 1x: margin ≈ Size (тобто margin / 200 ≈ 1.0).
    5. Cleanup у finally:
       - закрити позицію
       - повернути leverage на 50x (default для інших тестів)

    Запас ±10% покриває:
    - округлення BTC equivalent (FE bug — round-half-up на BTC)
    - природну зміну ціни BTC між кліками
    - комісії
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий
    expect(page.no_positions_text).to_be_visible()

    try:
        # Підготовка: встановити leverage = 1
        page.set_leverage(1)

        # Дія: відкрити Long на тестову суму при 1x leverage
        page.open_long_position(POSITION_SIZE_USDC)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Читаємо margin відкритої позиції
        margin = page.get_long_position_margin()

        # Перевірка універсальної формули: margin / Size ≈ 1 / leverage
        # Для 1x → ratio = 1.0
        size_usdc = float(POSITION_SIZE_USDC)
        expected_ratio = 1.0 / 1  # leverage = 1
        actual_ratio = margin / size_usdc
        tolerance = expected_ratio * 0.1  # ±10%

        assert abs(actual_ratio - expected_ratio) <= tolerance, (
            f"Margin/Size ratio at leverage 1x is {actual_ratio:.3f}, "
            f"expected {expected_ratio:.3f} ±{tolerance:.3f}. "
            f"Margin: ${margin}, Size: ${size_usdc}. "
            f"Difference: {abs(actual_ratio - expected_ratio):.3f}."
        )
    finally:
        # Teardown: тільки close_position. Leverage НЕ повертаємо на 50:
        # платформа сама скидає leverage на 50x при перезавантаженні сторінки
        # (page.open() на старті кожного тесту робить це автоматично).
        page.close_position()


def test_open_long_position_with_mid_leverage(
    authenticated_trading_page: TradingPage,
):
    """
    Sanity check: перевіряємо коректну роботу платформи на проміжному
    leverage (20x).

    Edge case типу "посередині діапазону" — не крайній мінімум (1x — тест A)
    і не дефолтний максимум (50x — який вже опосередковано покритий іншими
    тестами позицій). Цей тест ловить теоретичні баги, коли FE хардкодить
    обчислення тільки для крайніх значень.

    При leverage 20x: margin = notional / 20. Для Size $200 → margin ≈ $10.

    Сценарій:
    1. Pre-condition: позицій немає, leverage 50x (default).
    2. Встановлюємо leverage = 20.
    3. Відкриваємо Long на POSITION_SIZE_USDC.
    4. Перевіряємо універсальну формулу: margin / Size ≈ 1/leverage (±10%).
       Для leverage 20x: ratio = 0.05.
    5. Cleanup у finally:
       - закрити позицію
       - повернути leverage на 50x (default для інших тестів)

    Запас ±10% покриває округлення BTC equivalent, природну зміну ціни BTC
    між кліками, і комісії.
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий
    expect(page.no_positions_text).to_be_visible()

    try:
        # Підготовка: встановити leverage = 20
        page.set_leverage(20)

        # Дія: відкрити Long на тестову суму при 20x leverage
        page.open_long_position(POSITION_SIZE_USDC)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Читаємо margin відкритої позиції
        margin = page.get_long_position_margin()

        # Перевірка універсальної формули: margin / Size ≈ 1 / leverage
        # Для 20x → ratio = 0.05
        size_usdc = float(POSITION_SIZE_USDC)
        expected_ratio = 1.0 / 20  # leverage = 20
        actual_ratio = margin / size_usdc
        tolerance = expected_ratio * 0.1  # ±10%

        assert abs(actual_ratio - expected_ratio) <= tolerance, (
            f"Margin/Size ratio at leverage 20x is {actual_ratio:.4f}, "
            f"expected {expected_ratio:.4f} ±{tolerance:.4f}. "
            f"Margin: ${margin}, Size: ${size_usdc}. "
            f"Difference: {abs(actual_ratio - expected_ratio):.4f}."
        )
    finally:
        # Teardown: тільки close_position. Leverage НЕ повертаємо на 50:
        # платформа сама скидає leverage на 50x при перезавантаженні сторінки
        # (page.open() на старті кожного тесту робить це автоматично).
        page.close_position() 


@pytest.mark.xfail(
    reason=(
        "Bug платформи: при відкритті позиції в автотесті leverage у "
        "таблиці позицій не відповідає тосту 'Lev 50×' — позиція "
        "відкривається з leverage 10 замість 50. Margin не рекалькулюється "
        "при зміні leverage. Чекаємо фіксу від FE команди."
    ),
    strict=False,
)
@pytest.mark.xfail(
    reason=(
        "Bug платформи: позиція в автотесті відкривається з leverage 10 "
        "замість 50, хоча toast підтверджує 'Lev 50×'. Margin не "
        "рекалькулюється при зміні leverage. Bug зафіксовано у Jira."
    ),
    strict=False,
)

    
def test_changing_leverage_recalculates_margin_on_open_position(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо, що зміна leverage на ВІДКРИТІЙ позиції рекалькулює margin
    на платформі, при цьому розмір позиції (Size у BTC) залишається тим самим.

    Це ключова фіча margin trading: користувач може динамічно змінювати
    leverage без закриття позиції. Платформа має:
    - перерахувати margin за формулою: margin_new = margin_old × (lev_old / lev_new)
    - зберегти Size BTC незмінним (це фіксована кількість токенів)

    Сценарій:
    1. Pre-condition: позицій немає, leverage 50x (default).
    2. Відкриваємо Long $200 при leverage 50 → margin ≈ $4.
    3. Читаємо margin_before і size_before.
    4. Змінюємо leverage з 50 на 10 (зменшуємо в 5 разів).
    5. Чекаємо оновлення margin у UI.
    6. Перевіряємо:
       - margin виріс приблизно в 5 разів (margin × old_lev / new_lev),
       - Size BTC не змінився.
    7. Cleanup у finally: закрити позицію.

    Запас ±10% на margin покриває природну зміну ціни BTC між кліками
    (зміна leverage займає кілька секунд, BTC ціна змінюється).
    """
    page = authenticated_trading_page
    page.open()

    # Pre-condition: стартовий стан чистий
    expect(page.no_positions_text).to_be_visible()

    try:
        # Дія 1: відкрити Long $200 при дефолтному leverage 50
        page.open_long_position(POSITION_SIZE_USDC)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Читаємо стартовий стан позиції
        margin_before = page.get_long_position_margin()
        size_before = page.get_long_position_size()
        leverage_before = 50
        leverage_after = 10

        # Дія 2: змінити leverage на відкритій позиції з 50 на 10
        page.set_leverage(leverage_after)

        # Чекаємо, поки UI оновить margin (платформа рекалькулює асинхронно).
        # Без очікування читання margin одразу після set_leverage може повернути
        # старе значення, бо рядок таблиці ще не перерендерився.
        margin_after = page.wait_for_long_position_margin_change(
            from_value=margin_before
        )
        size_after = page.get_long_position_size()

        # Перевірка №1: margin рекалькулювався згідно формули
        # margin_new = margin_old × (leverage_old / leverage_new)
        expected_margin = margin_before * (leverage_before / leverage_after)
        tolerance = expected_margin * 0.1  # ±10% на зміну ціни BTC
        assert abs(margin_after - expected_margin) <= tolerance, (
            f"Margin after leverage change ({margin_after}) is not within ±10% "
            f"of expected ({expected_margin:.2f}). "
            f"Before: margin={margin_before}, leverage={leverage_before}. "
            f"After: leverage={leverage_after}. "
            f"Difference: {abs(margin_after - expected_margin):.2f}, "
            f"tolerance: ±{tolerance:.2f}."
        )

        # Перевірка №2: розмір позиції (Size BTC) не змінився
        # Це фіксована кількість токенів, leverage на неї не впливає.
        assert size_before == size_after, (
            f"Position size changed after leverage update: "
            f"before={size_before} BTC, after={size_after} BTC. "
            f"Size має залишатися незмінним при зміні leverage."
        )
    finally:
        # Teardown: закрити позицію.
        # Leverage НЕ повертаємо на 50: page.open() на старті наступного тесту
        # робить reload, який скидає leverage на 50x автоматично.
        page.close_position()


def test_open_short_position_creates_position(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо, що відкриття Short-позиції створює запис у таблиці позицій.

    Аналог test_open_long_position_creates_position, але для протилежного
    напрямку. Тестує симетрію базового флоу Long/Short.

    Сценарій:
    1. Pre-condition: позицій немає.
    2. Відкриваємо Short $200.
    3. Перевіряємо появу позиції через два індикатори:
       - вкладка змінилась на "Positions (1)"
       - текст "No open positions" зник
    4. Cleanup у finally: закрити позицію.
    """
    page = authenticated_trading_page
    page.open()
    expect(page.no_positions_text).to_be_visible()

    try:
        page.open_short_position("200")
        expect(page.positions_tab_with_one).to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )
        expect(page.no_positions_text).not_to_be_visible(
            timeout=POSITION_TIMEOUT_MS
        )
    finally:
        page.close_position()


def test_short_larger_than_long_flips_position_direction(
    authenticated_trading_page: TradingPage,
):
    """
    Перевіряємо netting flip: відкриття Short БІЛЬШОГО розміру за існуючу
    Long-позицію перевертає її у Short.

    Сценарій:
    1. Pre-condition: позицій немає.
    2. Відкриваємо Long $200 (margin ≈ $4).
    3. Відкриваємо Short $400 (вдвічі більше).
    4. Netting: Long закривається ПОВНІСТЮ, залишається Short $200.
    5. Перевіряємо:
       - позиція все ще існує (Positions (1)),
       - напрямок змінився з Long на Short.

    Цей тест доповнює test_open_short_reduces_long_position (Short меншого
    розміру) і test_opposite_position_with_same_size_closes_position
    (Short того ж розміру). Тут перевіряємо граничний кейс реверсу напрямку.

    ВАЖЛИВО: без Reduce Only платформа дозволяє реверс — це нормальна
    netting-логіка. З Reduce Only такий Short був би відхилений
    (це покрито test_reduce_only_blocks_position_increase).
    """
    page = authenticated_trading_page
    page.open()
    expect(page.no_positions_text).to_be_visible()

    try:
        # Дія 1: відкрити Long $200
        page.open_long_position(POSITION_SIZE_USDC)
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Дія 2: відкрити Short $400 — перевертає позицію
        page.open_short_position(str(int(POSITION_SIZE_USDC) * 2))

        # Перевірка №1: позиція все ще існує (Positions (1))
        expect(page.positions_tab_with_one).to_be_visible(timeout=POSITION_TIMEOUT_MS)

        # Перевірка №2: напрямок став Short
        # Чекаємо появи Short-індикатора (зникнення Long-індикатора зайве,
        # бо у DOM може на мить бути обидва під час netting).
        short_indicator = page.page.get_by_role("img", name="short")
        expect(short_indicator).to_be_visible(timeout=POSITION_TIMEOUT_MS)
    finally:
        page.close_position()
