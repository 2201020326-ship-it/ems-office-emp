"""Compatibility timesheet service for FastAPI layer."""

from datetime import date, time
from datetime import datetime

from schemas.employee_schema import TimesheetResponse, WorkDetailCreate, WorkDetailResponse
from service.timesheet_service import delete_work_details as _delete_work_details
from service.timesheet_service import get_timesheets as _get_timesheets
from service.timesheet_service import submit_timesheet


def _parse_time_value(value: str | time) -> time:
    if isinstance(value, time):
        return value
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    raise ValueError("Invalid time value")


def _format_time_hh_mm(value: str | time) -> str:
    return _parse_time_value(value).strftime("%H:%M")


def create_work_detail(work_detail: WorkDetailCreate) -> WorkDetailResponse:
    slots = []
    for slot in work_detail.slots:
        slot_dict = slot.model_dump()
        # Submit only hours and minutes; core service normalizes it for DB TIME storage.
        slot_dict["start_time"] = (
            slot_dict["start_time"].strftime("%H:%M")
            if isinstance(slot_dict["start_time"], time)
            else slot_dict["start_time"]
        )
        slot_dict["end_time"] = (
            slot_dict["end_time"].strftime("%H:%M")
            if isinstance(slot_dict["end_time"], time)
            else slot_dict["end_time"]
        )
        slots.append(slot_dict)
    work_date = (work_detail.work_date or date.today()).isoformat()
    success, message = submit_timesheet(work_detail.employee_id, work_date, slots)
    if not success:
        raise ValueError(message)

    return WorkDetailResponse(
        success=True,
        message=message,
        employee_id=work_detail.employee_id,
        work_date=work_detail.work_date or date.today(),
        slots_saved=len(slots),
    )


def get_timesheets(employee_id: int) -> list[TimesheetResponse]:
    success, message, items = _get_timesheets(employee_id)
    if not success:
        raise ValueError(message)

    return [
        TimesheetResponse(
            id=item.id,
            employee_id=item.employee_id,
            work_date=datetime.strptime(item.work_date, "%Y-%m-%d").date() if isinstance(item.work_date, str) else item.work_date,
            slot_number=item.slot_number,
            start_time=_format_time_hh_mm(item.start_time),
            end_time=_format_time_hh_mm(item.end_time),
            description=item.description,
        )
        for item in items
    ]


def delete_work_detail(employee_id: int, work_date: str) -> dict[str, int | str | bool]:
    success, message, deleted_slots = _delete_work_details(employee_id, work_date)
    if not success:
        raise ValueError(message)

    return {
        "success": True,
        "message": message,
        "employee_id": employee_id,
        "work_date": work_date,
        "deleted_slots": deleted_slots,
    }
