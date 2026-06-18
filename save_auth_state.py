"""
Утиліта для збереження авторизованої сесії.

Запускайте раз, коли потрібно оновити стан авторизації:
    python save_auth_state.py

Скрипт відкриє браузер, дочекається ручного логіну,
і збереже cookies/localStorage у auth_state.json.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright


PLATFORM_URL = "https://beta-dex.truefinance.ai/trading/BTCUSDC"
AUTH_STATE_FILE = "auth_state.json"


def save_auth_state():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(PLATFORM_URL)

        print("\n" + "=" * 60)
        print("БРАУЗЕР ВІДКРИТО")
        print("=" * 60)
        print("1. Залогіньтеся через ваш звичайний flow")
        print("   (Phantom / Email / Google — будь-який спосіб)")
        print("2. Переконайтеся, що ви бачите свій баланс/позиції")
        print("3. Поверніться у термінал і натисніть Enter")
        print("=" * 60 + "\n")

        input("Натисніть Enter після успішного логіну...")

        # Зберігаємо стан авторизації
        context.storage_state(path=AUTH_STATE_FILE)

        print(f"\n✅ Стан авторизації збережено у {AUTH_STATE_FILE}")
        print("Тепер тести можуть використовувати цю сесію.")

        browser.close()


if __name__ == "__main__":
    save_auth_state()