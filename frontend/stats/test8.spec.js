import { test, expect } from '@playwright/test';


const FILE_URL = `file://${process.cwd()}/dashboard.html`;


// ПЕРЕВІРКА ВІЗУАЛЬНИХ ЕЛЕМЕНТІВ ТА СТРУКТУРИ

test.describe('NutFit Dashboard - Елементи інтерфейсу', () => {

    test('Відображення головного заголовка та сітки графіків', async ({ page }) => {
        await page.goto(FILE_URL);
        await expect(page.locator('h1')).toHaveText('Дашборд статистики');
        await expect(page.locator('.grid')).toBeVisible();
    });

    test('Перевірка наявності всіх 4-х канвасів для графіків', async ({ page }) => {
        await page.goto(FILE_URL);
        await expect(page.locator('#calories-chart')).toBeVisible();
        await expect(page.locator('#macros-chart')).toBeVisible();
        await expect(page.locator('#workouts-chart')).toBeVisible();
        await expect(page.locator('#water-chart')).toBeVisible();
    });

});


// ТЕСТУВАННЯ ЛОГІКИ API ТА ВІДОБРАЖЕННЯ ДАНИХ

test.describe('NutFit Dashboard - Робота з даними та API', () => {

    test('Відображення кількості точок на графіку калорій через мета-дані', async ({ page }) => {
        await page.route('**/api/stats/calories*', route => route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                labels: ['Пн', 'Вт', 'Ср'],
                datasets: [{ data: [2000, 1800, 2100], label: 'Калорії' }]
            })
        }));

        await page.goto(FILE_URL);
        await expect(page.locator('#calories-meta')).toContainText('Точок: 3');
    });


    test('Коректність відображення відсотків БЖВ (білки, жири, вуглеводи)', async ({ page }) => {
        await page.route('**/api/stats/macros/today', route => route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                labels: ['Б', 'Ж', 'В'],
                datasets: [{ data: [30, 20, 50] }],
                percentages: { protein: 30, fat: 20, carbs: 50 }
            })
        }));

        await page.goto(FILE_URL);
        await expect(page.locator('#macros-meta')).toHaveText('Б: 30% | Ж: 20% | В: 50%');
    });

});

//ТЕСТУВАННЯ ОБРОБКИ ПОМИЛОК

test.describe('NutFit Dashboard - Сценарії помилок', () => {

    test('Поява повідомлення про помилку при збої сервера (500)', async ({ page }) => {
        await page.route('**/api/stats/**', route => route.fulfill({
            status: 500,
            body: 'Internal Server Error'
        }));

        await page.goto(FILE_URL);
        const errorElement = page.locator('#dashboard-error');
        await expect(errorElement).toBeVisible();
        await expect(errorElement).toContainText('Не вдалося завантажити статистику');
    });

    test('Обробка ситуації, коли Chart.js не завантажився', async ({ page }) => {
        await page.route('**/chart.umd.min.js', route => route.abort('failed'));
        await page.goto(FILE_URL);
        await expect(page.locator('#dashboard-error')).toContainText('Chart.js не завантажився');
    });

});