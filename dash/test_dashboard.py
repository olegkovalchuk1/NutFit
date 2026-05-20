import os
import pytest
from playwright.sync_api import Page, expect

def test_dashboard_charts_integration(page: Page):
    #ОБХІД БЛОКУВАННЯ
    html_path = os.path.abspath('dashboard.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    page.route("http://localhost/dashboard/", lambda route: route.fulfill(
        content_type="text/html",
        body=html_content
    ))

    #1. ОТРИМАННЯ ДАНИХ
    page.route("**/api/stats/calories*", lambda route: route.fulfill(
        json={"labels": ["Пн", "Вв", "Ср"], "datasets": [{"label": "Калорії", "data": [2000, 2100, 1900]}]}
    ))
    page.route("**/api/stats/macros/today", lambda route: route.fulfill(
        json={
            "labels": ["Білки", "Жири", "Вуглеводи"], 
            "datasets": [{"data": [30, 20, 50]}], 
            "percentages": {"protein": 30, "fat": 20, "carbs": 50}
        }
    ))
    page.route("**/api/stats/workouts/week", lambda route: route.fulfill(
        json={"labels": ["Пн"], "datasets": [{"data": [300]}], "week_start": "01.05", "week_end": "07.05"}
    ))
    page.route("**/api/stats/water/week", lambda route: route.fulfill(
        json={"labels": ["Пн"], "datasets": [{"data": [2]}], "week_start": "01.05", "week_end": "07.05"}
    ))

    page.goto("http://localhost/dashboard/")

    # 2. ВІДОБРАЖЕННЯ: Перевірка рендеру canvas-елементів у DOM
    for chart_id in ["calories-chart", "macros-chart", "workouts-chart", "water-chart"]:
        expect(page.locator(f"#{chart_id}")).to_be_visible()

    # 3. ОБРОБКА ДАНИХ: Перевірка парсингу JSON та виводу метаданих в UI
    expect(page.locator("#calories-meta")).to_have_text("Точок: 3")
    expect(page.locator("#macros-meta")).to_have_text("Б: 30% | Ж: 20% | В: 50%")
    expect(page.locator("#workouts-meta")).to_have_text("01.05 - 07.05")
    expect(page.locator("#water-meta")).to_have_text("01.05 - 07.05")

    # 4. ІНТЕГРАЦІЯ З CHART.JS: Перевірка фактичних даних всередині об'єкта графіка
    calories_chart_data = page.evaluate("""() => {
        const chart = Chart.getChart("calories-chart");
        return chart ? chart.data.datasets[0].data : null;
    }""")
    assert calories_chart_data == [2000, 2100, 1900]
    
    # Перевірка відсутності помилок на сторінці
    expect(page.locator("#dashboard-error")).to_be_empty()