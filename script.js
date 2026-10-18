
const semesterCountInput = document.getElementById("total_semesters");
const semesterFields = document.getElementById("semesterFields");
const examsPerDayInput = document.getElementById("exams_per_day");
const timeSlotsInput = document.getElementById("time_slots");

function createSemesterFields() {
    const count = Number(semesterCountInput.value);

    semesterFields.replaceChildren();

    for (let i = 1; i <= count; i++) {
        const card = document.createElement("div");
        card.className = "semester-card";

        const heading = document.createElement("h3");
        heading.textContent = `Semester Entry ${i}`;
        card.appendChild(heading);

        addInput(
            card,
            `Semester Number`,
            `sem_number_${i}`,
            "number",
            String(i),
            true
        );

        addInput(
            card,
            "Branch / Course Name",
            `branch_${i}`,
            "text",
            "",
            true,
            "e.g. Computer Science"
        );

        const label = document.createElement("label");
        label.appendChild(
            document.createTextNode("Subject Names (one per line)")
        );

        const textarea = document.createElement("textarea");
        textarea.name = `subjects_${i}`;
        textarea.rows = 4;
        textarea.required = true;
        textarea.placeholder =
            "Mathematics\nComputer Networks\nDatabase Management";

        label.appendChild(textarea);
        card.appendChild(label);
        semesterFields.appendChild(card);
    }
}

function addInput(
    container,
    labelText,
    name,
    type,
    value,
    required,
    placeholder = ""
) {
    const label = document.createElement("label");
    label.appendChild(document.createTextNode(labelText));

    const input = document.createElement("input");
    input.type = type;
    input.name = name;
    input.value = value;
    input.required = required;

    if (type === "number") {
        input.min = "1";
        input.max = name.startsWith("sem_number_")
            ? "100"
            : "30";
    }

    input.placeholder = placeholder;
    label.appendChild(input);
    container.appendChild(label);
}

semesterCountInput.addEventListener(
    "input",
    createSemesterFields
);

examsPerDayInput.addEventListener("change", () => {
    const count = Number(examsPerDayInput.value);
    const slots = timeSlotsInput.value
        .split("\n")
        .filter(slot => slot.trim());

    if (count >= 1 && count <= 10 && slots.length !== count) {
        timeSlotsInput.setCustomValidity(
            `Enter exactly ${count} time slots.`
        );
    } else {
        timeSlotsInput.setCustomValidity("");
    }
});

timeSlotsInput.addEventListener("input", () => {
    timeSlotsInput.setCustomValidity("");
});

document.getElementById("timetableForm").addEventListener(
    "submit",
    event => {
        const start = document.querySelector(
            '[name="start_date"]'
        ).value;

        const end = document.querySelector(
            '[name="end_date"]'
        ).value;

        if (start && end && start > end) {
            event.preventDefault();
            alert("Start date must not be after end date.");
        }

        const count = Number(examsPerDayInput.value);
        const slots = timeSlotsInput.value
            .split("\n")
            .filter(slot => slot.trim());

        if (count >= 1 && count <= 10 && slots.length !== count) {
            event.preventDefault();
            alert(
                `Please enter exactly ${count} time slots.`
            );
        }
    }
);

createSemesterFields();
