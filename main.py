# main.py
from reader import get_events, parse_bugcheck, group_incidents
from stop_codes import STOP_CODES


def build_report(incident):
    when = incident["first_time"].strftime("%Y-%m-%d %H:%M:%S")

    if incident["type"] == "unexpected_shutdown":
        return (
            f"Время: {when}\n"
            "Тип: неожиданное выключение или перезагрузка без синего экрана.\n"
            "Что это значит: компьютер выключился, не успев записать данные о сбое. "
            "Так бывает при потере питания, зависании с принудительным выключением "
            "или перегреве.\n"
            "Что проверить: питание и блок питания, температуру процессора и видеокарты, "
            "не нажималась ли кнопка питания."
        )

    crash = next(ev for ev in incident["events"] if ev["Id"] == 1001)
    info = parse_bugcheck(crash["Message"])
    if info is None:
        return f"Время: {when}\nТип: синий экран, но код ошибки разобрать не удалось."

    code = info["code"]
    entry = STOP_CODES.get(code)
    lines = [f"Время: {when}", "Тип: синий экран", f"Код ошибки: 0x{code:X}"]
    if entry is None:
        lines.append("Этого кода пока нет в справочнике.")
    else:
        lines.append(f"Название: {entry['name']}")
        lines.append(f"Что произошло: {entry['meaning']}")
        lines.append("Возможные причины: " + "; ".join(entry["causes"]))
        lines.append("Что проверить: " + "; ".join(entry["check"]))
    return "\n".join(lines)


if __name__ == "__main__":
    events = get_events([41, 1001], hours=72)
    incidents = group_incidents(events)
    if not incidents:
        print("Вылетов за этот период не найдено.")
    for inc in incidents:
        print(build_report(inc))
        print()