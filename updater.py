import requests
import os
import sys
import subprocess
import re

# Ваш GitHub-репозиторий в формате owner/repo
GITHUB_REPO = "MrAsavik/WhisperGUI_RUS"


def get_current_version():
    # если упаковано PyInstaller, все файлы лежат в sys._MEIPASS
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    changelog_path = os.path.join(base, "CHANGELOG.md")
    try:
        text = open(changelog_path, encoding="utf-8").read()
    except FileNotFoundError:
        return "0.0.0"
    m = re.search(r"\[(\d+\.\d+\.\d+)\]", text)
    return m.group(1) if m else "0.0.0"

# Текущая версия приложения, автоматически полученная из CHANGELOG.md
CURRENT_VERSION = get_current_version()


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
    latest_tag = data.get("tag_name", "").lstrip("v")
    if latest_tag == CURRENT_VERSION:
        return False  # обновлений нет

    # Ищем .exe среди ассетов
    asset = next((a for a in data.get("assets", []) if a["name"].endswith(".exe")), None)
    if not asset:
        return False

    download_url = asset["browser_download_url"]
    file_name = asset["name"]
    # Сохраняем рядом с текущим исполняемым файлом
    save_path = os.path.join(os.path.dirname(sys.executable), file_name)

    # Скачиваем файл
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    # Запускаем новую версию и закрываем старую
    subprocess.Popen([save_path], shell=True)
    sys.exit(0)
