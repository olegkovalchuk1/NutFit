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

// ================= ВІДКРИТТЯ БЛОКІВ =================
function toggleBlock(header) {
    const block = header.parentElement;
    block.classList.toggle("active");
}

// ================= ДАНІ =================
const notifications = [];

// ================= СТВОРЕННЯ КАРТКИ =================
function createCard(n) {
    const el = document.createElement("div");
    el.className = "card" + (n.read ? " read" : "");
    el.textContent = n.text;

    el.onclick = () => {
        n.read = true;
        renderNotifications();
    };

    return el;
}

// ================= СТВОРЕННЯ СПОВІЩЕННЯ =================
function createNotification(text, isImportant = false) {
    const notif = {
        id: Date.now(),
        text: text,
        important: isImportant,
        read: false
    };

    notifications.unshift(notif);
    renderNotifications();
}

// ================= РЕНДЕР =================
function renderNotifications() {
    const allBlock = document.getElementById("all");
    const importantBlock = document.getElementById("important");
    const unreadBlock = document.getElementById("unread");

    if (!allBlock || !importantBlock || !unreadBlock) {
        console.error("❌ Не знайдені блоки");
        return;
    }

    allBlock.innerHTML = "";
    importantBlock.innerHTML = "";
    unreadBlock.innerHTML = "";

    notifications.forEach(n => {
        // УСІ
        allBlock.appendChild(createCard(n));

        // ВАЖЛИВІ
        if (n.important) {
            importantBlock.appendChild(createCard(n));
        }

        // НЕПРОЧИТАНІ
        if (!n.read) {
            unreadBlock.appendChild(createCard(n));
        }
    });
}

// ================= ТАЙМЕР СПОВІЩЕНЬ =================
function startNotifications() {
    setInterval(() => {
        const now = new Date();
        const h = now.getHours();
        const m = now.getMinutes();

        // тільки на початку години
        if (m !== 0) return;

        if (h === 8) createNotification("Сніданок 🍳");
        if (h === 13) createNotification("Обід 🍲");
        if (h === 19) createNotification("Вечеря 🍽");
        if (h === 17) createNotification("Тренування 🏋️");

        // 💧 важливі
        if (h % 3 === 0) {
            createNotification("Пора пити воду 💧", true);
        }

    }, 60000);
}

// ================= СТАРТ =================
document.addEventListener("DOMContentLoaded", () => {

    // тестові (щоб одразу було видно)
    createNotification("Сніданок 🍳");
    createNotification("Пора пити воду 💧", true);
    createNotification("Тренування 🏋️");

    startNotifications();
});