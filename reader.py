
import json
import subprocess

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
    )
    out = result.stdout.strip()
    if not out:
        return []              # событий не найдено
    data = json.loads(out)
    return [data] if isinstance(data, dict) else data   # одно событие приходит как dict

if __name__ == "__main__":
    for e in get_events([41, 1001], hours=72):
        print(e["Time"], e["Id"], e["ProviderName"])
        print(e["Message"][:200], "\n")