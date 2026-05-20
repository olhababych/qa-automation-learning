import pytest
from playwright.sync_api import Page
from pages.trading_page import TradingPage


@pytest.fixture
def trading_page(page: Page) -> TradingPage:
    """Фікстура, що повертає готовий TradingPage."""
    return TradingPage(page)