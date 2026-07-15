import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.btc]
"""
Тести модалки вибору режиму маржі (Cross / Isolated).
Isolated поки в розробці — тестуємо лише наявність і базову поведінку
модалки, без реального перемикання на Isolated.
"""
from playwright.sync_api import expect
from pages.trading_page import TradingPage

TIMEOUT_MS = 10_000


def test_margin_mode_modal_opens_with_both_options(
    authenticated_trading_page: TradingPage,
):
    """Клік на Cross відкриває модалку margin mode з опціями Cross та Isolated."""
    page = authenticated_trading_page
    page.open()

    page.margin_mode_button.click()
    expect(page.margin_mode_heading).to_be_visible(timeout=TIMEOUT_MS)
    expect(page.margin_mode_cross_option).to_be_visible(timeout=TIMEOUT_MS)
    expect(page.margin_mode_isolated_option).to_be_visible(timeout=TIMEOUT_MS)


def test_margin_mode_modal_closes(
    authenticated_trading_page: TradingPage,
):
    """Модалка margin mode закривається через Close."""
    page = authenticated_trading_page
    page.open()

    page.margin_mode_button.click()
    expect(page.margin_mode_heading).to_be_visible(timeout=TIMEOUT_MS)

    page.margin_mode_close.click()
    expect(page.margin_mode_heading).to_be_hidden(timeout=TIMEOUT_MS)


def test_switch_cross_to_isolated_on_clean_account(
    authenticated_trading_page: TradingPage,
):
    """На чистому акаунті перемикання Cross -> Isolated успішне:
    показує тост оновлення, кнопка режиму стає Isolated.
    Cleanup: повертаємо Cross, щоб не лишати акаунт в Isolated.
    """
    page = authenticated_trading_page
    page.open()
    # Pre-condition: акаунт чистий (без позицій/ордерів) — інакше 409
    expect(page.no_positions_text).to_be_visible(timeout=TIMEOUT_MS)

    try:
        page.switch_margin_mode_to_isolated()
        expect(page.margin_mode_updated_toast).to_be_visible(timeout=TIMEOUT_MS)
        expect(page.margin_mode_button_isolated).to_be_visible(timeout=TIMEOUT_MS)
    finally:
        # Повертаємо Cross, щоб інші тести стартували з дефолтного режиму
        try:
            page.switch_margin_mode_to_cross()
            expect(page.margin_mode_button).to_be_visible(timeout=TIMEOUT_MS)
        except Exception:
            pass


def test_switch_margin_mode_blocked_with_open_position(
    authenticated_trading_page: TradingPage,
):
    """Критичний edge-case (409): при відкритій позиції перемикання на
    Isolated блокується — показує помилку, режим лишається Cross.
    """
    page = authenticated_trading_page
    page.open()
    # Прибрати можливі залишки від попередніх прогонів перед pre-condition
    page.cleanup_all()
    expect(page.no_positions_text).to_be_visible(timeout=TIMEOUT_MS)

    try:
        page.open_long_position("200")
        expect(page.positions_tab_with_one).to_be_visible(timeout=20_000)

        # Спроба перемкнути на Isolated при відкритій позиції
        page.switch_margin_mode_to_isolated()

        # Блокування: режим НЕ перемкнувся. Модалка лишається відкрита,
        # кнопка Isolated не з'явилась. Тост ефемерний — не головний асерт.
        expect(page.margin_mode_heading).to_be_visible(timeout=TIMEOUT_MS)
        expect(page.margin_mode_button_isolated).to_be_hidden(timeout=TIMEOUT_MS)
    finally:
        # Спершу гарантовано закрити модалку й дочекатись зникнення heading,
        # інакше вона перекриває вкладки і cleanup не закриє позицію.
        try:
            if page.margin_mode_heading.is_visible():
                page.margin_mode_close.click(timeout=5_000)
                expect(page.margin_mode_heading).to_be_hidden(timeout=10_000)
        except Exception:
            pass
        page.cleanup_all()
