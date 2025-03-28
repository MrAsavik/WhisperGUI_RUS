import os

# Корневая папка проекта (где находится сам `config.py`)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к файлу истории (теперь он будет в папке с проектом)
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

# Лог-файл разработчика
DEV_LOG_FILE = os.path.join(BASE_DIR, "whispergui_dev.log")

# Папка для сохранения результатов (по умолчанию — та же, где исходный файл)
DEFAULT_OUTPUT_DIR = BASE_DIR

# Доступные форматы вывода
OUTPUT_FORMATS = ["txt", "srt", "vtt", "json"]

# Настройки Whisper
DEFAULT_MODEL = "small"
DEFAULT_LANGUAGE = "Russian"
