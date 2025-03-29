import customtkinter as ctk
import threading
from tkinter import filedialog, scrolledtext
from cli_handler import process_files_cli
from config import DEFAULT_MODEL, DEFAULT_LANGUAGE, OUTPUT_FORMATS
from power import prevent_sleep, allow_sleep

import os

class WhisperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_process = None

        self.title("Whisper GUI Расширенный")
        self.geometry("900x700")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Переменные состояния ---
        self.selected_files = []
        self.output_dir = ""
        self.model_var = ctk.StringVar(value=DEFAULT_MODEL)
        self.language_var = ctk.StringVar(value=DEFAULT_LANGUAGE)
        self.selected_formats = {fmt: ctk.BooleanVar(value=True) for fmt in OUTPUT_FORMATS}
        self.progress_var = ctk.DoubleVar()
        self.log_messages = []

        self.create_widgets()

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill='both')

        self.main_tab = self.tabview.add("Главная")
        self.settings_tab = self.tabview.add("Настройки")
        self.dev_tab = self.tabview.add("Разработчику")

        self.clear_files_button = ctk.CTkButton(self.main_tab, text="Очистить список файлов", command=self.clear_file_list)
        self.clear_files_button.pack(pady=5)

        self.create_main_tab()
        self.create_settings_tab()
        self.create_dev_tab()

    def create_main_tab(self):
        self.file_label = ctk.CTkLabel(self.main_tab, text="Файлы не выбраны")
        self.file_label.pack(pady=10)

        self.select_button = ctk.CTkButton(self.main_tab, text="Выбрать файлы", command=self.select_files)
        self.select_button.pack(pady=5)

        self.process_button = ctk.CTkButton(self.main_tab, text="Распознать", command=self.process_files, state="disabled")
        self.process_button.pack(pady=5)

        self.stop_button = ctk.CTkButton(self.main_tab, text="Стоп", command=self.stop_process, fg_color="red", state="disabled")
        self.stop_button.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.main_tab, variable=self.progress_var, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_var.set(0)

        self.log_text_main = scrolledtext.ScrolledText(self.main_tab, wrap='word', width=80, height=10)
        self.log_text_main.pack(pady=10)
        self.bind_copy(self.log_text_main)

        self.clear_log_button = ctk.CTkButton(self.main_tab, text="Очистить лог", command=self.clear_log)
        self.clear_log_button.pack(pady=5)

    def create_settings_tab(self):
        ctk.CTkLabel(self.settings_tab, text="Модель Whisper:").pack(pady=5)
        ctk.CTkOptionMenu(self.settings_tab, values=["tiny", "small", "medium", "large"], variable=self.model_var).pack()

        ctk.CTkLabel(self.settings_tab, text="Язык:").pack(pady=5)
        ctk.CTkOptionMenu(self.settings_tab, values=["Russian", "English", "Auto"], variable=self.language_var).pack()

        ctk.CTkLabel(self.settings_tab, text="Форматы вывода:").pack(pady=5)
        for fmt, var in self.selected_formats.items():
            ctk.CTkCheckBox(self.settings_tab, text=f"{fmt.upper()} формат", variable=var).pack(anchor='w', padx=20)

        ctk.CTkButton(self.settings_tab, text="Выбрать папку для сохранения", command=self.select_folder).pack(pady=10)

    def create_dev_tab(self):
        self.log_text_dev = scrolledtext.ScrolledText(self.dev_tab, wrap='word', width=110, height=35)
        self.log_text_dev.pack(pady=10, padx=10, expand=True, fill='both')
        self.bind_copy(self.log_text_dev)

    def bind_copy(self, widget):
        """Позволяет копировать текст по Ctrl+C и Ctrl+С (английская и русская раскладки)"""
        def on_ctrl_key(event):
            if event.state & 0x4:  # Ctrl зажат
                if event.keysym.lower() in ("c", "с"):  # латинская и русская
                    widget.event_generate("<<Copy>>")

        widget.bind("<KeyPress>", on_ctrl_key)




    def clear_file_list(self):
        self.selected_files.clear()
        self.file_label.configure(text="Файлы не выбраны")
        self.process_button.configure(state="disabled")
        self.log("🗑️ Список файлов очищен.")

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Аудио и видео", "*.wav *.mp3 *.mp4 *.mkv *.m4a *.aac *.ogg")]
        )
        if files:
            new_files = list(files)
            added = 0
            for f in new_files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
                    added += 1
            self.file_label.configure(text=f"Выбрано файлов: {len(self.selected_files)}")
            self.process_button.configure(state="normal")
            self.log(f"📌 Добавлено файлов: {added}")
            for path in new_files:
                self.log(f"  ➤ {os.path.basename(path)} ({os.path.dirname(path)})")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.log(f"📁 Папка сохранения вручную выбрана: {self.output_dir}")
    

    def process_files(self):
        if self.selected_files:
            self.progress_var.set(0)
            self.process_button.configure(state="disabled")
            self.stop_button.configure(state="normal")

            thread = threading.Thread(target=self.run_processing)
            thread.start()

    def run_processing(self):
        model = self.model_var.get()
        language = self.language_var.get().lower()
        formats = [fmt for fmt, var in self.selected_formats.items() if var.get()]

        try:
            prevent_sleep()
            self.log("🔋 Блокировка сна активирована.")

            
            self.log("🚀 Начата обработка файлов...")


            self.current_process = process_files_cli(
                self.selected_files,
                model=model,
                language=language,
                formats=formats
            )

            for line in self.current_process.stdout:
                line = line.strip()
                self.dev_log(line)
                if "Ошибка" in line or "error" in line.lower():
                    self.log("❌ " + line)
                elif "Transcribing" in line or "Saved" in line:
                    self.log("📄 " + line)

            self.current_process.wait()
            self.current_process = None
            self.log("✅ Обработка завершена.")
        except Exception as e:
            self.log(f"❌ Ошибка: {e}")
        finally:
            self.process_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.progress_var.set(1.0)
            allow_sleep()
            self.log("🌙 Сон снова разрешён.")

    def stop_process(self):
        if self.current_process:
            self.current_process.terminate()
            self.log("🛑 Процесс остановлен вручную.")
            self.current_process = None
        else:
            self.log("⚠️ Нет активного процесса.")

    def log(self, message: str):
        self.log_messages.append(message)
        self.log_text_main.insert('end', message + "\n")
        self.log_text_main.yview('end')
        self.dev_log(message)  # синхронизируем с dev

    def dev_log(self, message: str):
        self.log_text_dev.insert('end', message + "\n")
        self.log_text_dev.yview('end')

    def clear_log(self):
        self.log_messages.clear()
        self.log_text_main.delete(1.0, 'end')
        self.log_text_dev.delete(1.0, 'end')

    def on_close(self):
        self.log("Закрытие приложения...")
        self.destroy()

if __name__ == "__main__":
    app = WhisperGUI()
    app.mainloop()
