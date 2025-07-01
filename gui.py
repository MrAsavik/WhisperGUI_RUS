import customtkinter as ctk
import threading
import os
from tkinter import filedialog, messagebox
import psutil

from cli_handler import process_files_cli
from config import DEFAULT_MODEL, DEFAULT_LANGUAGE, OUTPUT_FORMATS
from power import prevent_sleep, allow_sleep

from ui import build_ui
from monitor import start_cpu_monitor
from log_utils import log, dev_log
from ui_utils import bind_copy
from handlers import kill_process_tree
from updater import CURRENT_VERSION



class WhisperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Whisper GUI Расширенный")
        self.geometry("900x700")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # 🧠 Состояния
        self.selected_files = []
        self.output_dir = ""
        self.current_process = None

        self.model_var = ctk.StringVar(value=DEFAULT_MODEL)
        self.language_var = ctk.StringVar(value=DEFAULT_LANGUAGE)
        self.selected_formats = {fmt: ctk.BooleanVar(value=True) for fmt in OUTPUT_FORMATS}
        self.turbo_var = ctk.BooleanVar(value=False)
        self.progress_var = ctk.DoubleVar()
        self.log_messages = []
        

        # 📦 Интерфейс
        build_ui(self)
        # внизу правого угла — версия приложения
        self.version_label = ctk.CTkLabel(
            self,
            text=f"v{CURRENT_VERSION}",
            text_color="gray",
            fg_color=None
        )
        self.version_label.place(
            relx=1.0, rely=1.0,    # правый нижний угол окна
            x=-10, y=-10,          # отступ 10px от границ
            anchor="se"            # South-East (юго-восток)
        )


    def clear_file_list(self):
        self.selected_files.clear()
        self.file_label.configure(text="Файлы не выбраны")
        self.process_button.configure(state="disabled")
        log(self, "🗑️ Список файлов очищен.")

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Аудио и видео", "*.wav *.mp3 *.mp4 *.mkv *.m4a *.aac *.ogg")])
        if files:
            added = 0
            for f in files:
                if not os.path.exists(f):
                    log(self, f"⚠️ Файл не найден: {f}")
                    continue
                if f not in self.selected_files:
                    self.selected_files.append(f)
                    added += 1


            self.file_label.configure(text=f"Выбрано файлов: {len(self.selected_files)}")
            self.process_button.configure(state="normal")
            log(self, f"📌 Добавлено файлов: {added}")
            for path in files:
                log(self, f"  ➤ {os.path.basename(path)} ({os.path.dirname(path)})")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            log(self, f"📁 Папка сохранения вручную выбрана: {self.output_dir}")

    def process_files(self):
        
        if self.selected_files:
            self.progress_var.set(0)
            self.process_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            threading.Thread(target=self.run_processing, daemon=True).start()

    def run_processing(self):
        model = self.model_var.get()
        language = self.language_var.get().lower()
        formats = [fmt for fmt, var in self.selected_formats.items() if var.get()]
        threads = os.cpu_count() if self.turbo_var.get() else None

        try:
            cpu_load = psutil.cpu_percent(interval=1)
            if cpu_load > 90:
                log(self, f"⚠️ Предупреждение: высокая загрузка CPU ({cpu_load}%).")

            prevent_sleep()
            log(self, "🔋 Блокировка сна активирована.")
            log(self, "🚀 Начата обработка файлов...")
            if threads:
                log(self, f"🚀 Turbo-режим активен: потоков = {threads}")

            self.current_process = process_files_cli(
                self.selected_files,
                model=model,
                language=language,
                formats=formats,
                threads=threads
            )

            start_cpu_monitor(self)

            for line in self.current_process.stdout:
                line = line.strip()
                dev_log(self, line)
                if "Ошибка" in line or "error" in line.lower():
                    log(self, "❌ " + line)
                elif "Transcribing" in line or "Saved" in line:
                    log(self, "📄 " + line)

            process = self.current_process
            self.current_process = None
            if process:
                process.wait()
                if process.returncode != 0:
                    log(self, f"❌ Процесс завершился с ошибкой (код: {process.returncode})")
                log(self, "✅ Обработка завершена.")
        except Exception as e:
            log(self, f"❌ Ошибка: {e}")
        finally:
            self.process_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.progress_var.set(1.0)
            allow_sleep()
            log(self, "🌙 Сон снова разрешён.")

    def stop_process(self):
        if self.current_process:
            pid = self.current_process.pid
            kill_process_tree(pid)
            log(self, "🛑 Процесс полностью остановлен.")
            self.current_process = None
        else:
            log(self, "⚠️ Нет активного процесса.")

    def on_close(self):
        if self.current_process:
            if not messagebox.askyesno("Подтверждение", "🚧 Идёт распознавание.\nВыйти и прервать процесс?"):
                return
            else:
                self.stop_process()
        log(self, "Закрытие приложения...")
        self.destroy()


if __name__ == "__main__":
    app = WhisperGUI()
    app.mainloop()
