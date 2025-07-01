import sys
import os
import threading
import subprocess
import importlib
import tkinter as tk
from tkinter import ttk, messagebox

import customtkinter as ctk
from gui import WhisperGUI
from cli_handler import process_files_cli
from updater import check_update


def ensure_whisper_ui():
    """
    Отображает модальное окно с индикатором установки openai-whisper
    и устанавливает пакет в фоне, если его нет.
    """
    try:
        import whisper
        return
    except ImportError:
        pass

    # создаём splash для установки
    splash = tk.Tk()
    splash.title("Установка зависимостей")
    splash.geometry("350x100")
    splash.resizable(False, False)

    lbl = tk.Label(splash, text="Устанавливаем openai-whisper...", anchor="center")
    lbl.pack(expand=True, pady=(20, 5))

    bar = ttk.Progressbar(splash, mode="indeterminate")
    bar.pack(fill="x", padx=20)
    bar.start(10)

    def worker():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
            lbl.config(text="Установка завершена.")
        except Exception as e:
            lbl.config(text=f"Ошибка установки: {e}")
        finally:
            bar.stop()
            splash.after(500, splash.destroy)

    threading.Thread(target=worker, daemon=True).start()
    splash.mainloop()


def check_updates_ui():
    """
    Отображает простое модальное окно tkinter для проверки обновлений.
    """
    result = {'value': None}

    splash = tk.Tk()
    splash.title("Проверка обновлений")
    splash.geometry("300x100")
    splash.resizable(False, False)

    lbl = tk.Label(splash, text="Идёт проверка обновлений...", anchor="center")
    lbl.pack(expand=True, pady=(20, 5))

    bar = ttk.Progressbar(splash, mode="indeterminate")
    bar.pack(fill="x", padx=20)
    bar.start(10)

    def worker():
        try:
            res = check_update()
        except Exception as e:
            res = e
        result['value'] = res
        splash.quit()

    threading.Thread(target=worker, daemon=True).start()

    splash.mainloop()
    try:
        bar.stop()
    except:
        pass
    splash.destroy()

    res = result.get('value')
    if isinstance(res, Exception):
        messagebox.showerror("Ошибка обновления", str(res))
    elif res is False:
        messagebox.showinfo("Обновления", "Обновлений нет")
    # при успешном обновлении check_update() завершит процесс


if __name__ == '__main__':
    # кириллица в консоли Windows
    if os.name == 'nt':
        os.system('chcp 65001 >nul')
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass

    # 1. Убедимся, что whisper установлен
    ensure_whisper_ui()

    # 2. CLI режим
    if '--cli' in sys.argv:
        process_files_cli()
        sys.exit(0)

    # 3. Проверка обновлений
    check_updates_ui()

    # 4. Запуск GUI
    app = WhisperGUI()
    app.mainloop()
