import os
from config import DEFAULT_OUTPUT_DIR

def get_output_path(input_file, extension):
    """
    Генерирует путь для сохранения выходного файла.
    По умолчанию сохраняет в той же папке, где находился входной файл.
    Если папка не определена, сохраняет в DEFAULT_OUTPUT_DIR.
    """
    input_dir = os.path.dirname(input_file)
    output_dir = input_dir if input_dir else DEFAULT_OUTPUT_DIR

    # Создаём папку, если её нет
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    return os.path.join(output_dir, f"{base_name}.{extension}")

def save_file(output_path, content):
    """
    Сохраняет содержимое в указанный файл.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Файл сохранён: {output_path}")
    except Exception as e:
        print(f"❌ Ошибка при сохранении {output_path}: {e}")
