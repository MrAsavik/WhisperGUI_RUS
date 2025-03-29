import sys
import io
from gui import WhisperGUI
from cli_handler import process_files_cli

# 🔤 Устанавливаем кодировку вывода в UTF-8 (для Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    if '--cli' in sys.argv:
        # 🔧 CLI-режим (будет расширен, если передавать файлы, модель и т.д.)
        print("⚙️ Запущен в режиме командной строки (CLI)")
        # Пока передаём заглушку — позже можно обработать sys.argv и передать параметры
        process_files_cli([])
    else:
        # 🖼️ GUI-режим (основной)
        app = WhisperGUI()
        app.mainloop()

if __name__ == '__main__':
    main()
