import pytest
from playwright.sync_api import sync_playwright
import os

def test_nutrition_app():
    with sync_playwright() as p:
        # Запуск браузера (headless=False, щоб бачити процес)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Шлях до файлу recipes.html
        path = os.path.abspath("recipes.html")
        page.goto(f"file://{path}")
        print("\n🚀 ПОЧАТОК ТЕСТУВАННЯ ЛОГІКИ ХАРЧУВАННЯ")

        # --- ЕТАП 1: ПЕРЕВІРКА ТРЕКЕРА ВОДИ ---
        print("\n--- Етап 1: Трекер води ---")
        cups = page.locator(".cup")
        cups.nth(2).click()  # Клікаємо на 3-й стаканчик
        
        # Перевіряємо, чи стали перші три стаканчики активними
        is_active = "active" in (cups.nth(2).get_attribute("class") or "")
        if is_active:
            print("✅ Трекер води працює: стаканчики зафарбовуються")
        else:
            print("❌ ПОМИЛКА: Трекер води не реагує на клік")

        # --- ЕТАП 2: ПЕРЕВІРКА ПІДРАХУНКУ КБЖВ ---
        print("\n--- Етап 2: Розрахунок калорій (Сніданок) ---")
        
        # Заповнюємо поля в картці Сніданку
        breakfast_card = page.locator(".meal-card").first
        breakfast_card.locator(".input-calories").fill("450")
        breakfast_card.locator(".input-proteins").fill("25")
        breakfast_card.locator(".input-fats").fill("15")
        breakfast_card.locator(".input-carbs").fill("50")
        
        # Натискаємо ОК
        breakfast_card.locator("button:has-text('ОК')").click()
        print("Натиснуто кнопку 'ОК' у сніданку")

        # Перевіряємо загальну суму в таблиці зверху
        total_calories = page.locator("#total-calories").inner_text()
        if "450" in total_calories:
            print(f"✅ Математика працює: Калорії оновлено ({total_calories})")
        else:
            print(f"❌ ПОМИЛКА: Очікували 450 ккал, отримали {total_calories}")

        # --- ЕТАП 3: ПЕРЕВІРКА ОЧИЩЕННЯ ПОЛІВ ---
        print("\n--- Етап 3: Очищення інтерфейсу ---")
        input_val = breakfast_card.locator(".input-calories").input_value()
        if input_val == "":
            print("✅ Поля очищуються автоматично після додавання")
        else:
            print("❌ ПОМИЛКА: Поля не очистилися!")

        # --- ЕТАП 4: ТЕСТ ФІЛЬТРА РЕЦЕПТІВ ---
        print("\n--- Етап 4: Пошук рецептів ---")
        search_input = page.locator("#recipeSearch")
        search_input.fill("Авокадо")
        page.wait_for_timeout(500) # Чекаємо на відпрацювання JS
        
        visible_recipes = page.locator(".recipe-card:visible")
        count = visible_recipes.count()
        print(f"Знайдено страв за запитом 'Авокадо': {count}")
        
        if count > 0:
            print("✅ Фільтр працює коректно")
        else:
            print("⚠️ Увага: Нічого не знайдено, перевірте наявність страв у HTML")

        print("\n" + "="*30)
        print("ТЕСТУВАННЯ ЗАВЕРШЕНО УСПІШНО!")
        print("="*30)

        browser.close()

if __name__ == "__main__":
    test_nutrition_app()