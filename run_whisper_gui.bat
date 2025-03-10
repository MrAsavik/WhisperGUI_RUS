@echo off
REM Перейти на диск D:
D:

REM Перейти в директорию проекта
cd D:\IT\проекты\Распознание Речи 2\WhisperGUI_RUS

REM Активировать виртуальное окружение
call D:\python_envs\whisper_env\Scripts\activate.bat

REM Запустить основное приложение
python WhisperGUI.py

