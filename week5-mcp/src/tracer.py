import os
import json
from datetime import datetime
from src.constants import TRACE_COLOR, RESET, BOLD

LOG_FILE = 'logs/trace.log'


def ensure_log_dir():
    os.makedirs('logs', exist_ok=True)


def trace(agent: str, event: str, data: dict) -> None:
    ensure_log_dir()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = {
        'timestamp': timestamp,
        'agent': agent,
        'event': event,
        'data': data,
    }
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
    print(
        f'{TRACE_COLOR}[Trace] {timestamp} | '
        f'{BOLD}{agent}{RESET}{TRACE_COLOR} | '
        f'{event}{RESET}'
    )


def get_traces() -> list:
    ensure_log_dir()
    if not os.path.exists(LOG_FILE):
        return []
    traces = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                traces.append(json.loads(line))
    return traces
