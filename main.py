import sys
import os
import threading
import subprocess
import importlib
import customtkinter as ctk
from gui import WhisperGUI
from cli_handler import process_files_cli
from updater import check_update

def ensure_whisper():
    """
    Проверяет, доступен ли модуль whisper.
    Если нет — показывает окно с прогресс-баром и устанавливает его.
    """
    try:
        importlib.import_module("whisper")
        return  # всё ок
    except ImportError:
        pass

    # Создаём окно-сплэш с прогрессбаром
    splash = ctk.CTk()
    splash.title("Установка зависимостей")
    splash.geometry("400x100")
    splash.resizable(False, False)

    label = ctk.CTkLabel(splash, text="Устанавливаем openai-whisper...\nПожалуйста, подождите")
    label.pack(pady=(20, 5))

    progress = ctk.CTkProgressBar(splash, orientation="horizontal", mode="indeterminate")
    progress.pack(fill="x", padx=20, pady=(0, 20))
    progress.start(10)

    def install():
        # Запускаем pip install внутри той же среды
        subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper"], check=True)
        # после установки можно закрыть сплэш
        splash.destroy()

    # Установка в фоне, чтобы не блокировать GUI-цикл
    threading.Thread(target=install, daemon=True).start()
    splash.mainloop()

if __name__ == '__main__':
    if os.name == 'nt':
        os.system('chcp 65001 >nul')
        sys.stdout.reconfigure(encoding='utf-8')

    # 1) Авто-установка whisper
    ensure_whisper()

    # 2) CLI-режим
    if '--cli' in sys.argv:
        process_files_cli()
    else:
        # 3) Авто-обновление
        try:
            check_update()
        except Exception:
            pass

        # 4) Запуск GUI
        app = WhisperGUI()
        app.mainloop()
