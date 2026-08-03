import os
import json
from datetime import datetime
from src.constants import HOOK_COLOR, RESET, BOLD


LOG_FILE = 'logs/tool_calls.log'


def ensure_log_dir():
    os.makedirs('logs', exist_ok=True)


def pre_tool_hook(tool_name: str, tool_args: dict) -> dict:
    ensure_log_dir()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = {
        'timestamp': timestamp,
        'event': 'tool_call',
        'tool': tool_name,
        'args': tool_args,
    }
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')

    print(
        f'{HOOK_COLOR}[Hook] {timestamp} | '
        f'Calling: {BOLD}{tool_name}{RESET}{HOOK_COLOR} '
        f'args: {tool_args}{RESET}'
    )
    return log_entry


def post_tool_hook(tool_name: str, result: str) -> None:
    ensure_log_dir()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = {
        'timestamp': timestamp,
        'event': 'tool_result',
        'tool': tool_name,
        'result_preview': result[:200],
    }
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')

    preview = result[:100]
    print(
        f'{HOOK_COLOR}[Hook] {timestamp} | '
        f'{BOLD}{tool_name}{RESET}{HOOK_COLOR} '
        f'completed. Preview: {preview}...{RESET}'
    )


def get_logs() -> list:
    ensure_log_dir()
    if not os.path.exists(LOG_FILE):
        return []
    logs = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                logs.append(json.loads(line))
    return logs
