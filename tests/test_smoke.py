from playwright.sync_api import expect
from pages.trading_page import TradingPage


def test_trading_page_opens(trading_page: TradingPage):
    """Smoke-тест: сторінка торгівлі BTCUSDC відкривається."""
    trading_page.open()
    expect(trading_page.page).to_have_url(TradingPage.URL)


def test_sign_in_button_visible(trading_page: TradingPage):
    """Перевіряємо, що кнопка 'Sign In' присутня і видима на сторінці."""
    trading_page.open()
    expect(trading_page.sign_in_button).to_be_visible()


def test_trading_pair_selector_visible(trading_page: TradingPage):
    """Перевіряємо, що селектор торгової пари відображається у верху сторінки."""
    trading_page.open()
    expect(trading_page.trading_pair_button).to_be_visible()

def test_sign_in_opens_auth_modal(trading_page: TradingPage):
    """Клік по Sign In відкриває модальне вікно авторизації."""
    trading_page.open()
    trading_page.click_sign_in()
    expect(trading_page.auth_modal_heading).to_be_visible()


def test_auth_modal_can_be_closed(trading_page: TradingPage):
    """Модальне вікно авторизації закривається через X."""
    trading_page.open()
    trading_page.click_sign_in()
    expect(trading_page.auth_modal_heading).to_be_visible()
    trading_page.close_auth_modal()
    expect(trading_page.auth_modal_heading).to_be_hidden()  
    

def test_orders_tab_switches_content(trading_page: TradingPage):
    """Перемикання на вкладку Orders показує відповідний контент."""
    trading_page.open()
    trading_page.orders_tab.click()
    expect(trading_page.no_orders_text).to_be_visible()


def test_positions_history_tab_switches_content(trading_page: TradingPage):
    """Перемикання на вкладку Positions history показує відповідний контент."""
    trading_page.open()
    trading_page.positions_history_tab.click()
    expect(trading_page.no_positions_history_text).to_be_visible()


def test_order_history_tab_switches_content(trading_page: TradingPage):
    """Перемикання на вкладку Order history показує відповідний контент."""
    trading_page.open()
    trading_page.order_history_tab.click()
    expect(trading_page.no_order_history_text).to_be_visible()


def test_positions_tab_is_default_active(trading_page: TradingPage):
    """За замовчуванням активна вкладка Positions."""
    trading_page.open()
    expect(trading_page.no_positions_text).to_be_visible()     


def test_size_input_accepts_number(trading_page: TradingPage):
    """Поле Size приймає числове значення."""
    trading_page.open()
    trading_page.fill_size("100")
    expect(trading_page.size_input).to_have_value("100")    