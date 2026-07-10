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
        # Дропдаун вибору торгової пари
        self.pair_search_input: Locator = page.get_by_placeholder(
            "Enter asset name or ticker"
        )
        
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
        self.order_notional_below_minimum_toast: Locator = page.get_by_text(
            "Order notional below minimum"
        )
        self.no_positions_history_text: Locator = page.get_by_text("No positions history")
        self.no_order_history_text: Locator = page.get_by_text("No order history")
        # Записи в історії (статуси-якорі)
        self.order_history_filled_status: Locator = page.get_by_text("Filled").first
        self.positions_history_closed_status: Locator = page.get_by_text("CLOSED").first

        # Поле розміру позиції (TODO: ask FE team for data-testid)
        #.first використовуємо, бо placeholder="0" може бути на кількох полях
        self.size_input: Locator = page.get_by_placeholder("0").first
        # Size input у Limit-режимі — другий textbox (перший це Price).
        # У Market-режимі використовуємо size_input (перший).
        self.size_input_limit: Locator = page.locator(
            "input[placeholder='0']"
        ).nth(1)

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
        # Тип ордера — combobox у формі (зверху, поряд з leverage).
        # Платформа використовує <combobox>, не звичайний <button>.
        self.order_type_combobox: Locator = page.get_by_role(
            "combobox"
        ).filter(has_text=re.compile(r"^(Market|Limit)$")).first

        # Опція "Limit" у дропдауні — з'являється після кліку на combobox.
        self.limit_order_option: Locator = page.get_by_role(
            "option", name="Limit"
        )
        # Поле ціни — з'являється тільки при виборі Limit. Має placeholder "0".
        # Локатор унікалізується тим, що Price input — єдиний textbox з лейблом Price.
        # Поле Price — це textbox з placeholder "0", без accessible name.
        # Той самий placeholder використовує і Size, тому беремо .first —
        # Price input з'являється першим у DOM (вище за Size) коли вибрано Limit.
        # Поле Price — це textbox з placeholder "0", без accessible name.
        # У Limit-режимі це перший textbox у формі (Size — другий).
        # У Market-режимі поля Price немає взагалі, тому price_input
        # використовується ТІЛЬКИ у Limit-флоу.
        self.price_input: Locator = page.locator(
            "input[placeholder='0']"
        ).nth(0)
        # Текст "No open orders" — плейсхолдер коли таблиця ордерів порожня.
        self.no_orders_text: Locator = page.get_by_text("No open orders")
        # Reduce Only checkbox — обмежує ордер до зменшення/закриття позиції.
        # Реалізовано як checkbox у формі ордера (під полем Size).
        self.reduce_only_checkbox: Locator = page.get_by_role(
            "checkbox", name="Reduce Only"
        )
        # Тост помилки Reduce Only — з'являється при спробі збільшити позицію
        # з увімкненим Reduce Only.
        self.reduce_only_error_toast: Locator = page.get_by_text(
            "Reduce-only order cannot increase position size"
        )
        # Take Profit / Stop Loss
        self.tpsl_checkbox: Locator = page.get_by_role(
            "checkbox", name="Take Profit / Stop Loss"
        )
        self.tp_price_input: Locator = page.get_by_placeholder("TP Price")
        self.tp_above_market_error: Locator = page.get_by_text("must be above market price")
        self.sl_price_input: Locator = page.get_by_placeholder("SL Price")
        self.tp_order_placed_toast: Locator = page.get_by_text("Take Profit order placed")
        self.sl_order_placed_toast: Locator = page.get_by_text("Stop Loss order placed")
        # Фінансові операції
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
        self.close_position_button: Locator = page.get_by_role("button", name="Close position").first

        # Заголовок модалки — використовуємо як якір "модалка з'явилась":
        self.close_position_modal_heading: Locator = page.get_by_text("Close position?")

        # Кнопка підтвердження в модалці — є дві кнопки з назвою "Close position",
        # тому розрізняємо її через локалізацію всередині модалки.
        # Використовуємо filter has_text на тексті модалки як sibling-якір.
        self.close_position_modal_confirm: Locator = page.locator(
            "button", has_text="Close position"
        ).last

        # Кнопка Cancel у модалці підтвердження закриття позиції.
        # exact=True щоб не зачепити інші можливі "Cancel ..." кнопки.
        self.close_position_modal_cancel: Locator = page.get_by_role(
            "button", name="Cancel", exact=True
        )

        # Cancel order модалка — двоетапний flow (як close_position).
        # Заголовок "Cancel order?" з'являється після кліку × у рядку ордера.
        self.cancel_order_modal_heading: Locator = page.get_by_text("Cancel order?")
        # Confirm кнопка — "Cancel order" (червона), exact=True щоб НЕ зачепити
        # сам heading "Cancel order?" чи поле тосту з тим самим текстом.
        # Confirm кнопка — велика червона "Cancel order" у модалці.
        # Має клас `bg-active-red` — на платформі це єдиний елемент з таким класом.
        # Confirm кнопка модалки — велика червона "Cancel order".
        # Sell/Short теж має клас bg-active-red, тому фільтруємо за текстом.
        self.cancel_order_modal_confirm: Locator = page.locator(
            "button.bg-active-red"
        ).filter(has_text="Cancel order")
        # Cancel order у рядку ордера — червоний × біля кожного ордера в таблиці.
        # Знайдемо першу видиму — у тестах буде тільки один ордер.
        # У DOM це <button> з aria-label, але точний label треба буде перевірити.
        # Поки використовуємо CSS-локатор через клас X icon у рядку ордера.
        # Кнопка × у рядку ордера — має accessible name "Cancel order"
        # (не плутати з кнопкою "Cancel order" у модалці підтвердження —
        # вона з ОДНАКОВИМ ім'ям, тому беремо .first, бо у рядку йде раніше).
        # Кнопка Cancel order у рядку ордера — за aria-label (клас hover:text-red-500 зник з DOM)
        # для розрізнення від модалки (там клас `bg-active-red`).
        self.cancel_first_order_button: Locator = page.get_by_role(
            "button", name="Cancel order"
        ).first
        
       
        # Edit Limit order — інлайн-редагування ціни прямо в рядку ордера.
        # Олівець "Edit order" має aria-label — стабільний семантичний якір.
        self.edit_first_order_button: Locator = page.get_by_role(
            "button", name="Edit order"
        ).first

        # Поле ціни у режимі редагування. У input немає aria-label/name/placeholder —
        # лише класи. Прив'язуємось до рядка ордера (h-14) і беремо єдиний input
        # усередині, щоб не залежати від інших полів на сторінці.
        # TODO: ask FE team for data-testid on edit price input.
        # Поле ціни у режимі редагування. У input немає aria-label/name/placeholder.
        # Прив'язуємось до самого input через його характерний клас h-6 (edit-поле
        # маленьке, h-6) — він з'являється лише після кліку олівця і єдиний такий
        # у таблиці ордерів. Не залежить від класу рядка-обгортки.
        # TODO: ask FE team for data-testid on edit price input.
        self.edit_order_price_input: Locator = page.locator(
        "input.h-6"
        ).first

        # Зелена галочка підтвердження — aria-label="Save".
        self.edit_order_save_button: Locator = page.get_by_role(
            "button", name="Save"
        )

        # Тост успіху після збереження редагування.
        self.order_updated_toast: Locator = page.get_by_text("Order updated")

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
        # Тост "Market order filled" — перекриває рядок позиції; чекаємо його зникнення
        self.order_filled_toast: Locator = page.get_by_text("Market order filled")
        self.long_position_margin: Locator = (
            page.locator("img[alt='long']")
            .locator("xpath=ancestor::div[contains(@class, 'h-14')][1]")
            .locator("> div").nth(-3)
        )
        # Margin для Short — третя колонка з кінця (та сама логіка, що для long).
        self.short_position_indicator: Locator = page.locator("img[alt='short']")
        self.short_position_margin: Locator = (
        page.locator("img[alt='short']")
        .locator("xpath=ancestor::div[contains(@class, 'h-14')][1]")
        .locator("> div").nth(-3)
)
        
        # Size позиції — 4-та колонка таблиці (Direction, Asset, Leverage, SIZE, ...).
        # Розмір у BTC (наприклад, "0.0031"). На відміну від margin, Size не змінюється
        # при зміні leverage — це фіксована кількість токенів у позиції.
        self.long_position_size: Locator = (
            page.locator("img[alt='long']")
            .locator("xpath=ancestor::div[contains(@class, 'h-14')][1]")
            .locator("> div").nth(-6)
        )

        # Leverage селектор і модалка
        # Кнопка показує поточний leverage у форматі "Nx" (1x, 20x, 50x тощо).
        # Regex дозволяє знайти її незалежно від поточного значення —
        # критично для тестів, які міняють leverage (вони лишають кнопку у
        # стані, відмінному від default 50x, на час cleanup).
        self.leverage_button: Locator = page.get_by_role(
            "button", name=re.compile(r"^\d+x$")
        )
        self.leverage_modal_heading: Locator = page.get_by_text("Adjust BTCUSDC Leverage")
        self.leverage_modal_close: Locator = page.get_by_role("button", name="Close", exact=True)
        self.leverage_modal_confirm: Locator = page.get_by_role("button", name="Confirm")

        # Значення leverage всередині модалки, формат "x50", "x49", "x100"
        # TODO: replace with data-testid when FE adds them
        # Локалізуємо через текст "x50" як якір — від нього беремо сусідні кнопки
        # Значення leverage у модалці — це <div>, тоді як на бейджі пари це <span>
        # TODO: replace with data-testid when FE adds them
        self.leverage_modal_value: Locator = page.locator(
            "div.text-\\[15px\\]"
        ).filter(has_text=re.compile(r"^x\d+$")).first
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
        # Amount input модалки Deposit — input з атрибутом name="amount".
        self.deposit_amount_input: Locator = page.locator("input[name='amount']")
        self.withdraw_amount_input: Locator = page.locator(
            "xpath=//*[contains(text(), 'Withdrawable')]/following::input[not(@type='checkbox')][1]"
        )
        self.deposit_modal_submit: Locator = page.locator(
            "button.w-full"
        ).filter(has_text="Deposit").first
        self.withdraw_modal_submit: Locator = page.locator(
            "button.w-full"
        ).filter(has_text="Withdraw").first
        self.deposit_available_balance: Locator = page.get_by_text("Avail.").first
        self.withdraw_available_balance: Locator = page.get_by_text("Withdrawable")
        self.below_minimum_withdrawal_error: Locator = page.get_by_text(
            "Minimum withdrawal is 1 USDC"
        )
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
        
        
    def switch_to_pair(self, ticker: str) -> None:
        """Перемкнути торгову пару через дропдаун селектора.
        Клік на селектор пари → пошук тикера → вибір рядка зі списку.
        Args:
            ticker: тикер пари, напр. "SOL" (шукає "SOL/USDC").
        """
        self.trading_pair_button.click()
        expect(self.pair_search_input).to_be_visible(timeout=10_000)
        self.pair_search_input.fill(ticker)
        # Вибрати рядок пари зі списку (напр. "SOL/USDC")
        self.page.get_by_text(f"{ticker}/USDC", exact=False).first.click()

    def fill_size(self, value: str) -> None:
        """Ввести значення в поле розміру позиції."""
        self.size_input.fill(value)
        
        
    def select_long(self) -> None:
        """Перемкнути напрямок угоди на Long."""
        self.long_tab.click()


    def select_short(self) -> None:
        """Перемкнути напрямок угоди на Short."""
        self.short_tab.click()

    def enable_reduce_only(self) -> None:
        """Увімкнути чекбокс Reduce Only у формі ордера.

        Reduce Only обмежує ордер: він може тільки зменшити/закрити позицію,
        але не може її збільшити чи відкрити нову. Якщо клікнути ордер
        з увімкненим Reduce Only коли позиція збільшується — платформа
        відхиляє ордер з тостом помилки.

        Чому force=True: чекбокс реалізований як кастомний Tailwind компонент,
        де <input type="checkbox"> прихований класом 'sr-only peer', а видимий
        <span> поверх нього перехоплює pointer events. Playwright не може
        клікнути прихований input напряму — використовуємо force=True для
        обходу actionability check. Стан чекбоксу все одно змінюється коректно.
        """
        self.reduce_only_checkbox.check(force=True)
        # Sanity check: чекбокс реально увімкнений
        expect(self.reduce_only_checkbox).to_be_checked(timeout=5_000)


    def _wait_for_stable_btc_equivalent(self) -> None:
        """Чекати, поки BTC-еквівалент під полем Size стане стабільним.

        Проблема: після fill_size UI оновлює "~X BTC" в декілька етапів —
        спочатку платформа підраховує приблизно, потім уточнює за оракулом.
        Якщо клікнути Buy/Long між цими оновленнями, платформа отримує
        запит зі застарілим Size і повертає "fail quantity" або
        "Order notional below minimum".

        Стратегія: читати текст до 10 разів з паузою 500мс, шукати два
        однакові послідовні значення (UI стабілізувався). Якщо за 5 секунд
        не стабілізувалось — виходимо тихо, нехай платформа сама розбирається
        (краще ніж блокувати тест нескінченно).
        """
        last_text = ""
        for _ in range(10):
            current = self.size_btc_equivalent.inner_text()
            if current == last_text and current.startswith("~"):
                return
            last_text = current
            self.page.wait_for_timeout(500)

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

    def set_leverage(self, target: int) -> None:
        """Встановити конкретне значення leverage через модалку.

        Відкриває модалку, циклічно клікає +/- до досягнення target,
        читаючи актуальне значення з UI після кожного кліку, потім Confirm.

        Чому читаємо UI замість локального counter'а: платформа іноді
        пропускає кліки (race condition у обробці input'ів). Якщо локально
        рахувати "клікнув мінус = -1", лічильник розходиться з реальним
        UI станом. Читаючи UI, ми завжди знаємо точний стан.

        Безпека:
        - target має бути в діапазоні [1, 50] (max_leverage за конфігом ринку)
        - safety counter — захист від нескінченного циклу
        - якщо клік не змінив значення UI, expect.not_to_have_text
          падає з timeout — це сигнал, що платформа ігнорує кліки

        Args:
            target: цільове значення leverage (1-50).

        Raises:
            ValueError: target поза дозволеним діапазоном.
            AssertionError: якщо UI не оновився після кліку (платформа
                пропустила натискання) або перевищено max ітерацій.
        """
        if not 1 <= target <= 50:
            raise ValueError(
                f"Leverage target must be between 1 and 50, got {target}"
            )

        self.open_leverage_modal()
        expect(self.leverage_modal_value).to_be_visible(timeout=10_000)

        # Safety counter: max 60 ітерацій (більше за max_leverage=50 для запасу)
        max_iterations = 60
        iterations = 0

        while True:
            if iterations >= max_iterations:
                raise AssertionError(
                    f"set_leverage exceeded {max_iterations} iterations. "
                    f"Target {target}, never reached."
                )

            # Читаємо актуальний стан UI — це джерело правди, не локальний counter
            current_text = self.leverage_modal_value.inner_text()
            current = int(current_text.lstrip("x"))

            if current == target:
                break

            # Запам'ятовуємо текст до кліку, щоб дочекатися зміни
            previous_text = current_text

            if current < target:
                self.leverage_modal_increase.click()
            else:
                self.leverage_modal_decrease.click()

            # Чекаємо, поки UI **зміниться** з previous_text.
            # Якщо клік пропущено платформою — текст не зміниться, expect
            # впаде з timeout. Це сигнал реального bug'а, не помилки тесту.
            expect(self.leverage_modal_value).not_to_have_text(
               previous_text, timeout=5_000
            )
            iterations += 1

        # Застосувати зміну
        self.leverage_modal_confirm.click()

        # Чекаємо, поки модалка реально закриється.
        # Після кліку Confirm текст кнопки змінюється на "Processing…"
        # і модалка з backdrop ще 3-5 секунд видима, блокуючи інші кліки.
        # Без цього очікування наступний крок тесту (наприклад, Buy/Long)
        # не може клікнути нічого, бо модалка перекриває pointer events.
        # Чекаємо, поки backdrop (півпрозорий чорний overlay) зникне.
        # Текст заголовка модалки зникає швидше, ніж backdrop, тож якщо
        # чекати на heading — Playwright продовжить роботу, поки backdrop
        # ще блокує всі pointer events. Чекаємо на сам backdrop.
        backdrop = self.page.locator("div.bg-black\\/60.backdrop-blur-xs")
        expect(backdrop).not_to_be_visible(timeout=15_000)


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
        

    def open_long_with_tpsl(self, size: str, tp_price: str, sl_price: str) -> None:
        """Відкрити Long-позицію з Take Profit і Stop Loss.
        Вмикає чекбокс TP/SL, заповнює TP Price і SL Price, потім Buy/Long.
        Для Long: TP має бути ВИЩЕ ринку, SL — НИЖЧЕ ринку.
        Args:
            size: розмір у USDC, напр. "150".
            tp_price: ціна Take Profit (вище ринку), напр. "59920".
            sl_price: ціна Stop Loss (нижче ринку), напр. "58733".
        """
        self.select_long()
        self.fill_size(size)
        expect(self.size_btc_equivalent).to_have_text(
            re.compile(r"^~\d+\.\d+\s+BTC$"), timeout=5_000
        )
        self.tpsl_checkbox.check(force=True)
        expect(self.tpsl_checkbox).to_be_checked(timeout=5_000)
        self.tp_price_input.fill(tp_price)
        self.sl_price_input.fill(sl_price)
        self.buy_long_button.click()

    def open_short_with_tpsl(self, size: str, tp_price: str, sl_price: str) -> None:
        """Відкрити Short-позицію з Take Profit і Stop Loss.
        Для Short: TP має бути НИЖЧЕ ринку, SL — ВИЩЕ ринку (дзеркало Long).
        Args:
            size: розмір у USDC.
            tp_price: ціна Take Profit (нижче ринку).
            sl_price: ціна Stop Loss (вище ринку).
        """
        self.select_short()
        self.fill_size(size)
        expect(self.size_btc_equivalent).to_have_text(
            re.compile(r"^~\d+\.\d+\s+BTC$"), timeout=5_000
        )
        self.tpsl_checkbox.check(force=True)
        expect(self.tpsl_checkbox).to_be_checked(timeout=5_000)
        self.tp_price_input.fill(tp_price)
        self.sl_price_input.fill(sl_price)
        self.sell_short_button.click()

    def disable_tpsl_if_enabled(self) -> None:
        """Зняти галку Take Profit / Stop Loss, якщо вона увімкнена.
        На dex-dev TP/SL тепер увімкнений за замовчуванням — для звичайних
        ордерів (без TP/SL) його треба знімати, інакше порожні TP/SL поля
        блокують створення ордера.
        """
        if self.tpsl_checkbox.is_checked():
            self.tpsl_checkbox.uncheck(force=True)
            expect(self.tpsl_checkbox).not_to_be_checked(timeout=5_000)

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
        # Додаткова стабілізація — чекаємо, поки UI перестане оновлювати
        # BTC-еквівалент (зазвичай ~1 сек після першої появи).
        self._wait_for_stable_btc_equivalent()
        self.disable_tpsl_if_enabled()
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
        # Додаткова стабілізація — див. коментар у open_long_position.
        self._wait_for_stable_btc_equivalent()
        self.disable_tpsl_if_enabled()
        self.sell_short_button.click()

    def select_limit_order_type(self) -> None:
        """Переключити тип ордера на Limit через combobox.

        За замовчуванням платформа використовує Market — для Limit треба
        явно вибрати у dropdown. Після переключення з'являється поле Price,
        яке відсутнє в Market.

        Метод ідемпотентний: якщо Limit уже вибрано, повторний виклик
        нічого не зламає (другий клік просто закриє і знов відкриє dropdown).
        """
        self.order_type_combobox.click()
        self.limit_order_option.click()
        # Sanity check: поле Price з'явилось — значить Limit реально вибрано.
        expect(self.price_input).to_be_visible(timeout=5_000)

    def create_limit_long_order(self, price: str, size: str) -> None:
        """Створити Limit Long ордер з заданою ціною та розміром у USDC.

        Сценарій:
        1. Перемкнути тип ордера на Limit.
        2. Перемкнути напрямок на Long.
        3. Ввести ціну (у форматі "60000" — без коми).
        4. Ввести Size (у USDC).
        5. Чекати, поки UI розрахує BTC-еквівалент.
        6. Клікнути Buy / Long.

        Ціну зазвичай задаємо НИЖЧЕ ринкової ціни (для Long) — щоб ордер
        НЕ виконався одразу, а залишився відкритим у списку Orders.
        Це дозволяє тестувати лайфцикл Limit-ордерів (створення, скасування)
        без реальних угод.
        """
        self.select_limit_order_type()
        self.select_long()
        self.price_input.fill(price)
        # У Limit-режимі size_input — другий textbox; fill_size() використовує
        # перший, тому пишемо напряму у size_input_limit.
        self.size_input_limit.fill(size)
        # Чекаємо, поки UI відобразить НЕ-нульовий BTC-еквівалент
        # (на платформі BTC-розрахунок асинхронний — див. _wait_for_stable_btc_equivalent).
        expect(self.size_btc_equivalent).to_have_text(
            re.compile(r"^~0\.\d+\s+BTC$"), timeout=5_000
        )
        self._wait_for_stable_btc_equivalent()
        self.disable_tpsl_if_enabled()
        self.buy_long_button.click()

    def create_limit_short_order(self, price: str, size: str) -> None:
        """Створити Limit Short ордер з заданою ціною та розміром у USDC.

        Аналог create_limit_long_order для Short напрямку. Ціну зазвичай задаємо
        ВИЩЕ ринкової — щоб ордер НЕ виконався одразу, а залишився у списку
        Orders для тестування лайфциклу.
        """
        self.select_limit_order_type()
        self.select_short()
        self.price_input.fill(price)
        # У Limit-режимі size_input — другий textbox (перший це Price).
        self.size_input_limit.fill(size)
        # Чекаємо, поки UI відобразить НЕ-нульовий BTC-еквівалент.
        expect(self.size_btc_equivalent).to_have_text(
            re.compile(r"^~0\.\d+\s+BTC$"), timeout=5_000
        )
        self._wait_for_stable_btc_equivalent()
        self.disable_tpsl_if_enabled()
        self.sell_short_button.click()

    def cancel_first_order(self) -> None:
        """Скасувати перший Limit-ордер у списку Orders через двоетапний UI-флоу.

        На платформі скасування — двоетапний процес (як close_position):
        1. Клік × у рядку ордера → відкриває модалку "Cancel order?"
        2. Клік "Cancel order" (червона кнопка у модалці) → підтверджує

        Метод чекає реального зникнення ордера зі списку перш ніж повернути
        керування — це критично для використання як teardown у finally.

        Затримка скасування — до 5 секунд на платформі, беремо 20 для запасу.
        """
        # Крок 1: клікаємо × біля ордера — відкриває confirmation модалку
        self.cancel_first_order_button.click(timeout=60_000)

        # Крок 2: чекаємо появи модалки
        expect(self.cancel_order_modal_heading).to_be_visible(timeout=10_000)

        # Крок 3: клікаємо confirm у модалці
        self.cancel_order_modal_confirm.click()

        # Крок 4: чекаємо реального зникнення ордера зі списку
        expect(self.no_orders_text).to_be_visible(timeout=20_000)

    def edit_first_order_price(self, new_price: str) -> None:
        """Змінити ціну першого Limit-ордера через інлайн-редагування.

        Клік олівця Edit order перетворює Price на поле вводу; після Save
        платформа показує тост Order updated і оновлює ціну в рядку.
        Edit не виконує ордер, якщо нова ціна лишається нижче ринку (Long).

        Args:
            new_price: нова ціна, напр. "55000" (без коми).
        """
        expect(self.edit_first_order_button).to_be_visible(timeout=20_000)
        self.edit_first_order_button.click(timeout=60_000)
        expect(self.edit_order_price_input).to_be_visible(timeout=10_000)
        self.edit_order_price_input.fill(new_price)
        self.edit_order_save_button.click()

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
        # Крок 1: дочекатись появи кнопки × (після Cancel у модалці вона може
        # перемальовуватись із затримкою) і клікнути — відкриває модалку
        expect(self.close_position_button).to_be_visible(timeout=20_000)
        self.close_position_button.click(timeout=60_000)

        # Крок 2: чекаємо появи модалки (заголовок як якір)
        expect(self.close_position_modal_heading).to_be_visible(timeout=10_000)

        # Крок 3: клікаємо confirm у модалці
        self.close_position_modal_confirm.click()

        # Крок 4: чекаємо реального закриття позиції на платформі
        expect(self.no_positions_text).to_be_visible(timeout=20_000)



    def cleanup_all(self) -> None:
        """Закрити всі позиції й скасувати всі ордери. Для teardown-фікстури.
        Безпечний: ловить винятки, не валить тест якщо чисто."""
        try:
            self.orders_tab.click(timeout=10_000)
            for _ in range(10):
                if self.no_orders_text.is_visible():
                    break
                try:
                    self.cancel_first_order()
                except Exception:
                    break
        except Exception:
            pass
        try:
            self.positions_tab.click(timeout=10_000)
        except Exception:
            pass
        for _ in range(10):
            try:
                if self.no_positions_text.is_visible():
                    break
                self.close_position()
            except Exception:
                break

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
        # Тост Market order filled може перекривати рядок — чекаємо зникнення
        expect(self.order_filled_toast).to_have_count(0, timeout=15_000)
        expect(self.long_position_margin).to_have_text(
            re.compile(r"^\d+\.\d+$"), timeout=20_000
        )
        margin_text = self.long_position_margin.inner_text()
        return float(margin_text)
    

    def get_long_position_size(self) -> float:
        """Прочитати поточне значення Size у Long-позиції BTCUSDC.

        Size — це кількість BTC у позиції (наприклад, "0.0031"). На відміну
        від margin, Size НЕ змінюється при зміні leverage — це фіксована
        кількість токенів. Використовується у тестах, які перевіряють
        збереження розміру позиції при операціях типу зміни leverage.

        Затримка появи значення — до 20 секунд (для повільного dev-бекенду).

        Raises:
            ValueError: якщо текст не парситься як float.
        """
        # Чекаємо, поки текст у клітинці буде числом у форматі "0.0031"
        # (BTC має дробову частину з різною кількістю знаків).
        expect(self.order_filled_toast).to_have_count(0, timeout=15_000)
        expect(self.long_position_size).to_have_text(
            re.compile(r"^\d+\.\d+$"), timeout=20_000
        )
        size_text = self.long_position_size.inner_text()
        return float(size_text)

   
    def wait_for_long_position_margin_change(self, from_value: float) -> float:
        """Чекає, поки margin Long-позиції зміниться відносно from_value,
        і повертає нове значення як float.

        Використовується після дій, які повинні змінити позицію (наприклад,
        netting через Short). Без очікування читання margin одразу після
        кліку може повернути старе значення, бо UI ще не оновився —
        Playwright бачить попередній рядок таблиці у DOM, який ще не
        перерендерився.

        Реалізація використовує Playwright auto-retry через `expect`:
        бібліотека сама повторює перевірку, поки текст не зміниться
        або не сплине timeout.

        Args:
            from_value: попереднє значення margin, від якого чекаємо змін.

        Returns:
            Нове значення margin після зміни.

        Raises:
            AssertionError: якщо margin не змінився за 10 секунд.
        """
        # Формуємо текст у тому ж форматі, як платформа його показує
        # (два знаки після коми — "4.11", "2.06").
        previous_text = f"{from_value:.2f}"
        expect(self.long_position_margin).not_to_have_text(
            previous_text, timeout=20_000
        )
        new_text = self.long_position_margin.inner_text()
        return float(new_text)