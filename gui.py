import customtkinter as ctk
from tkinter import filedialog, scrolledtext
from cli_handler import process_files_cli
from config import DEFAULT_MODEL, DEFAULT_LANGUAGE, OUTPUT_FORMATS

class WhisperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
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

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        """Создаёт вкладки и элементы управления."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill='both')
        
        self.main_tab = self.tabview.add("Главная")
        self.settings_tab = self.tabview.add("Настройки")
        
        self.create_main_tab()
        self.create_settings_tab()

    def create_main_tab(self):
        """Создаёт элементы на вкладке Главная."""
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

        self.log_text = scrolledtext.ScrolledText(self.main_tab, wrap='word', width=80, height=10)
        self.log_text.pack(pady=10)
        
        self.clear_log_button = ctk.CTkButton(self.main_tab, text="Очистить лог", command=self.clear_log)
        self.clear_log_button.pack(pady=5)
        
    def create_settings_tab(self):
        """Создаёт элементы на вкладке Настройки."""
        ctk.CTkLabel(self.settings_tab, text="Модель Whisper:").pack(pady=5)
        ctk.CTkOptionMenu(self.settings_tab, values=["tiny", "small", "medium", "large"], variable=self.model_var).pack()

        ctk.CTkLabel(self.settings_tab, text="Язык:").pack(pady=5)
        ctk.CTkOptionMenu(self.settings_tab, values=["Russian", "English", "Auto"], variable=self.language_var).pack()

        ctk.CTkLabel(self.settings_tab, text="Форматы вывода:").pack(pady=5)
        for fmt, var in self.selected_formats.items():
            ctk.CTkCheckBox(self.settings_tab, text=f"{fmt.upper()} формат", variable=var).pack(anchor='w', padx=20)

        ctk.CTkButton(self.settings_tab, text="Выбрать папку для сохранения", command=self.select_folder).pack(pady=10)

    def select_files(self):
        """Выбор файлов через диалоговое окно."""
        files = filedialog.askopenfilenames(filetypes=[("Аудио и видео", "*.wav *.mp3 *.mp4 *.mkv" ".m4a" ".aac")])
        if files:
            self.selected_files = list(files)
            self.file_label.configure(text=f"Выбрано файлов: {len(self.selected_files)}")
            self.process_button.configure(state="normal")

    def select_folder(self):
        """Выбор папки сохранения."""
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.log(f"Папка сохранения: {folder}")

    def process_files(self):
        """Запускает обработку файлов."""
        if self.selected_files:
            self.progress_var.set(0.5)
            process_files_cli(self.selected_files)
            self.progress_var.set(1.0)

    def stop_process(self):
        """Останавливает текущий процесс (заглушка)."""
        self.log("⛔ Остановка процесса... (Функция ещё не реализована)")

    def log(self, message: str):
        """Выводит сообщение в лог в GUI."""
        self.log_messages.append(message)
        self.log_text.insert('end', message + "\n")
        self.log_text.yview('end')

    def clear_log(self):
        """Очищает окно логов."""
        self.log_messages.clear()
        self.log_text.delete(1.0, 'end')

    def on_close(self):
        """Закрытие приложения с очисткой ресурсов."""
        self.log("Закрытие приложения...")
        self.destroy()

if __name__ == "__main__":
    app = WhisperGUI()
    app.mainloop()
