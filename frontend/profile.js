document.getElementById("golovna").addEventListener("click", function () {
    window.location.href = "main.html"; // інша сторінка
});

document.getElementById("uvijty").addEventListener("click", function () {
    window.location.href = "login.html"; // інша сторінка
});

document.getElementById("osobistiy-kabinet").addEventListener("click", function () {
    window.location.href = "profile.html"; // інша сторінка
});

document.getElementById("spovishennya").addEventListener("click", function () {
    window.location.href = "notifications.html"; // інша сторінка
});


// --- 1. ЗАВАНТАЖЕННЯ СЕКЦІЙ ---
function loadSection(page) {
    fetch(page)
        .then(response => response.text())
        .then(data => {
            const content = document.getElementById("content");
            content.innerHTML = data;

            // Запускаємо логіку залежно від завантаженої сторінки
            if (page === 'recipes.html') initRecipes();
            if (page === 'exercise.html') initExercises();
            if (page === 'test.html') console.log("Секцію ТЕСТ завантажено");
        })
        .catch(error => console.error("Помилка завантаження:", error));
}

// --- 2. ГЛОБАЛЬНЕ ДЕЛЕГУВАННЯ ПОДІЙ ---
// Це змушує JS працювати у завантажених файлах
document.addEventListener('click', function (e) {
    // Стаканчики з водою (recipes.html)
    if (e.target.classList.contains('cup')) {
        handleWaterClick(e.target);
    }

    // Кнопка завершення тесту (test.html)
    if (e.target.id === 'finishTestBtn') {
        calculateAndSaveNorma();
    }

    // Кнопки розрахунку з'їденого (recipes.html)
    if (e.target.classList.contains('calculate-btn')) {
        calculateTotal();
    }
});

// --- 3. ЛОГІКА ТЕСТУ ---
function calculateAndSaveNorma() {
    const age = parseFloat(document.getElementById('age')?.value);
    const height = parseFloat(document.getElementById('height')?.value);
    const weight = parseFloat(document.getElementById('weight')?.value);
    const genderEl = document.querySelector('input[name="gender"]:checked');
    const activityEl = document.querySelector('input[name="activity"]:checked');
    const goalEl = document.querySelector('input[name="goal"]:checked');

    if (!age || !height || !weight || !genderEl || !activityEl || !goalEl) {
        alert("Будь ласка, заповніть всі поля тесту!");
        return;
    }

    let bmr = (10 * weight) + (6.25 * height) - (5 * age);
    bmr = (genderEl.value === 'male') ? bmr + 5 : bmr - 161;
    let totalCalories = bmr * parseFloat(activityEl.value);

    if (goalEl.value === 'lose') totalCalories -= 300;
    if (goalEl.value === 'gain') totalCalories += 300;

    localStorage.setItem('normaCalories', Math.round(totalCalories));
    localStorage.setItem('normaProteins', Math.round((totalCalories * 0.3) / 4));
    localStorage.setItem('normaFats', Math.round((totalCalories * 0.3) / 9));
    localStorage.setItem('normaCarbs', Math.round((totalCalories * 0.4) / 4));

    alert("Дані збережено!");
    loadSection('recipes.html'); // Перехід після тесту
}

// --- 4. ЛОГІКА РЕЦЕПТІВ ТА ВОДИ ---
function initRecipes() {
    displayNorma();
}

function handleWaterClick(clickedCup) {
    const cups = document.querySelectorAll('.cup');
    const index = [...cups].indexOf(clickedCup);
    const isActive = clickedCup.classList.contains('active');

    cups.forEach((cup, i) => {
        cup.classList.toggle('active', !isActive && i <= index);
    });
}

function displayNorma() {
    document.getElementById('norma-calories-display').innerText = (localStorage.getItem('normaCalories') || 0) + " ккал";
    document.getElementById('norma-proteins-display').innerText = (localStorage.getItem('normaProteins') || 0) + " г";
    document.getElementById('norma-fats-display').innerText = (localStorage.getItem('normaFats') || 0) + " г";
    document.getElementById('norma-carbs-display').innerText = (localStorage.getItem('normaCarbs') || 0) + " г";
}

function calculateTotal() {
    const categories = [
        { class: 'input-calories', id: 'total-calories', unit: ' ккал' },
        { class: 'input-proteins', id: 'total-proteins', unit: ' г' },
        { class: 'input-fats', id: 'total-fats', unit: ' г' },
        { class: 'input-carbs', id: 'total-carbs', unit: ' г' }
    ];

    categories.forEach(cat => {
        const inputs = document.querySelectorAll('.' + cat.class);
        const display = document.getElementById(cat.id);
        let current = parseFloat(display.innerText) || 0;
        let added = 0;
        inputs.forEach(input => {
            added += parseFloat(input.value) || 0;
            input.value = "";
        });
        display.innerText = Math.round(current + added) + cat.unit;
    });
}

// Пошук рецептів
function filterRecipes() {
    const input = document.getElementById('recipeSearch')?.value.toLowerCase() || "";
    const grids = document.querySelectorAll('.recipe-grid');

    grids.forEach(grid => {
        const recipes = grid.querySelectorAll('.recipe-card');
        let hasVisible = false;

        recipes.forEach(recipe => {
            const title = recipe.querySelector('.recipe-title')?.innerText.toLowerCase() || "";

            if (title.includes(input)) {
                recipe.style.display = "block";
                hasVisible = true;
            } else {
                recipe.style.display = "none";
            }
        });

        const section = grid.closest('section');

        if (hasVisible) {
            grid.style.display = "grid";
            if (section) section.style.display = "";
        } else {
            grid.style.display = "none";
            if (section) section.style.display = "none";
        }
    });
}

// --- 5. ЛОГІКА ТРЕНУВАНЬ (КАЛЕНДАР) ---
function initExercises() {
    const grid = document.getElementById("grid");
    if (!grid) return;
    grid.innerHTML = ""; 
    
    let saved = JSON.parse(localStorage.getItem("tracker")) || [];
    const today = new Date();
    const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
    const offset = (new Date(today.getFullYear(), today.getMonth(), 1).getDay() + 6) % 7;

    for (let i = 0; i < offset; i++) grid.appendChild(document.createElement("div"));

    for (let i = 1; i <= daysInMonth; i++) {
        let cell = document.createElement("div");
        cell.classList.add("cell");
        if (saved[i]) cell.classList.add("active");
        if (i === today.getDate()) cell.classList.add("today");

        cell.onclick = () => {
            cell.classList.toggle("active");
            saved[i] = cell.classList.contains("active");
            localStorage.setItem("tracker", JSON.stringify(saved));
        };
        grid.appendChild(cell);
    }
}