const cups = document.querySelectorAll('.cup');

cups.forEach((cup, index) => {
    cup.addEventListener('click', () => {

        if (cup.classList.contains('active')) {
            for (let i = index; i < cups.length; i++) {
                cups[i].classList.remove('active');
            }
        } else {
            for (let i = 0; i <= index; i++) {
                cups[i].classList.add('active');
            }
        }

    });
});

function filterRecipes() {
    const input = document.getElementById('recipeSearch').value.toLowerCase();
    const grids = document.querySelectorAll('.recipe-grid');

    grids.forEach(grid => {
        const recipes = grid.querySelectorAll('.recipe-card'); // ✔️ правильний клас
        let hasVisibleRecipes = false;

        recipes.forEach(recipe => {
            const title = recipe.querySelector('.recipe-title').innerText.toLowerCase(); // ✔️ правильний клас

            if (title.includes(input)) {
                recipe.style.display = "block";
                hasVisibleRecipes = true;
            } else {
                recipe.style.display = "none";
            }
        });

        // ховаємо всю секцію якщо нічого не знайдено
        const section = grid.closest('section');

        if (hasVisibleRecipes) {
            grid.style.display = "grid";
            if (section) section.style.display = "";
        } else {
            grid.style.display = "none";
            if (section) section.style.display = "none";
        }
    });
}

// Функція для відображення норми з тесту
function displayNorma() {
    const cals = localStorage.getItem('normaCalories') || 0;
    const prots = localStorage.getItem('normaProteins') || 0;
    const fats = localStorage.getItem('normaFats') || 0;
    const carbs = localStorage.getItem('normaCarbs') || 0;

    const elCals = document.getElementById('norma-calories-display');
    const elProts = document.getElementById('norma-proteins-display');
    const elFats = document.getElementById('norma-fats-display');
    const elCarbs = document.getElementById('norma-carbs-display');

    if (elCals) elCals.innerText = cals + " ккал";
    if (elProts) elProts.innerText = prots + " г";
    if (elFats) elFats.innerText = fats + " г";
    if (elCarbs) elCarbs.innerText = carbs + " г";
}

// Функція для підрахунку з'їденого (для кнопок ОК)
function calculateTotal() {
    // Список категорій та відповідних ID у верхній таблиці
    const categories = [
        { class: 'input-calories', id: 'total-calories', unit: ' ккал' },
        { class: 'input-proteins', id: 'total-proteins', unit: ' г' },
        { class: 'input-fats', id: 'total-fats', unit: ' г' },
        { class: 'input-carbs', id: 'total-carbs', unit: ' г' }
    ];

    categories.forEach(cat => {
        // Знаходимо всі інпути цього класу (наприклад, у Сніданку, Обіді тощо)
        const inputs = document.querySelectorAll('.' + cat.class);
        const displayElement = document.getElementById(cat.id);
        
        // Отримуємо поточне число з таблички (прибираємо текст "г" або "ккал")
        let currentTotal = parseFloat(displayElement.innerText) || 0;
        
        let addedValue = 0;
        inputs.forEach(input => {
            const val = parseFloat(input.value) || 0;
            addedValue += val;
            input.value = ""; // ОЧИЩАЄМО ПОЛЕ після зчитування
        });

        // Додаємо нове до старого і оновлюємо екран
        let newTotal = currentTotal + addedValue;
        displayElement.innerText = Math.round(newTotal) + cat.unit;
    });
    
    // Також очистимо поле "Назва" у всіх картках
    document.querySelectorAll('.meal-card input[placeholder="Назва"]').forEach(nameInput => {
        nameInput.value = "";
    });
}

// Запуск при завантаженні
window.addEventListener('DOMContentLoaded', displayNorma);