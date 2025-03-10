import os
import re
import json
import subprocess
import threading
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext

try:
    import tkdnd  # для Drag & Drop
except ImportError:
    tkdnd = None  # Если нет tkdnd, Drag & Drop работать не будет

print("Инициализация приложения...")

ctk.set_appearance_mode("dark")  # Тёмная тема
ctk.set_default_color_theme("blue")

HISTORY_FILE = "history.json"
DEV_LOG_FILE = "whispergui_dev.log"

def write_dev_log(message: str):
    """Пишет логи разработчика в отдельный файл."""
    with open(DEV_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


class WhisperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        print("Создание главного окна...")

        self.title("Whisper GUI Расширенный")
        self.geometry("900x700")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Переменные состояния ---
        self.selected_files = []
        self.whisper_process = None

        # Прогресс-бар и статусы
        self.progress_var = ctk.DoubleVar()
        self.estimated_time_var = ctk.StringVar(value="Ожидание...")
        self.current_file_var = ctk.StringVar(value="Файл не выбран")

        # Whisper-настройки
        self.model_var = ctk.StringVar(value="small")
        self.language_var = ctk.StringVar(value="Russian")
        self.output_dir = os.getcwd()
        self.output_formats = ["txt", "srt", "vtt", "json"]
        self.selected_formats = {fmt: ctk.BooleanVar(value=True) for fmt in self.output_formats}

        # История обработанных файлов (JSON)
        self.history_data = self.load_history()

        # Аналитика
        self.files_processed = 0
        self.total_processing_time = 0.0

        # Планировщик (автоматизация)
        self.scheduler_thread = None
        self.schedule_active = False
        self.schedule_interval = 60  # секунд

        self.create_widgets()
        self.enable_drag_and_drop()

    def create_widgets(self):
        write_dev_log("Создание виджетов...")

        # Основной виджет ctk.CTkTabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill='both')

        # Вкладки
        self.main_tab = self.tabview.add("Главная")
        self.settings_tab = self.tabview.add("Настройки")
        self.stats_tab = self.tabview.add("Статистика")

        # --- Главная вкладка ---
        self.file_label = ctk.CTkLabel(self.main_tab, text="Файлы не выбраны")
        self.file_label.pack(pady=10)

        self.select_button = ctk.CTkButton(self.main_tab, text="Выбрать файлы", command=self.select_files)
        self.select_button.pack(pady=5)

        self.process_button = ctk.CTkButton(self.main_tab, text="Распознать", command=self.process_files, state="disabled")
        self.process_button.pack(pady=5)

        self.stop_button = ctk.CTkButton(self.main_tab, text="Стоп", command=self.stop_process, fg_color="red", state="disabled")
        self.stop_button.pack(pady=5)

        # Прогресс-бар
        self.progress_bar = ctk.CTkProgressBar(self.main_tab, variable=self.progress_var, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_var.set(0)

        # Статус
        self.status_label = ctk.CTkLabel(self.main_tab, textvariable=self.estimated_time_var, font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=10)

        # Текущий файл
        self.current_file_label = ctk.CTkLabel(self.main_tab, textvariable=self.current_file_var, font=('Arial', 10))
        self.current_file_label.pack(pady=5)

        # Поле логов
        self.log_text = scrolledtext.ScrolledText(self.main_tab, wrap='word', width=80, height=10)
        self.log_text.pack(pady=10)

        self.clear_log_button = ctk.CTkButton(self.main_tab, text="Очистить лог", command=self.clear_log)
        self.clear_log_button.pack(pady=5)

        # --- Настройки ---
        ctk.CTkLabel(self.settings_tab, text="Форматы вывода:").pack(pady=10)
        for fmt, var in self.selected_formats.items():
            ctk.CTkCheckBox(self.settings_tab, text=f"{fmt.upper()} формат", variable=var).pack(anchor='w', padx=20)

        # Whisper настройки
        ctk.CTkLabel(self.settings_tab, text="Whisper Модель:").pack(pady=10)
        ctk.CTkOptionMenu(self.settings_tab, values=["tiny", "small", "medium", "large"], variable=self.model_var).pack()

        ctk.CTkLabel(self.settings_tab, text="Язык:").pack(pady=10)
        ctk.CTkOptionMenu(self.settings_tab, values=["Russian", "English", "Auto"], variable=self.language_var).pack()

        ctk.CTkButton(self.settings_tab, text="Выбрать папку для сохранения", command=self.select_folder).pack(pady=10)

        # Псевдо-планировщик
        ctk.CTkLabel(self.settings_tab, text="Автоматическая обработка каждые 60 сек:").pack()
        ctk.CTkButton(self.settings_tab, text="Включить расписание", command=self.start_scheduler).pack(pady=5)
        ctk.CTkButton(self.settings_tab, text="Выключить расписание", command=self.stop_scheduler).pack()

        # --- Статистика ---
        self.stats_label = ctk.CTkLabel(self.stats_tab, text="", font=('Arial', 12))
        self.stats_label.pack(pady=10)
        self.update_stats_label()

    # ---------------------
    #   ЛОГИРОВАНИЕ
    # ---------------------
    def log(self, message: str):
        """Безопасное логирование."""
        try:
            self.log_text.insert('end', f"{message}\n")
            self.log_text.yview('end')
            write_dev_log(message)
        except Exception as e:
            print(f"[Ошибка логирования] {e}")

    # ---------------------
    #   DRAG & DROP
    # ---------------------
    def enable_drag_and_drop(self):
        if hasattr(self.main_tab, 'tk') and hasattr(self.main_tab.tk, 'tkdnd'):
            self.main_tab.tk.tk.call('package', 'require', 'tkdnd')
            self.main_tab.drop_target_register('*')
            self.main_tab.dnd_bind('<<DropEnter>>', self.drop_enter)
            self.main_tab.dnd_bind('<<DropPosition>>', self.drop_position)
            self.main_tab.dnd_bind('<<DropLeave>>', self.drop_leave)
            self.main_tab.dnd_bind('<<Drop>>', self.drop)
        else:
            write_dev_log("tkdnd не обнаружен. Drag & Drop не будет работать.")

    def drop_enter(self, event):
        write_dev_log("Drop Enter")

    def drop_position(self, event):
        pass

    def drop_leave(self, event):
        write_dev_log("Drop Leave")

    def drop(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            if os.path.splitext(f)[1].lower() in [".wav", ".mp3", ".mp4", ".mkv"]:
                self.selected_files.append(f)
        self.file_label.configure(text=f"Выбрано файлов: {len(self.selected_files)}")
        self.process_button.configure(state="normal")

    # ---------------------
    #   ИСТОРИЯ ФАЙЛОВ
    # ---------------------
    def load_history(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def save_history(self, file_name, success=True):
        entry = {
            "file": file_name,
            "success": success,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history_data.append(entry)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history_data, f, ensure_ascii=False, indent=2)

    # ---------------------
    #   СТАТИСТИКА
    # ---------------------
    def update_stats_label(self):
        text = (
            f"Всего обработано файлов: {self.files_processed}\n"
            f"Суммарное время обработки (примерно): {self.total_processing_time:.1f} сек\n"
            "Более детальная статистика может быть добавлена здесь."
        )
        self.stats_label.configure(text=text)

    # ---------------------
    #   ОБРАБОТКА GUI
    # ---------------------
    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Аудио и видео", "*.wav *.mp3 *.mp4 *.mkv")])
        if files:
            self.selected_files = list(files)
            self.file_label.configure(text=f"Выбрано файлов: {len(self.selected_files)}")
            self.process_button.configure(state="normal")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            try:
                self.output_dir = folder
                self.log(f"Папка для сохранения: {self.output_dir}")
            except Exception as e:
                print(f"[Ошибка log при select_folder] {e}")

    def process_files(self):
        self.output_formats = [fmt for fmt, var in self.selected_formats.items() if var.get()]
        if not self.output_formats:
            messagebox.showerror("Ошибка", "Выберите хотя бы один формат вывода!")
            return

        try:
            self.log(f"Выбраны форматы: {', '.join(self.output_formats)}")
        except Exception as e:
            print(f"[Ошибка log при process_files] {e}")

        self.process_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        threading.Thread(target=self.run_whisper, daemon=True).start()

    def run_whisper(self):
        start_time = time.time()
        total_files = len(self.selected_files)

        for index, file_path in enumerate(self.selected_files):
            file_name = os.path.basename(file_path)
            try:
                self.current_file_var.set(f"Обработка файла: {file_name}")
                self.log(f"🟢 Начало обработки файла: {file_name}")
            except Exception as e:
                print(f"[Ошибка при установке current_file_var/log] {e}")

            # Примитивная проверка: файл уже был обработан?
            if self.file_already_processed(file_name):
                try:
                    self.log(f"⏭ Пропуск (файл уже обрабатывался): {file_name}")
                except:
                    pass
                continue

            success = True
            for fmt in self.output_formats:
                whisper_args = [
                    "whisper", file_path,
                    "--model", self.model_var.get(),
                    "--language", self.language_var.get(),
                    "--output_dir", self.output_dir,
                    "--output_format", fmt
                ]
                self.whisper_process = subprocess.Popen(
                    whisper_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                stdout, stderr = self.whisper_process.communicate()

                if stdout:
                    for line in stdout.splitlines():
                        try:
                            self.log(line)
                        except:
                            pass
                if stderr:
                    for line in stderr.splitlines():
                        try:
                            self.log(f"[stderr] {line}")
                        except:
                            pass

                rc = self.whisper_process.returncode
                if rc != 0:
                    try:
                        self.log(f"❌ Ошибка при обработке {file_name} (формат {fmt})")
                    except:
                        pass
                    success = False
                    break

            progress = (index + 1) / total_files
            self.progress_var.set(progress)
            self.update_idletasks()

            self.save_history(file_name, success=success)
            if success:
                try:
                    self.log(f"✅ Файл {file_name} обработан и записан.")
                except:
                    pass
            else:
                try:
                    self.log(f"⚠ Частичная ошибка при обработке {file_name}")
                except:
                    pass

        end_time = time.time()
        self.stop_button.configure(state="disabled")
        self.process_button.configure(state="normal")
        self.estimated_time_var.set("✅ Все файлы обработаны!")

        duration = end_time - start_time
        self.files_processed += total_files
        self.total_processing_time += duration
        self.update_stats_label()

        try:
            self.log(f"✅ Обработка завершена за {duration:.1f} сек.")
        except:
            pass

    def file_already_processed(self, file_name):
        for item in self.history_data:
            if item["file"] == file_name and item["success"] is True:
                return True
        return False

    def stop_process(self):
        if self.whisper_process and self.whisper_process.poll() is None:
            self.whisper_process.terminate()
            try:
                self.log("⚠ Процесс остановлен пользователем.")
            except:
                pass
            self.process_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

    def clear_log(self):
        self.log_text.delete(1.0, 'end')

    # ---------------------
    #   Псевдо-Планировщик
    # ---------------------
    schedule_active = False
    schedule_thread = None
    schedule_interval = 60

    def start_scheduler(self):
        try:
            self.log("⏲ Планировщик запущен.")
        except:
            pass
        self.schedule_active = True
        self.schedule_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.schedule_thread.start()

    def stop_scheduler(self):
        self.schedule_active = False
        try:
            self.log("⏹ Планировщик остановлен.")
        except:
            pass

    def scheduler_loop(self):
        while self.schedule_active:
            time.sleep(self.schedule_interval)
            self.auto_process_folder()

    def auto_process_folder(self):
        folder = self.output_dir
        all_files = [
            os.path.join(folder, f) for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and os.path.splitext(f)[1].lower() in ('.mp4', '.mkv', '.wav', '.mp3')
        ]
        if not all_files:
            try:
                self.log("Планировщик: нет новых файлов для обработки.")
            except:
                pass
            return
        self.selected_files = all_files
        try:
            self.log(f"Планировщик: найдено {len(all_files)} файлов. Запуск распознавания...")
        except:
            pass
        self.process_files()

    def on_close(self):
        """Безопасное закрытие окна."""
        try:
            self.stop_process()
            self.stop_scheduler()
        except Exception as e:
            print(f"Ошибка при закрытии: {e}")
        finally:
            self.destroy()


if __name__ == '__main__':
    app = WhisperGUI()
    app.mainloop()
