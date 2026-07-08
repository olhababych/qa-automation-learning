import datetime
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Page, Browser, BrowserContext
from pages.trading_page import TradingPage
from pages.sol_trading_page import SolTradingPage


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
SAFE_DOMAINS = ["d23u65c82prt0b.amplifyapp.com"]


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

    # Детектор серверних помилок платформи: логує відповіді API зі статусом
    # 500+. Дозволяє відрізнити падіння через INTERNAL_ERROR бекенду dev від
    # реального дефекту в тесті — при падінні у виводі видно [SERVER 5xx] URL.
    def _log_server_error(response):
        if response.status >= 500:
            print(f"\n[SERVER {response.status}] {response.url}")

    page.on("response", _log_server_error)
    yield page
    page.close()


@pytest.fixture
def authenticated_trading_page(authenticated_page: Page) -> Generator[TradingPage, None, None]:
    """TradingPage з авторизованою сесією — для тестів торгівлі."""
    tp = TradingPage(authenticated_page)
    yield tp
    # Teardown: закрити все, що лишилось, щоб не текло в наступний тест
    try:
        tp.cleanup_all()
    except Exception:
        pass


@pytest.fixture
def sol_trading_page(page: Page) -> SolTradingPage:
    """Фікстура для SOL/USDC тестів без авторизації (guest state)."""
    return SolTradingPage(page)


@pytest.fixture
def authenticated_sol_trading_page(authenticated_page: Page) -> Generator[SolTradingPage, None, None]:
    """SolTradingPage з авторизованою сесією — для тестів торгівлі на SOL/USDC."""
    tp = SolTradingPage(authenticated_page)
    yield tp
    try:
        tp.cleanup_all()
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────
# Hooks для покращення HTML-репорту
# ──────────────────────────────────────────────────────────────────────────

SCREENSHOTS_DIR = Path(__file__).parent.parent / "reports" / "screenshots"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """При failure тесту — зробити скріншот і прикріпити його до HTML-репорту.

    Скріншоти зберігаються у reports/screenshots/<test_name>.png та посилання
    додається до HTML-звіту як <img> поряд з повідомленням про помилку.
    """
    outcome = yield
    report = outcome.get_result()

    # Робимо скріншот тільки при failure у фазі call (сам тест), не у setup/teardown
    if report.when == "call" and report.failed:
        # Шукаємо сторінку Playwright серед fixture'ів тесту
        page = None
        for fixture_name in ("authenticated_page", "page"):
            if fixture_name in item.funcargs:
                page = item.funcargs[fixture_name]
                break
            # TradingPage / SolTradingPage загорнуті — дістаємо .page
            for tp_name in ("authenticated_trading_page", "trading_page",
                          "authenticated_sol_trading_page", "sol_trading_page"):
                if tp_name in item.funcargs:
                    page = item.funcargs[tp_name].page
                    break
            if page:
                break

        if page:
            try:
                SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
                safe_name = item.nodeid.replace("/", "_").replace("::", "_").replace("[", "_").replace("]", "")
                screenshot_path = SCREENSHOTS_DIR / f"{safe_name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)

                # Прикріпити до pytest-html звіту як base64-embedded image.
                # Це дозволяє ділитися self-contained HTML (Netlify, email)
                # без окремої папки screenshots/.
                extra = getattr(report, "extra", [])
                try:
                    import base64
                    from pytest_html import extras
                    with open(screenshot_path, "rb") as img_f:
                        encoded = base64.b64encode(img_f.read()).decode("utf-8")
                    extra.append(extras.image(f"data:image/png;base64,{encoded}"))
                    report.extra = extra
                except ImportError:
                    pass
            except Exception as e:
                print(f"[screenshot] Failed to capture: {e}")


def pytest_html_report_title(report):
    """Заголовок HTML-репорту."""
    report.title = "TruefFinance QA Automation Report"


def pytest_configure(config):
    """Додає метадані у HTML-репорт (домен, час, ОС)."""
    metadata = getattr(config, "_metadata", None)
    if metadata is not None:
        metadata["Platform Domain"] = TradingPage.URL
        metadata["Run Started"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata["Test Suite"] = "End-to-End UI Tests"
