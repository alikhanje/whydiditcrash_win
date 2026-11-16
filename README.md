# WhyDidItCrash

Windows tool that finds out why your PC crashed. It reads the Windows
Event Log, detects blue screens (BSOD) and unexpected shutdowns, and
explains the stop code in plain language.

## Features

- Reads crash events (ID 41 and 1001) from the Windows System event log
- Parses the bugcheck stop code and its parameters
- Groups related events into incidents (BSOD vs. shutdown without a blue screen)
- Explains known stop codes: what happened, likely causes, what to check

## Requirements

- Windows 10/11
- Python 3.12+

## Quick start

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python main.py

## Tests

    python -m pytest

## Project structure

    backend/    event reader, parser, incident grouping, stop code reference
    tests/      pytest tests
    main.py     entry point, prints the crash report

## Download

Get the latest `WhyDidItCrash.exe` from the [Releases](../../releases) page
and run it. No installation or Python required.


## How to use

1. Run `WhyDidItCrash.exe`
2. Choose a period and press **Check**
3. Select an incident in the list to read the explanation




## Roadmap

- [ ] AI explanations for stop codes missing from the reference
- [ ] System metrics (CPU, RAM) before a crash
- [ ] Web dashboard