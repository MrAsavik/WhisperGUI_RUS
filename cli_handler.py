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
    return [
        os.path.join(output_dir, base_filename + ext)
        for ext in extensions
        if os.path.exists(os.path.join(output_dir, base_filename + ext))
    ]


def process_files_cli(file_paths, model=None, language=None, formats=None, threads=None):
    """
    Запускает CLI whisper для каждого файла и возвращает subprocess.Popen.

    :param file_paths: Список путей к файлам
    :param model: Модель whisper (по умолчанию из config)
    :param language: Язык распознавания (по умолчанию из config)
    :param formats: Список форматов вывода (по умолчанию из config)
    :param threads: Количество потоков (опционально)
    :return: subprocess.Popen для всей команды
    """
    model = model or DEFAULT_MODEL
    language = language or DEFAULT_LANGUAGE
    formats = formats or OUTPUT_FORMATS

    output_format = "all" if len(formats) > 1 else (formats[0] if formats else "txt")

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

    # Формируем полную команду с экранированием аргументов
    full_script = " && ".join(
        " ".join(f'"{arg}"' if ' ' in arg or '\\' in arg else arg for arg in cmd)
        for cmd in commands
    )

    # subprocess с указанием кодировки utf-8, чтобы избежать UnicodeEncodeError
    return subprocess.Popen(
        full_script,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf-8',  # <-- фикс кодировки
        errors='replace'   # <-- чтобы не падать даже при странных символах
    )