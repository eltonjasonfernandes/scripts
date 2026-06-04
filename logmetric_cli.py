#!/usr/bin/env python3
import re
import sys
import time
import threading
from collections import deque, defaultdict

from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console

# -----------------------
# CONFIG
# -----------------------
ROLLING_LINES = 15
DEDUP_WINDOW = 5

console = Console()

# -----------------------
# LOG GROUPS
# -----------------------
GROUPS = ["INCIDENT", "WARN", "INFO", "HTTP 4XX", "HTTP 5XX"]

buffers = {g: deque(maxlen=ROLLING_LINES) for g in GROUPS}

# dedup_cache stores a deque of timestamps for each unique fingerprint
dedup_cache = defaultdict(lambda: {"timestamps": deque()})

pause_event = threading.Event()
pause_event.set()

# -----------------------
# CLASSIFICATION
# -----------------------
def classify(line: str):
    u = line.upper()

    # INCIDENT = CRITICAL + ERROR
    if re.search(r"CRITICAL|FATAL", u) or re.search(r"\bERROR\b", u):
        return "INCIDENT"

    if re.search(r"WARN(ING)?", u):
        return "WARN"

    if "HTTP" in u:
        if re.search(r" 4\d\d", u):
            return "HTTP 4XX"
        if re.search(r" 5\d\d", u):
            return "HTTP 5XX"

    if "INFO" in u or "NOTICE" in u:
        return "INFO"

    return None

# -----------------------
# FINGERPRINT
# -----------------------
def fingerprint(line: str):
    # remove digits to avoid counting unique IDs separately
    return re.sub(r"\d{1,6}", "", line).strip()

# -----------------------
# DEDUP WITH COUNTS (rolling window)
# -----------------------
def dedup(line: str):
    sig = fingerprint(line)
    now = time.time()

    entry = dedup_cache[sig]
    q = entry["timestamps"]

    # append current timestamp
    q.append(now)

    # remove timestamps older than DEDUP_WINDOW
    while q and now - q[0] > DEDUP_WINDOW:
        q.popleft()

    count = len(q)

    if count > 1:
        return f"{line} (x{count} in last {DEDUP_WINDOW}s)", count
    return line, 1

# -----------------------
# FILE FOLLOW
# -----------------------
def tail(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)
        while True:
            pause_event.wait()
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line.strip()

# -----------------------
# DASHBOARD
# -----------------------
def render():
    layout = Layout()

    layout.split_column(
        Layout(name="INCIDENT", size=12),   # BIG TOP PANEL
        Layout(name="WARN"),
        Layout(name="INFO"),
        Layout(name="HTTP 4XX"),
        Layout(name="HTTP 5XX"),
    )

    for g in GROUPS:
        lines = list(buffers[g])

        if g == "INCIDENT":
            color = "red"
        elif g == "WARN":
            color = "yellow"
        elif g in ("HTTP 4XX", "HTTP 5XX"):
            color = "magenta"
        else:
            color = "blue"

        layout[g].update(
            Panel(
                "\n".join(lines) if lines else " ",
                title=f"{g} ({len(lines)} lines)",
                border_style=color
            )
        )

    return layout

# -----------------------
# KEY LISTENER
# -----------------------
def key_listener():
    import sys, termios, tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    try:
        while True:
            ch = sys.stdin.read(1)
            if ch.lower() == "p":
                if pause_event.is_set():
                    pause_event.clear()
                else:
                    pause_event.set()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# -----------------------
# MAIN LOOP
# -----------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: logmetric_cli.py <logfile>")
        sys.exit(1)

    file_path = sys.argv[1]

    console.print(f"🚀 Observability stream: {file_path}")
    console.print("Press 'p' to pause/resume")

    threading.Thread(target=key_listener, daemon=True).start()

    with Live(render(), refresh_per_second=3, console=console, screen=True) as live:
        for line in tail(file_path):
            group = classify(line)
            if not group:
                continue

            deduped, count = dedup(line)
            if not deduped:
                continue

            buffers[group].append(deduped)
            live.update(render())

if __name__ == "__main__":
    main()
