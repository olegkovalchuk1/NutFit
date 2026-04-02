const grid = document.getElementById("grid");
let saved = JSON.parse(localStorage.getItem("tracker")) || [];

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth();

const firstDay = new Date(year, month, 1).getDay();
const offset = (firstDay + 6) % 7;

const daysInMonth = new Date(year, month + 1, 0).getDate();

for (let i = 0; i < offset; i++) {
    let empty = document.createElement("div");
    grid.appendChild(empty);
}

for (let i = 1; i <= daysInMonth; i++) {
    let cell = document.createElement("div");
    cell.classList.add("cell");

    if (saved[i]) cell.classList.add("active");

    if (i === today.getDate()) {
        cell.classList.add("today");
    }

    cell.onclick = () => {
        cell.classList.toggle("active");
        saved[i] = cell.classList.contains("active");
        localStorage.setItem("tracker", JSON.stringify(saved));
    };

    grid.appendChild(cell);
}

function resetGrid() {
    localStorage.removeItem("tracker");
    location.reload();
}

function toggle(el) {
    const content = el.parentElement.querySelector(".hidden");

    content.style.display =
        content.style.display === "block" ? "none" : "block";
}