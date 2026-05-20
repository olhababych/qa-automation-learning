from playwright.sync_api import Page


class BasePage:
    """
    Базовий клас для всіх Page Objects.
    Містить спільну логіку, яка стосується будь-якої сторінки.
    """

    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str) -> None:
        """Відкрити URL у браузері."""
        self.page.goto(url)

    def take_screenshot(self, filename: str) -> None:
        """Зробити повноекранний скріншот сторінки."""
        self.page.screenshot(path=filename, full_page=True)