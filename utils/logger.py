import datetime

def log(msg):
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] {msg}", flush=True)
