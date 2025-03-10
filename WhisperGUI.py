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

        # Поле логов
        self.log_text = scrolledtext.ScrolledText(self, wrap='word', width=80, height=10, state='disabled')
        self.log_text.pack(pady=10)

    def log(self, message: str):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.configure(state='disabled')
        self.log_text.yview('end')

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Аудио и видео", "*.wav *.mp3 *.mp4 *.mkv")]
        )
        if files:
            self.selected_files = list(files)
            self.file_label.configure(text=f"Выбрано файлов: {len(self.selected_files)}")
            self.process_button.configure(state="normal")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.log(f"📁 Папка для сохранения: {self.output_dir}")

    def process_files(self):
        if not self.selected_files:
            messagebox.showerror("Ошибка", "Сначала выберите файлы!")
            return

        self.start_time = time.time()
        self.process_button.configure(state="disabled")
        self.estimated_time_var.set("⏳ Запуск процесса...")
        threading.Thread(target=self.run_whisper, daemon=True).start()

    def run_whisper(self):
        for file_path in self.selected_files:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            self.current_file_var.set(f"Текущий файл: {file_name}")
            self.log(f"🟢 Обработка файла: {file_name}")

            whisper_args = ["whisper", file_path, "--model", self.model_var.get(), "--language", self.language_var.get(), "--output_dir", self.output_dir]
            self.log(f"Запуск команды: {' '.join(whisper_args)}")

            self.whisper_process = subprocess.Popen(
                whisper_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            for line in iter(self.whisper_process.stdout.readline, ''):
                match = re.search(r"(\d{2}:\d{2}:\d{2},\d{3})", line)
                if match:
                    time_str = match.group(1)
                    current_time = self.time_to_seconds(time_str)
                    progress = min((current_time / self.duration), 1)
                    self.progress_var.set(progress)
                    self.update_idletasks()

            self.estimated_time_var.set(f"✅ Готово: {file_name}")
            self.log(f"✅ Сохранено в: {self.output_dir}")

        total_time = time.time() - self.start_time
        messagebox.showinfo("Готово!", f"Все файлы успешно обработаны.\nОбщее время выполнения: {self.format_time(total_time)}")
        self.process_button.configure(state="normal")

    def time_to_seconds(self, time_str: str) -> float:
        match = re.search(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", time_str)
        if match:
            h, m, s, ms = match.groups()
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        self.log(f"❌ Некорректный формат времени: {time_str}")
        return 0

    def format_time(self, seconds: float) -> str:
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def on_close(self):
        if self.whisper_process and self.whisper_process.poll() is None:
            self.whisper_process.terminate()
        self.destroy()

if __name__ == '__main__':
    app = WhisperGUI()
    app.mainloop()
