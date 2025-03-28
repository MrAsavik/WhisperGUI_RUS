import os
import time
import threading
from cli_handler import process_files_cli
from config import OUTPUT_DIR

def auto_process_folder():
    """Автоматическая обработка файлов."""
    while True:
        files = [
            os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR)
            if f.endswith((".mp3", ".wav", ".mp4", ".mkv"))
        ]
        for file in files:
            print(f"🔄 Найден новый файл: {file}")
            process_files_cli(file)
        time.sleep(60)  # Проверять раз в минуту

def start_scheduler():
    """Запуск фонового потока с планировщиком."""
    thread = threading.Thread(target=auto_process_folder, daemon=True)
    thread.start()
