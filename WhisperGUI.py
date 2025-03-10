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
