import sys
from gui import WhisperGUI
from cli_handler import process_files_cli
from updater import check_update

if __name__ == '__main__':
    # Если запущено в режиме CLI, обрабатываем аргументы и выходим
    if '--cli' in sys.argv:
        process_files_cli()
    else:
        # Проверяем наличие обновлений перед запуском GUI
        try:
            check_update()
        except Exception as e:
            print(f"Не удалось проверить обновления: {e}")

        # Запускаем графический интерфейс
        app = WhisperGUI()
        app.mainloop()
