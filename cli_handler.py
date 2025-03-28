import subprocess
from config import DEFAULT_MODEL, DEFAULT_LANGUAGE
from file_handler import get_output_path, save_file
from history import save_history

def process_files_cli(selected_files):
    """
    Обрабатывает файлы через командную строку, используя Whisper.
    """
    if not selected_files:
        print("Ошибка: Не выбраны файлы для обработки.")
        return

    for file_path in selected_files:
        print(f"🟢 Обрабатываю файл: {file_path}")

        # Определяем выходной путь
        output_path = get_output_path(file_path, "txt")

        # Формируем команду для Whisper
        whisper_args = [
            "whisper", file_path,
            "--model", DEFAULT_MODEL,
            "--language", DEFAULT_LANGUAGE,
            "--output_format", "txt"
        ]

        try:
            process = subprocess.run(whisper_args, text=True, capture_output=True)

            if process.returncode == 0:
                save_file(output_path, process.stdout)
                save_history(file_path, success=True)
                print(f"✅ Файл успешно обработан: {output_path}")
            else:
                print(f"❌ Ошибка при обработке {file_path}: {process.stderr}")
                save_history(file_path, success=False)

        except Exception as e:
            print(f"❌ Ошибка запуска Whisper для {file_path}: {e}")
            save_history(file_path, success=False)
