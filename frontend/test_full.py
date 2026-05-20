import pytest
from playwright.sync_api import sync_playwright
import os
import re

def get_video_id(url):
    """Витягує унікальний ID відео з будь-якого формату посилання YouTube."""
    match = re.search(r"(?:embed/|youtu\.be/|v=)([^?&]+)", url)
    return match.group(1) if match else None

def test_workout_app():
    with sync_playwright() as p:
        # Запуск браузера
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Шлях до файлу
        path = os.path.abspath("exercise.html")
        page.goto(f"file://{path}")
        print("\nПЕРЕВІРКА ПРОЄКТУ")

        # --- ЧАСТИНА 1: ТЕСТ ТРЕКЕРА ТА ПАМ'ЯТІ ---
        print("\n--- Етап 1: Трекер та LocalStorage ---")
        first_cell = page.locator("#grid .cell").first
        first_cell.click()
        
        if "active" in first_cell.get_attribute("class"):
            print("✅ Клітинка активується при кліку")
        
        page.reload()
        reloaded_cell = page.locator("#grid .cell").first
        assert "active" in reloaded_cell.get_attribute("class"), "❌ ПОМИЛКА: Дані не збереглися після оновлення!"
        print("✅ LocalStorage працює: прогрес збережено")

        # --- ЧАСТИНА 2: ТЕСТ ІНТЕРФЕЙСУ (TOGGLE) ---
        print("\n--- Етап 2: Інтерактивність опису ---")
        workout_title = page.locator(".title-row").first
        hidden_content = page.locator(".hidden").first
        
        workout_title.click()
        page.wait_for_timeout(500) # невелика затримка для анімації
        assert hidden_content.is_visible(), "❌ ПОМИЛКА: Опис тренування не відкрився!"
        print("✅ Блоки з описом розгортаються коректно")

        # --- ЧАСТИНА 3: ПЕРЕВІРКА ВСІХ ВІДЕО З ФАЙЛУ ---
        print("\n--- Етап 3: Валідація відеоконтенту ---")
        
        # Читаємо посилання з файлу links.txt
        if os.path.exists("links.txt"):
            with open("links.txt", "r") as f:
                file_links = [line.strip() for line in f if "youtu" in line]
            expected_ids = [get_video_id(link) for link in file_links]
        else:
            print("⚠️ Файл links.txt не знайдено! Перевірку відео пропущено.")
            expected_ids = []

        iframes = page.locator("iframe")
        video_count = iframes.count()
        print(f"Знайдено відео на сторінці: {video_count}")

        errors = 0
        for i in range(video_count):
            video_src = iframes.nth(i).get_attribute("src")
            current_id = get_video_id(video_src)
            
            if current_id in expected_ids:
                print(f"  [{i+1}] ID {current_id} — ВІРНО ✅")
            else:
                print(f"  [{i+1}] ID {current_id} — НЕМАЄ В СПИСКУ ❌")
                errors += 1

        if video_count != len(expected_ids):
            print(f"⚠️ Увага: Кількість відео ({video_count}) не збігається з ТЗ ({len(expected_ids)})")

        # Фінальний результат
        print("\n" + "="*30)
        if errors == 0:
            print("ТЕСТ ПРОЙДЕНО: Проєкт працює ідеально!")
        else:
            print(f"⚠️ ТЕСТ ЗАВЕРШЕНО: Знайдено помилок у відео: {errors}")
        print("="*30)

        browser.close()

if __name__ == "__main__":
    test_workout_app()