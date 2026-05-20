import re
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class TradingPage(BasePage):
    """Page Object для сторінки торгівлі BTCUSDC."""

    URL = "https://platform-dev.dd8hy3vt93k5p.amplifyapp.com/trading/BTCUSDC"

    def __init__(self, page: Page):
        super().__init__(page)
        # Гостьовий стан
        self.sign_in_button: Locator = page.get_by_role("button", name="Sign In")
        self.trading_pair_button: Locator = page.get_by_role("button", name="BTC /USDC -")

        # Auth-модалка (Dynamic SDK)
        self.auth_modal_heading: Locator = page.get_by_test_id("dynamic-auth-modal-heading")
        self.auth_modal_close_button: Locator = page.get_by_test_id("close-button")

        # Вкладки нижньої панелі
        self.positions_tab: Locator = page.get_by_role("button", name="Positions (0)")
        self.orders_tab: Locator = page.get_by_role("button", name="Orders", exact=True)
        self.positions_history_tab: Locator = page.get_by_role("button", name="Positions history")
        self.order_history_tab: Locator = page.get_by_role("button", name="Order history")

        # Контент-маркери для кожної вкладки
        self.no_positions_text: Locator = page.get_by_text("No open positions")
        self.no_orders_text: Locator = page.get_by_text("No open orders")
        self.no_positions_history_text: Locator = page.get_by_text("No positions history")
        self.no_order_history_text: Locator = page.get_by_text("No order history")

        # Поле розміру позиції
        self.size_input: Locator = page.get_by_placeholder("0").first

        # Авторизований стан
        # Баланс у header, формат "$0.00", "$1,234.56", тощо
        self.header_balance: Locator = page.get_by_text(re.compile(r"^\$[\d,]+\.\d{2}$"))

    def open(self) -> None:
        """Відкрити сторінку торгівлі BTCUSDC."""
        super().open(self.URL)

    def click_sign_in(self) -> None:
        """Клікнути по Sign In для відкриття auth-модалки."""
        self.sign_in_button.click()

    def close_auth_modal(self) -> None:
        """Закрити auth-модалку через хрестик."""
        self.auth_modal_close_button.click()

    def fill_size(self, value: str) -> None:
        """Ввести значення в поле розміру позиції."""
        self.size_input.fill(value)