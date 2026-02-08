import time

def log_event(event: str, data: dict):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {event}: {data}")
