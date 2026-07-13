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
