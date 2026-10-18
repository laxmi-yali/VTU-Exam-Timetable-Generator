
from datetime import date, timedelta
from flask import Flask, render_template, request

app = Flask(__name__)

MAX_SEMESTERS = 20
MAX_SUBJECTS = 30
MAX_HOLIDAYS = 100
MAX_EXAMS_PER_DAY = 10


def generate_dates(start_date, end_date):
    """Generate all dates between the start and end dates."""
    dates = []
    current = start_date

    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)

    return dates


def is_valid_date(current_date, holidays):
    """Exclude Sundays and holidays."""
    return current_date.weekday() != 6 and current_date not in holidays


def generate_timetable(
    start_date,
    end_date,
    holidays,
    semesters,
    exams_per_day,
    time_slots,
    gap_days
):
    all_dates = generate_dates(start_date, end_date)

    valid_dates = [
        current_date
        for current_date in all_dates
        if is_valid_date(current_date, holidays)
    ]

    all_timetables = []

    # Generate a timetable for each semester and branch.
    for semester in semesters:
        timetable = []
        subjects = semester["subjects"]

        # Number of exam days required for this semester.
        required_days = (
            len(subjects) + exams_per_day - 1
        ) // exams_per_day

        # Each exam day is followed by the specified gap
        # in valid exam dates.
        required_dates = (
            (required_days - 1) * (gap_days + 1) + 1
            if required_days > 0
            else 0
        )

        if required_dates > len(valid_dates):
            raise ValueError(
                f"Not enough valid exam dates for "
                f"Semester {semester['number']} "
                f"({semester['branch']}). "
                f"Required: {required_dates}, "
                f"Available: {len(valid_dates)}."
            )

        for subject_index, subject in enumerate(subjects):
            exam_day_index = subject_index // exams_per_day
            slot_index = subject_index % exams_per_day

            date_index = exam_day_index * (gap_days + 1)
            exam_date = valid_dates[date_index]

            timetable.append({
                "date": exam_date.strftime("%d/%m/%Y"),
                "subject": subject,
                "semester": semester["number"],
                "branch": semester["branch"],
                "time_slot": time_slots[slot_index],
                "sort_date": exam_date
            })

        all_timetables.append({
            "number": semester["number"],
            "branch": semester["branch"],
            "exams": timetable
        })

    return all_timetables


@app.route("/", methods=["GET", "POST"])
def index():
    timetables = None
    error = None

    if request.method == "POST":
        try:
            # Read and validate the examination period.
            start_date = date.fromisoformat(
                request.form["start_date"].strip()
            )
            end_date = date.fromisoformat(
                request.form["end_date"].strip()
            )

            if start_date > end_date:
                raise ValueError(
                    "Start date must not be after end date."
                )

            # Read holidays in YYYY-MM-DD format.
            holiday_text = request.form.get(
                "holidays", ""
            ).strip()

            holiday_lines = [
                line.strip()
                for line in holiday_text.splitlines()
                if line.strip()
            ]

            if len(holiday_lines) > MAX_HOLIDAYS:
                raise ValueError(
                    f"Maximum {MAX_HOLIDAYS} holidays allowed."
                )

            holidays = set()

            for line in holiday_lines:
                try:
                    holidays.add(date.fromisoformat(line))
                except ValueError:
                    raise ValueError(
                        f"Invalid holiday date: {line}. "
                        "Use YYYY-MM-DD."
                    )

            # Read the number of semester/branch entries.
            total_semesters = int(
                request.form["total_semesters"]
            )

            if not 1 <= total_semesters <= MAX_SEMESTERS:
                raise ValueError(
                    f"Entries must be between 1 and "
                    f"{MAX_SEMESTERS}."
                )

            semesters = []
            semester_numbers = set()

            for i in range(1, total_semesters + 1):
                number = int(
                    request.form[f"sem_number_{i}"]
                )

                branch = request.form[
                    f"branch_{i}"
                ].strip()

                if number < 1:
                    raise ValueError(
                        "Semester numbers must be positive."
                    )

                if number in semester_numbers:
                    raise ValueError(
                        f"Semester number {number} is duplicated. "
                        "Use unique semester numbers."
                    )

                if not branch:
                    raise ValueError(
                        f"Enter a branch name for entry {i}."
                    )

                semester_numbers.add(number)

                subjects = [
                    subject.strip()
                    for subject in request.form[
                        f"subjects_{i}"
                    ].splitlines()
                    if subject.strip()
                ]

                if not 1 <= len(subjects) <= MAX_SUBJECTS:
                    raise ValueError(
                        f"Entry {i} must contain between 1 "
                        f"and {MAX_SUBJECTS} subjects."
                    )

                semesters.append({
                    "number": number,
                    "branch": branch,
                    "subjects": subjects
                })

            # Read exams per day.
            exams_per_day = int(
                request.form["exams_per_day"]
            )

            if not 1 <= exams_per_day <= MAX_EXAMS_PER_DAY:
                raise ValueError(
                    f"Exams per day must be between 1 and "
                    f"{MAX_EXAMS_PER_DAY}."
                )

            # Read time slots.
            time_slots = [
                slot.strip()
                for slot in request.form[
                    "time_slots"
                ].splitlines()
                if slot.strip()
            ]

            if len(time_slots) != exams_per_day:
                raise ValueError(
                    "Enter exactly one time slot for each "
                    "exam allowed per day."
                )

            # Read the gap between exam days.
            gap_days = int(request.form["gap_days"])

            if gap_days < 0:
                raise ValueError(
                    "Gap days cannot be negative."
                )

            # Generate the timetables.
            timetables = generate_timetable(
                start_date=start_date,
                end_date=end_date,
                holidays=holidays,
                semesters=semesters,
                exams_per_day=exams_per_day,
                time_slots=time_slots,
                gap_days=gap_days
            )

        except (ValueError, KeyError, TypeError) as exc:
            error = str(exc) or "Please check your input."

    return render_template(
        "index.html",
        timetables=timetables,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
