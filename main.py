# main.py
import ctypes
import time

from backend.db import init_db, save_incident
from backend.reader import get_events, group_incidents, parse_bugcheck
from backend.report import build_report
from backend.stop_codes import STOP_CODES


def store_incident(incident):
    """Достаёт из инцидента нужные поля и сохраняет в базу. True, если инцидент новый."""
    code, name = None, None
    if incident["type"] == "bsod":
        crash = next(ev for ev in incident["events"] if ev["Id"] == 1001)
        info = parse_bugcheck(crash["Message"])
        if info:
            code = info["code"]
            entry = STOP_CODES.get(code)
            name = entry["name"] if entry else None
    return save_incident(incident["first_time"], incident["type"], code, name)


def show_popup(title, text):
    """Показывает стандартное окно Windows с текстом."""
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)


def wait_for_db(attempts=10, delay=15):
    """После включения компьютера база стартует не сразу, поэтому пробуем несколько раз."""
    for _ in range(attempts):
        try:
            init_db()
            return True
        except Exception:
            time.sleep(delay)
    return False


if __name__ == "__main__":
    if not wait_for_db():
        show_popup("WhyDidItCrash", "Не удалось подключиться к базе данных. Запущен ли Docker?")
        raise SystemExit(1)

    events = get_events([41, 1001], hours=720)
    incidents = group_incidents(events)

    new_reports = []
    for incident in incidents:
        if store_incident(incident):
            new_reports.append(build_report(incident))

    if new_reports:
        show_popup(
            f"WhyDidItCrash: найдено новых вылетов: {len(new_reports)}",
            "\n\n".join(new_reports[-3:]),
        )