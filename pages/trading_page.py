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

        # Поле розміру позиції (TODO: ask FE team for data-testid)
        #.first використовуємо, бо placeholder="0" може бути на кількох полях
        self.size_input: Locator = page.get_by_placeholder("0").first

        # Динамічний розрахунок BTC еквіваленту, формат "~0 BTC", "~0.00128 BTC"
        self.size_btc_equivalent: Locator = page.get_by_text(
            re.compile(r"^~[\d.]+\s+BTC$")
        )

        # Авторизований стан
        # Баланс у header, формат "$0.00", "$1,234.56", тощо
        self.header_balance: Locator = page.get_by_text(re.compile(r"^\$[\d,]+\.\d{2}$"))

        # Action button (змінюється залежно від Long/Short селектора)
        self.buy_long_button: Locator = page.get_by_role("button", name="Buy / Long")
        self.sell_short_button: Locator = page.get_by_role("button", name="Sell / Short")

        # Перемикач напрямку угоди (Long/Short селектор)
        self.long_tab: Locator = page.get_by_role("button", name="Long", exact=True)
        self.short_tab: Locator = page.get_by_role("button", name="Short", exact=True)

        # Фінансові операції
        self.deposit_button: Locator = page.get_by_role("button", name="Deposit")
        self.withdraw_button: Locator = page.get_by_role("button", name="Withdraw")

        # Total equity у нижній панелі
        self.total_equity_value: Locator = page.get_by_text( 
            re.compile(r"^[\d,]+\.\d{2}\s+USDC$")
        ).first
        
        # Leverage селектор і модалка
        self.leverage_button: Locator = page.get_by_role("button", name="50x")
        self.leverage_modal_heading: Locator = page.get_by_text("Adjust BTCUSDC Leverage")
        self.leverage_modal_close: Locator = page.get_by_role("button", name="Close")
        self.leverage_modal_confirm: Locator = page.get_by_role("button", name="Confirm")

        # Значення leverage всередині модалки, формат "x50", "x49", "x100"
        # TODO: replace with data-testid when FE adds them
        # Локалізуємо через текст "x50" як якір — від нього беремо сусідні кнопки
        # Значення leverage у модалці — це <div>, тоді як на бейджі пари це <span>
        # TODO: replace with data-testid when FE adds them
        self.leverage_modal_value: Locator = page.locator("div").filter(
        has_text=re.compile(r"^x\d+$")
        ).first
        # Кнопки керування у модалці leverage
        self.leverage_modal_decrease: Locator = (
        self.leverage_modal_value.locator("..").locator("button").first
        )
        self.leverage_modal_increase: Locator = (
        self.leverage_modal_value.locator("..").locator("button").last
        )


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
        
        
    def select_long(self) -> None:
        """Перемкнути напрямок угоди на Long."""
        self.long_tab.click()


    def select_short(self) -> None:
        """Перемкнути напрямок угоди на Short."""
        self.short_tab.click()


    def open_leverage_modal(self) -> None:
        """Відкрити модалку зміни leverage."""
        self.leverage_button.click()


    def close_leverage_modal(self) -> None:
        """Закрити модалку leverage без збереження змін."""
        self.leverage_modal_close.click()


    def decrease_leverage(self) -> None:
        """Зменшити leverage на 1 (натискання мінус-кнопки у модалці)."""
        self.leverage_modal_decrease.click()

    def increase_leverage(self) -> None:
        """Збільшити leverage на 1 (натискання плюс-кнопки у модалці)."""
        self.leverage_modal_increase.click()