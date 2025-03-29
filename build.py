import subprocess
import os
import shutil
import zipfile
import datetime
import re
import time

PROJECT_NAME = "WhisperGUI_RUS"
MAIN_SCRIPT = "main.py"
DIST_DIR = "dist_builds"
LOG_FILE = "build_log.txt"
CHANGELOG_FILE = "CHANGELOG.md"

def extract_version():
    with open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'\[(\d+\.\d+\.\d+)\]', content)
    if match:
        return match.group(1)
    return "0.0.0"

def log(message):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_message = f"{timestamp} {message}"
    print(log_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(log_message + '\n')

def build_exe():
    version = extract_version()
    date_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    build_name = f"{PROJECT_NAME}_v{version}_{date_time}"
    build_path = os.path.join(DIST_DIR, build_name)

    log("🚧 Запуск сборки...")
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", PROJECT_NAME,
        MAIN_SCRIPT
    ], check=True)

    # Перемещаем EXE в каталог сборки
    if not os.path.exists(build_path):
        os.makedirs(build_path)
    shutil.move(f"dist/{PROJECT_NAME}.exe", f"{build_path}/{PROJECT_NAME}.exe")

    # Создаём ZIP
    zip_name = f"{build_path}.zip"
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        zipf.write(f"{build_path}/{PROJECT_NAME}.exe", f"{PROJECT_NAME}.exe")

    log(f"✅ Сборка завершена. Путь: {build_path}")
    log(f"📦 Создан архив: {zip_name}")

    # Очистка временных файлов
    cleanup(build_path)

    # Автозапуск
    auto_run_exe(f"{build_path}/{PROJECT_NAME}.exe")

def cleanup(path):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            print(f"♻️ Удалено: {path}")
            break
        except PermissionError as e:
            print(f"⚠️ Файл занят ({e}), попытка {attempt+1}/{max_retries}...")
            time.sleep(5)  # ожидание перед повторной попыткой
    else:
        print(f"❌ Не удалось удалить {path}. Удалите вручную позже.")

    log("🧹 Очистка завершена.")

def auto_run_exe(exe_path):
    log(f"🧪 Запуск {exe_path}...")
    subprocess.Popen(exe_path, shell=True)
    log("🚀 Приложение успешно запущено.")

if __name__ == "__main__":
    build_exe()
