import os
import re
import subprocess
import threading
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
from pydub.utils import mediainfo

# Настройки окна
ctk.set_appearance_mode("dark")  # Тёмная тема
ctk.set_default_color_theme("blue")
import os
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk

# Настройки окна
ctk.set_appearance_mode("dark")  # Тёмная тема
ctk.set_default_color_theme("blue")

class FileProcessor:
    """ Класс для обработки файлов с помощью Whisper """

    def __init__(self, on_complete_callback, log_callback, update_status_callback):
        self.on_complete_callback = on_complete_callback
        self.log_callback = log_callback
        self.update_status_callback = update_status_callback
        self.whisper_process = None

    def process_files(self, files, model="small", language="Russian", output_dir=os.getcwd(), formats=None, overwrite=False):
        """ Запуск обработки файлов в отдельном потоке """
        threading.Thread(
            target=self._run_whisper,
            args=(files, model, language, output_dir, formats, overwrite),
            daemon=True
        ).start()

    def _run_whisper(self, files, model, language, output_dir, formats, overwrite):
        for file_path in files:
            file_name = os.path.basename(file_path)
            self.update_status_callback(f"⏳ Обработка файла: {file_name}")
            self.log_callback(f"Начало обработки файла: {file_name}")

            for fmt in formats:
                output_file = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.{fmt}")
                if os.path.exists(output_file) and not overwrite:
                    self.log_callback(f"⏭ Пропуск (уже существует): {output_file}")
                    continue

                whisper_args = [
                    "whisper", file_path,
                    "--model", model,
                    "--language", language,
                    "--output_dir", output_dir,
                    "--output_format", fmt
                ]

                self.whisper_process = subprocess.Popen(
                    whisper_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                stdout, stderr = self.whisper_process.communicate()

                if self.whisper_process.returncode != 0:
                    messagebox.showerror("Ошибка", f"Ошибка при обработке {file_name} ({fmt}):\n{stderr}")
                    self.log_callback(f"❌ Ошибка: {stderr}")
                    return

                self.log_callback(f"✅ Файл обработан: {output_file}")

        self.on_complete_callback()

    def stop(self):
        if self.whisper_process and self.whisper_process.poll() is None:
            self.whisper_process.terminate()
            self.log_callback("⚠ Процесс обработки остановлен.")

class WhisperGUI(ctk.CTk):
    """ Основной класс графического интерфейса """

    def __init__(self):
        super().__init__()

        self.title("Whisper GUI")
        self.geometry("700x700")

        self.selected_files = []
        self.output_formats = ["txt", "srt"]
        self.output_dir = os.getcwd()

        self.progress_var = ctk.DoubleVar()
        self.estimated_time_var = ctk.StringVar(value="Ожидание...")
        self.enable_sound_notifications = ctk.BooleanVar(value=True)
        self.overwrite_existing = ctk.BooleanVar(value=False)

        self.file_processor = FileProcessor(
            self.on_process_complete,
            self.log,
            self.update_status
        )

        self.create_widgets()

    def create_widgets(self):
        """ Создание виджетов интерфейса """

        # Выбор файлов
        self.file_label = ctk.CTkLabel(self, text="Файлы не выбраны")
        self.file_label.pack(pady=10)

        self.select_button = ctk.CTkButton(self, text="Выбрать файлы", command=self.select_files)
        self.select_button.pack(pady=5)

        self.process_button = ctk.CTkButton(self, text="Распознать", command=self.process_files, state="disabled")
        self.process_button.pack(pady=5)

        # Прогресс-бар
        self.progress_bar = ctk.CTkProgressBar(self, variable=self.progress_var, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_var.set(0)

        # Статус
        self.status_label = ctk.CTkLabel(self, textvariable=self.estimated_time_var, font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=10)

        # Настройки модели и языка
        ctk.CTkLabel(self, text="Модель:").pack()
        self.model_var = ctk.StringVar(value="small")
        self.model_menu = ctk.CTkOptionMenu(self, values=["small", "medium", "large"], variable=self.model_var)
        self.model_menu.pack(pady=5)

        ctk.CTkLabel(self, text="Язык:").pack()
        self.language_var = ctk.StringVar(value="Russian")
        self.language_menu = ctk.CTkOptionMenu(self, values=["Russian", "English"], variable=self.language_var)
        self.language_menu.pack(pady=5)

        # Выбор папки для сохранения
        self.select_folder_button = ctk.CTkButton(self, text="Выбрать папку для сохранения", command=self.select_folder)
        self.select_folder_button.pack(pady=5)

        # Чекбокс для перезаписи существующих файлов
        self.overwrite_checkbox = ctk.CTkCheckBox(self, text="Перезаписывать уже распознанные файлы", variable=self.overwrite_existing)
        self.overwrite_checkbox.pack(pady=10)

        # Переключение темы
        self.theme_switch = ctk.CTkSwitch(self, text="Тёмная тема", command=self.toggle_theme)
        self.theme_switch.pack(pady=5)

        # Чекбокс для звуковых уведомлений
        self.sound_checkbox = ctk.CTkCheckBox(self, text="Включить звук уведомлений", variable=self.enable_sound_notifications)
        self.sound_checkbox.pack(pady=10)

        # Поле логов
        self.log_text = scrolledtext.ScrolledText(self, wrap='word', width=80, height=10, state='disabled')
        self.log_text.pack(pady=10)

    def toggle_theme(self):
        mode = "dark" if self.theme_switch.get() else "light"
        ctk.set_appearance_mode(mode)

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Аудио и видео", "*.wav *.mp3 *.mp4 *.mkv")])
        if files:
            self.selected_files = list(files)
            self.file_label.configure(text=f"Выбрано файлов: {len(self.selected_files)}")
            self.process_button.configure(state="normal")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.log(f"📁 Папка для сохранения: {self.output_dir}")

    def log(self, message: str):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.configure(state='disabled')
        self.log_text.yview('end')

    def update_status(self, message: str):
        self.estimated_time_var.set(message)

    def process_files(self):
        formats = ["txt", "srt"]  # Пример форматов
        self.file_processor.process_files(
            self.selected_files,
            model=self.model_var.get(),
            language=self.language_var.get(),
            output_dir=self.output_dir,
            formats=formats,
            overwrite=self.overwrite_existing.get()
        )
        self.update_status("⏳ Начало обработки файлов...")

    def on_process_complete(self):
        self.update_status("✅ Обработка завершена!")
        messagebox.showinfo("Готово!", "Все файлы успешно обработаны!")

    def on_close(self):
        self.file_processor.stop()
        self.destroy()


if __name__ == '__main__':
    app = WhisperGUI()
    app.mainloop()

class WhisperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Whisper GUI")
        self.geometry("700x700")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Переменные состояния
        self.selected_files = []
        self.whisper_process = None
        self.duration = 1  # Длительность текущего файла в секундах
        self.progress_var = ctk.DoubleVar()
        self.estimated_time_var = ctk.StringVar(value="Ожидание...")
        self.current_file_var = ctk.StringVar(value="Файл не выбран")
        self.model_var = ctk.StringVar(value="small")
        self.language_var = ctk.StringVar(value="Russian")
        self.output_dir = os.getcwd()
        self.output_formats = ["txt", "srt"]
        self.overwrite_existing = ctk.BooleanVar(value=False)
        self.enable_sound_notifications = ctk.BooleanVar(value=True)
        self.start_time = 0

        self.create_widgets()

    def create_widgets(self):
        # Выбор файлов
        self.file_label = ctk.CTkLabel(self, text="Файлы не выбраны")
        self.file_label.pack(pady=10)

        self.select_button = ctk.CTkButton(self, text="Выбрать файлы", command=self.select_files)
        self.select_button.pack(pady=5)

        self.process_button = ctk.CTkButton(self, text="Распознать", command=self.process_files, state="disabled")
        self.process_button.pack(pady=5)

        # Прогресс-бар
        self.progress_bar = ctk.CTkProgressBar(self, variable=self.progress_var, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_var.set(0)

        # Статус
        self.status_label = ctk.CTkLabel(self, textvariable=self.estimated_time_var, font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=10)

        # Текущий файл
        self.current_file_label = ctk.CTkLabel(self, textvariable=self.current_file_var, font=('Arial', 10))
        self.current_file_label.pack(pady=5)

        # Настройки модели и языка
        ctk.CTkLabel(self, text="Модель:").pack()
        self.model_menu = ctk.CTkOptionMenu(self, values=["small", "medium", "large"], variable=self.model_var)
        self.model_menu.pack(pady=5)

        ctk.CTkLabel(self, text="Язык:").pack()
        self.language_menu = ctk.CTkOptionMenu(self, values=["Russian", "English"], variable=self.language_var)
        self.language_menu.pack(pady=5)

        # Выбор папки для сохранения
        self.select_folder_button = ctk.CTkButton(self, text="Выбрать папку для сохранения", command=self.select_folder)
        self.select_folder_button.pack(pady=5)

        # Чекбокс для перезаписи существующих файлов
        self.overwrite_checkbox = ctk.CTkCheckBox(self, text="Перезаписывать уже распознанные файлы", variable=self.overwrite_existing)
        self.overwrite_checkbox.pack(pady=10)

        # Переключение темы
        self.theme_switch = ctk.CTkSwitch(self, text="Тёмная тема", command=self.toggle_theme)
        self.theme_switch.pack(pady=5)

        # Чекбокс для звуковых уведомлений
        self.sound_checkbox = ctk.CTkCheckBox(self, text="Включить звук уведомлений", variable=self.enable_sound_notifications)
        self.sound_checkbox.pack(pady=10)

        # Поле логов
        self.log_text = scrolledtext.ScrolledText(self, wrap='word', width=80, height=10, state='disabled')
        self.log_text.pack(pady=10)

    def toggle_theme(self):
        mode = "dark" if self.theme_switch.get() else "light"
        ctk.set_appearance_mode(mode)

    # Остальной код без изменений...

if __name__ == '__main__':
    app = WhisperGUI()
    app.mainloop()
