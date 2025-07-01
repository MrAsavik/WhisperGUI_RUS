import requests
import os
import sys
import subprocess

# Укажите ваш GitHub-репозиторий
GITHUB_REPO = "MrAsavik/WhisperGUI_RUS"
# Текущая версия приложения, синхронизируйте с CHANGELOG
CURRENT_VERSION = "0.2.1"

def check_update():
    """
    Проверяет GitHub Releases на наличие новой версии.
    Если найдёт, скачает .exe и запустит его, после чего текущий процесс завершится.
    """
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    resp = requests.get(api_url)
    if resp.status_code != 200:
        return False

    data = resp.json()
    latest_tag = data["tag_name"].lstrip("v")
    if latest_tag == CURRENT_VERSION:
        return False  # обновлений нет

    # Ищем `.exe` в списке ассетов
    asset = next((a for a in data["assets"] if a["name"].endswith(".exe")), None)
    if not asset:
        return False

    download_url = asset["browser_download_url"]
    local_path = os.path.join(os.path.dirname(sys.executable),
                              asset["name"])

    # Скачиваем файл
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    # Запускаем новую версию и завершаем старую
    subprocess.Popen([local_path], shell=True)
    sys.exit(0)
