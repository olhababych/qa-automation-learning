from pathlib import Path

import pytest
from playwright.sync_api import Page, Browser, BrowserContext
from pages.trading_page import TradingPage


AUTH_STATE_FILE = Path(__file__).parent.parent / "auth_state.json"


@pytest.fixture
def trading_page(page: Page) -> TradingPage:
    """Фікстура для тестів без авторизації (guest state)."""
    return TradingPage(page)


@pytest.fixture
def authenticated_context(browser: Browser) -> BrowserContext:
    """
    Створює контекст браузера з завантаженою авторизованою сесією.
    Файл auth_state.json створюється скриптом save_auth_state.py.
    """
    if not AUTH_STATE_FILE.exists():
        pytest.skip(
            f"Auth state file not found at {AUTH_STATE_FILE}. "
            f"Run 'python save_auth_state.py' first."
        )
    context = browser.new_context(storage_state=str(AUTH_STATE_FILE))
    yield context
    context.close()


@pytest.fixture
def authenticated_page(authenticated_context: BrowserContext) -> Page:
    """
    Сторінка з авторизованою сесією.
    Використовуйте у тестах, які потребують залогіненого користувача.
    """
    page = authenticated_context.new_page()
    yield page
    page.close()


@pytest.fixture
def authenticated_trading_page(authenticated_page: Page) -> TradingPage:
    """TradingPage з авторизованою сесією — для тестів торгівлі."""
    return TradingPage(authenticated_page)