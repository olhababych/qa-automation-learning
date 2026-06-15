from playwright.sync_api import Page


class BasePage:
    """
    Базовий клас для всіх Page Objects.
    Містить спільну логіку, яка стосується будь-якої сторінки.
    """

    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str) -> None:
        """Відкрити URL у браузері з повним reload.

        Чому reload після goto: Playwright може skip-нути перезавантаження,
        якщо URL не змінився (це поведінка SPA — клієнтський роутинг
        не тригерить full reload). На платформі TruefFinance це призводить до
        просочення стану між тестами: leverage не скидається на 50x,
        UI кеш з попередньої сесії залишається.

        Чому wait_for_timeout 2000: платформа повільна на dev-сервері, після
        reload UI рендериться поетапно. Без явного очікування наступний крок
        тесту може почати дії до того як leverage реально скинеться на 50.
        """
        self.page.goto(url)
        self.page.reload()
        self.page.wait_for_timeout(2000)

        
    def take_screenshot(self, filename: str) -> None:
        """Зробити повноекранний скріншот сторінки."""
        self.page.screenshot(path=filename, full_page=True)