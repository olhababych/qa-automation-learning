from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Page, Browser, BrowserContext
from pages.trading_page import TradingPage


AUTH_STATE_FILE = Path(__file__).parent.parent / "auth_state.json"

# Production safety guard — захист від випадкового запуску тестів проти
# середовищ з не-testnet балансами. Whitelist підхід: тільки явно відомі
# безпечні домени дозволені. Якщо TradingPage.URL не містить жодного з
# них — pytest зупиняється до виконання жодного тесту.
#
# Чому це критично: тести позицій відкривають реальні Long/Short ордери.
# На dev це testnet USDC. На beta або prod це може бути зовсім інша мережа
# зі справжніми коштами або непередбачуваними наслідками.
#
# Додавати домени сюди тільки після свідомої перевірки, що там testnet.
SAFE_DOMAINS = ["dex-dev.true.trading"]


def pytest_collection_modifyitems(config, items):
    """Production safety guard: блокуємо запуск, якщо URL не у whitelist."""
    current_url = TradingPage.URL
    if not any(domain in current_url for domain in SAFE_DOMAINS):
        pytest.exit(
            f"\n\n[PRODUCTION SAFETY GUARD]\n"
            f"TradingPage.URL не містить жодного з safe-доменів.\n"
            f"Поточна URL: {current_url}\n"
            f"Дозволені домени: {SAFE_DOMAINS}\n\n"
            f"Тести позицій відкривають реальні ордери. Запуск проти не-dev\n"
            f"середовища може зачепити справжні баланси.\n"
            f"Якщо це свідомий запуск — додайте домен до SAFE_DOMAINS у conftest.py.\n",
            returncode=1,
        )

@pytest.fixture
def trading_page(page: Page) -> TradingPage:
    """Фікстура для тестів без авторизації (guest state)."""
    return TradingPage(page)


@pytest.fixture
def authenticated_context(browser: Browser) -> Generator[BrowserContext, None, None]:
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
def authenticated_page(
    authenticated_context: BrowserContext,
) -> Generator[Page, None, None]:
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