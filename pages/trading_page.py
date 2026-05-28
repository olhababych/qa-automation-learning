import re
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class TradingPage(BasePage):
    """Page Object для сторінки торгівлі BTCUSDC."""

    URL = "https://dex-dev.true.trading/trading/BTCUSDC"

    def __init__(self, page: Page):
        super().__init__(page)
        # Гостьовий стан
        self.sign_in_button: Locator = page.get_by_role("button", name="Sign In")
        self.trading_pair_button: Locator = page.get_by_role("button", name=re.compile(r"^BTC \/USDC x\d+$"))
        
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
        # На новому домені у header'і з'явилось друге $X.XX число (ціна BTC) —
        # використовуємо .first як толерантний smoke-check на наявність будь-якого
        # балансоподібного числа в header'і у автентифікованому стані.
        self.header_balance: Locator = page.get_by_text(
            re.compile(r"^\$[\d,]+\.\d{2}$")
        ).first

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

        ## Position close — на новому домені dex-dev.true.trading з'явилась
        # confirmation модалка (на старому домені її не було). Закриття тепер
        # двоетапне: клік "Close position" біля позиції → модалка → confirm.
        # Маленька кнопка на самій позиції (відкриває модалку):
        self.close_position_button: Locator = page.get_by_role("button", name="Close position")

        # Заголовок модалки — використовуємо як якір "модалка з'явилась":
        self.close_position_modal_heading: Locator = page.get_by_text("Close position?")

        # Кнопка підтвердження в модалці — є дві кнопки з назвою "Close position",
        # тому розрізняємо її через локалізацію всередині модалки.
        # Використовуємо filter has_text на тексті модалки як sibling-якір.
        self.close_position_modal_confirm: Locator = page.locator(
            "button", has_text="Close position"
        ).last

        # Positions tab counter — динамічний, змінюється з 0 на 1, 2 і т.д.
        # positions_tab_with_one для перевірки появи позиції після Buy/Long
        # positions_tab_generic — універсальний, для перевірок через to_have_text
        self.positions_tab_with_one: Locator = page.get_by_role("button", name="Positions (1)")
        self.positions_tab_generic: Locator = page.locator("button").filter(
            has_text=re.compile(r"^Positions \(\d+\)$")
        )

        # Margin у таблиці позицій — 7-ма колонка (індекс 6) у grid-рядку.
        # Якір — img[alt='long' або 'short'] унікально визначає рядок позиції;
        # h-14 розрізняє рядок позиції від header'а (h-7).
        # Стійко до зміни ціни BTC (бо це live-значення), але крихко до зміни
        # порядку колонок у таблиці. TODO: ask FE team for data-testid.
        self.long_position_margin: Locator = (
            page.locator("img[alt='long']")
            .locator("xpath=ancestor::div[contains(@class, 'h-14')][1]")
            .locator("> div").nth(6)
        )
        self.short_position_margin: Locator = (
            page.locator("img[alt='short']")
            .locator("xpath=ancestor::div[contains(@class, 'h-14')][1]")
            .locator("> div").nth(6)
        )
        
        # Leverage селектор і модалка
        self.leverage_button: Locator = page.get_by_role("button", name="50x")
        self.leverage_modal_heading: Locator = page.get_by_text("Adjust BTCUSDC Leverage")
        self.leverage_modal_close: Locator = page.get_by_role("button", name="Close", exact=True)
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

        # Deposit модалка
        self.deposit_modal_subtitle: Locator = page.get_by_text(
        "Transfer money to your trading account"
        )
        self.deposit_modal_close: Locator = page.get_by_role("button", name="Close", exact=True)
        # Withdraw модалка
        self.withdraw_modal_subtitle: Locator = page.get_by_text(
        "Transfer money from your trading account"
        )
        self.withdraw_modal_close: Locator = page.get_by_role("button",name="Close", exact=True)


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


    def open_deposit_modal(self) -> None:
        """Відкрити модалку Deposit."""
        self.deposit_button.click()

    def close_deposit_modal(self) -> None:
        """Закрити модалку Deposit без транзакції."""
        self.deposit_modal_close.click()

    def open_withdraw_modal(self) -> None:
        """Відкрити модалку Withdraw."""
        self.withdraw_button.click()

    def close_withdraw_modal(self) -> None:
        """Закрити модалку Withdraw без транзакції."""
        self.withdraw_modal_close.click()
        

    def open_long_position(self, size: str) -> None:
        """Відкрити Long-позицію заданого розміру в USDC.

        Виконує повний флоу: вибір Long → введення розміру → очікування,
        поки UI розрахує BTC-еквівалент → клік Buy / Long.

        Очікування на BTC-еквівалент критичне: без нього Playwright клікає
        Buy/Long швидше, ніж React оновить state з введеним розміром,
        і платформа повертає "Order notional below minimum".

        Підтвердження транзакції не потрібне (email-логін через Dynamic SDK).
        Затримка появи позиції в UI — до 5 секунд.
        """
        self.select_long()
        self.fill_size(size)
        # Чекаємо, поки UI відобразить НЕ-нульовий BTC-еквівалент.
        # "~0 BTC" → платформа ще не врахувала розмір; "~0.0013 BTC" → готово.
        expect(self.size_btc_equivalent).to_have_text(
            re.compile(r"^~0\.\d+\s+BTC$"), timeout=5_000
        )
        self.buy_long_button.click()
        
        
    def open_short_position(self, size: str) -> None:
        """Відкрити Short-позицію заданого розміру в USDC.

        Виконує повний флоу: вибір Short → введення розміру → очікування,
        поки UI розрахує BTC-еквівалент → клік Sell / Short.
        При наявності Long-позиції спрацьовує netting-модель платформи.

        Очікування на BTC-еквівалент критичне: без нього Playwright клікає
        Sell/Short швидше, ніж React оновить state, і платформа повертає
        "Order notional below minimum".

        Затримка появи/зміни позиції в UI — до 5 секунд.
        """
        self.select_short()
        self.fill_size(size)
        # Чекаємо, поки UI відобразить НЕ-нульовий BTC-еквівалент.
        expect(self.size_btc_equivalent).to_have_text(
            re.compile(r"^~0\.\d+\s+BTC$"), timeout=5_000
        )
        self.sell_short_button.click()


    def close_position(self) -> None:
        """Закрити першу відкриту позицію через двоетапний UI-флоу.

        На новому домені dex-dev.true.trading з'явилась confirmation
        модалка: клік на "Close position" біля позиції відкриває модалку
        з підтвердженням, де треба клікнути другу "Close position".

        Метод чекає реального закриття на платформі перш ніж повернути
        керування — це критично для використання як teardown у finally:
        без очікування браузер може закритись до того, як платформа
        обробить запит, і позиція залишиться відкритою.

        Затримка закриття — до 5 секунд (беремо 10 для запасу).
        """
        # Крок 1: клікаємо маленьку кнопку біля позиції — відкриває модалку
        self.close_position_button.click()

        # Крок 2: чекаємо появи модалки (заголовок як якір)
        expect(self.close_position_modal_heading).to_be_visible(timeout=5_000)

        # Крок 3: клікаємо confirm у модалці
        self.close_position_modal_confirm.click()

        # Крок 4: чекаємо реального закриття позиції на платформі
        expect(self.no_positions_text).to_be_visible(timeout=10_000)


    def get_long_position_margin(self) -> float:
        """Прочитати поточне значення Margin у Long-позиції BTCUSDC.

        Чекає, поки клітинка покаже число у форматі "X.XX" (не плейсхолдер
        типу "—" або "0"), потім парсить у float. Це критично для тестів
        netting-моделі, де треба порівнювати margin до/після зміни позиції.

        Затримка появи реального значення — до 5 секунд (беремо 10 для запасу).

        Raises:
            ValueError: якщо текст не парситься як float (несподіваний формат UI).
        """
        # Чекаємо, поки текст у клітинці буде числом, а не плейсхолдером.
        # Regex ловить формат "4.11", "10.05", etc — два знаки після коми
        # (так платформа форматує margin).
        expect(self.long_position_margin).to_have_text(
            re.compile(r"^\d+\.\d+$"), timeout=10_000
        )
        margin_text = self.long_position_margin.inner_text()
        return float(margin_text)