import json
import os
import time
from config import HISTORY_FILE

def load_history():
    """Загружает историю обработанных файлов."""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(file_name, success=True):
    """Сохраняет файл в историю."""
    history_data = load_history()
    history_data.append({
        "file": file_name,
        "success": success,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

def file_already_processed(file_name):
    """Проверяет, был ли уже обработан файл."""
    history_data = load_history()
    return any(entry["file"] == file_name and entry["success"] for entry in history_data)
