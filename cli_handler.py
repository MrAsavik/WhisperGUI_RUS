import os
import subprocess
from config import DEFAULT_MODEL, DEFAULT_LANGUAGE, OUTPUT_FORMATS


def check_output_file(output_dir, base_filename, extensions):
    """
    Проверяет, были ли созданы файлы результата.

    :param output_dir: Папка, куда должны сохраняться файлы
    :param base_filename: Имя файла без расширения
    :param extensions: Список возможных расширений (.txt, .srt, .json и т.д.)
    :return: список найденных файлов
    """
    found_files = []
    for ext in extensions:
        path = os.path.join(output_dir, base_filename + ext)
        if os.path.exists(path):
            found_files.append(path)
    return found_files

def process_files_cli(file_paths, model=None, language=None, formats=None, threads=None):
    """
    Запускает CLI whisper для каждого файла и возвращает subprocess.Popen.
    """
    model = model or DEFAULT_MODEL
    language = language or DEFAULT_LANGUAGE
    formats = formats or OUTPUT_FORMATS

    # Определяем формат вывода
    if len(formats) > 1:
        output_format = "all"
    elif formats:
        output_format = formats[0]
    else:
        output_format = "txt"

    commands = []
    for file_path in file_paths:
        output_dir = os.path.dirname(file_path)
        
        cmd = [
            "whisper", file_path,
            "--model", model,
            "--language", language,
            "--output_format", output_format,
            "--output_dir", output_dir
        ]
        if threads:
            cmd.extend(["--threads", str(threads)])
        commands.append(cmd)
        

    full_script = " && ".join(
        " ".join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
        for cmd in commands
    )

    return subprocess.Popen(
        full_script,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
