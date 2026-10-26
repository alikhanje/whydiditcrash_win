# main.py
from reader import get_events, parse_bugcheck
from stop_codes import STOP_CODES


def build_report(event):
    info = parse_bugcheck(event["Message"])
    when = event["Time"][:19].replace("T", " ")

    if info is None:
        return f"{when}: найден сбой, но код ошибки разобрать не удалось."

    code = info["code"]
    entry = STOP_CODES.get(code)

    lines = [f"Время: {when}", f"Код ошибки: 0x{code:X}"]
    if entry is None:
        lines.append("Этого кода пока нет в справочнике.")
    else:
        lines.append(f"Название: {entry['name']}")
        lines.append(f"Что произошло: {entry['meaning']}")
        lines.append("Возможные причины: " + "; ".join(entry["causes"]))
        lines.append("Что проверить: " + "; ".join(entry["check"]))
    return "\n".join(lines)


if __name__ == "__main__":
    crashes = get_events([1001], hours=72)
    if not crashes:
        print("Синих экранов за этот период не найдено.")
    for crash in crashes:
        print(build_report(crash))
        print()