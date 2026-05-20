function assert(condition, message) {
    if (!condition) {
        console.error("FAIL:", message);
        throw new Error(message);
    } else {
        console.log("PASS:", message);
    }
}

function testStructure() {
    console.log("=== TEST: STRUCTURE ===");

    const form = document.querySelector("form");
    const q1 = document.querySelectorAll('input[name="q1"]');
    const q2 = document.querySelectorAll('input[name="q2"]');
    const gender = document.querySelectorAll('input[name="gender"]');
    const inputs = document.querySelectorAll(".data-inputs input");
    const btn = document.querySelector(".btn");

    assert(form !== null, "Форма існує");
    assert(q1.length === 4, "Q1 має 4 варіанти");
    assert(q2.length === 3, "Q2 має 3 варіанти");
    assert(gender.length === 2, "Gender має 2 варіанти");
    assert(inputs.length === 3, "Є 3 input поля");
    assert(btn !== null, "Кнопка існує");
}

function testInputs() {
    console.log("=== TEST: INPUTS ===");

    const inputs = document.querySelectorAll(".data-inputs input");

    inputs.forEach((input, i) => {
        assert(
            input.type === "number",
            `Поле ${i + 1} повинно бути type="number"`
        );

        input.value = "123";

        assert(
            !isNaN(input.value),
            `Поле ${i + 1} приймає число`
        );
    });
}

function testValidation() {
    console.log("=== TEST: VALIDATION ===");

    const inputs = document.querySelectorAll(".data-inputs input");

    inputs.forEach((input, i) => {
        input.value = "";

        assert(
            input.checkValidity() === false,
            `Поле ${i + 1} не повинно бути валідним без значення`
        );
    });
}

function testSubmit() {
    console.log("=== TEST: SUBMIT ===");

    const form = document.querySelector("form");
    const btn = document.querySelector(".btn");

    let submitted = false;

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        submitted = true;
    });

    btn.click();

    assert(
        submitted === false,
        "Форма не повинна відправлятись без валідних даних"
    );
}

function runAllTests() {
    console.log("RUN ALL TESTS\n");

    testStructure();
    testInputs();
    testValidation();
    testSubmit();

    console.log("\n ALL TESTS PASSED");
}

window.onload = runAllTests;