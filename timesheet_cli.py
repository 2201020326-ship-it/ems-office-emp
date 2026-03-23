"""CLI helper for submitting multiple timesheet slots."""

from datetime import date

from service.timesheet_service import submit_timesheet as submit_timesheet_batch


def submit_timesheet(emp_id: int) -> None:
    work_date = date.today().isoformat()
    print(f"Work date auto-set to: {work_date}")

    slots: list[dict[str, str]] = []

    while True:
        start_time = input("Start time (HH:MM): ").strip()
        end_time = input("End time (HH:MM): ").strip()
        description = input("Description: ").strip()

        slots.append(
            {
                "start_time": start_time,
                "end_time": end_time,
                "description": description,
            }
        )

        add_more = input("Add another slot? (y/n): ").strip().lower()
        if add_more != "y":
            break

    success, message = submit_timesheet_batch(emp_id, work_date, slots)
    if success:
        print("Timesheet submitted successfully!")
    else:
        print(f"Failed: {message}")
