import customtkinter as ctk
from tkinter import filedialog, scrolledtext
from ui_utils import bind_copy  # ✅ Добавить импорт
from log_utils import clear_log



def build_ui(app):
    """
    Основная точка создания UI: собирает все вкладки и их компоненты.
    """
    app.tabview = ctk.CTkTabview(app)
    app.tabview.pack(expand=True, fill='both')

    build_main_tab(app)
    build_settings_tab(app)
    build_dev_tab(app)


def build_main_tab(app):
    tab = app.tabview.add("Главная")

    # Верхние кнопки
    ctk.CTkButton(tab, text="Очистить список файлов", command=app.clear_file_list).pack(pady=5)
    app.file_label = ctk.CTkLabel(tab, text="Файлы не выбраны")
    app.file_label.pack(pady=10)

    # Кнопки обработки
    ctk.CTkButton(tab, text="Выбрать файлы", command=app.select_files).pack(pady=5)
    app.process_button = ctk.CTkButton(tab, text="Распознать", command=app.process_files, state="disabled")
    app.process_button.pack(pady=5)
    app.stop_button = ctk.CTkButton(tab, text="Стоп", command=app.stop_process, fg_color="red", state="disabled")
    app.stop_button.pack(pady=5)

    # Прогресс и статус
    app.progress_bar = ctk.CTkProgressBar(tab, variable=app.progress_var, width=400)
    app.progress_bar.pack(pady=10)
    app.progress_var.set(0)

    app.status_label = ctk.CTkLabel(tab, text="⚪ Ожидание...", anchor='w')
    app.status_label.pack(pady=5)

    # Основной лог
    app.log_text_main = scrolledtext.ScrolledText(tab, wrap='word', width=80, height=10)
    app.log_text_main.pack(pady=10)
    bind_copy(app.log_text_main)

    ctk.CTkButton(tab, text="Очистить лог", command=lambda: clear_log(app)).pack(pady=5)




def build_settings_tab(app):
    tab = app.tabview.add("Настройки")

    ctk.CTkLabel(tab, text="Модель Whisper:").pack(pady=5)
    ctk.CTkOptionMenu(tab, values=["tiny", "small", "medium", "large"], variable=app.model_var).pack()

    ctk.CTkLabel(tab, text="Язык:").pack(pady=5)
    ctk.CTkOptionMenu(tab, values=["Russian", "English", "Auto"], variable=app.language_var).pack()

    ctk.CTkLabel(tab, text="Форматы вывода:").pack(pady=5)
    for fmt, var in app.selected_formats.items():
        ctk.CTkCheckBox(tab, text=f"{fmt.upper()} формат", variable=var).pack(anchor='w', padx=20)

    ctk.CTkButton(tab, text="Выбрать папку для сохранения", command=app.select_folder).pack(pady=10)
    ctk.CTkLabel(tab, text="Дополнительно:").pack(pady=10)
    ctk.CTkCheckBox(tab, text="🌙 Turbo-режим (ночная высокая нагрузка CPU)", variable=app.turbo_var).pack(anchor='w', padx=20)


def build_dev_tab(app):
    tab = app.tabview.add("Разработчику")
    app.log_text_dev = scrolledtext.ScrolledText(tab, wrap='word', width=110, height=35)
    app.log_text_dev.pack(pady=10, padx=10, expand=True, fill='both')
    bind_copy(app.log_text_dev)