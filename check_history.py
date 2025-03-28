import os
from config import HISTORY_FILE
from history import load_history, save_history, file_already_processed

print(f"📂 Ожидаемый путь history.json: {HISTORY_FILE}")

# Проверяем, где реально находится файл
if os.path.exists(HISTORY_FILE):
    print(f"✅ Файл найден по пути: {HISTORY_FILE}")
else:
    print(f"❌ Файл НЕ найден!")

# Добавляем тестовую запись
save_history("test_file.mp4", success=True)

# Проверяем, что история обновилась
history = load_history()
print("📜 История обработки файлов:", history)
