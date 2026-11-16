# reader.py
import json
import re
import subprocess
from datetime import datetime


def get_events(event_ids, hours=24):
    ids = ",".join(str(i) for i in event_ids)
    ps = f"""
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $since = (Get-Date).AddHours(-{hours})
    Get-WinEvent -FilterHashtable @{{LogName='System'; Id={ids}; StartTime=$since}} -ErrorAction SilentlyContinue |
      Select-Object @{{n='Time';e={{$_.TimeCreated.ToString('o')}}}}, Id, ProviderName, Message |
      ConvertTo-Json
    """
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        capture_output=True, text=True, encoding="utf-8",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    out = result.stdout.strip()
    if not out:
        return []
    data = json.loads(out)
    return [data] if isinstance(data, dict) else data


def parse_bugcheck(message):
    m = re.search(r"(0x[0-9a-fA-F]+)\s*\(([^)]*)\)", message)
    if not m:
        return None
    return {
        "code": int(m.group(1), 16),
        "params": [p.strip() for p in m.group(2).split(",")],
    }

def group_incidents(events, window_seconds=120):
    """Группирует события 41 и 1001 в инциденты по близости по времени."""
    parsed = sorted(
        events,
        key=lambda e: datetime.fromisoformat(e["Time"][:26] + e["Time"][-6:]),
    )
    incidents = []
    for e in parsed:
        t = datetime.fromisoformat(e["Time"][:26] + e["Time"][-6:])
        if incidents and (t - incidents[-1]["last_time"]).total_seconds() <= window_seconds:
            incidents[-1]["events"].append(e)
            incidents[-1]["last_time"] = t
        else:
            incidents.append({"first_time": t, "last_time": t, "events": [e]})

    for inc in incidents:
        ids = {ev["Id"] for ev in inc["events"]}
        inc["type"] = "bsod" if 1001 in ids else "unexpected_shutdown"
    return incidents


if __name__ == "__main__":
    for e in get_events([41, 1001], hours=72):
        print(e["Time"], e["Id"], e["ProviderName"])
        print(e["Message"][:200], "\n")

        if e["Id"] == 1001:
            print(parse_bugcheck(e["Message"]))
            print()