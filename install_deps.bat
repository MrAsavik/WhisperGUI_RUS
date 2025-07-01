@echo off
REM =========================================
REM  Скрипт автоматической установки зависимостей
REM =========================================

REM 1) Проверяем, что Python доступен
where python >nul 2>&1
if errorlevel 1 (
  echo Ошибка: не найден python в PATH.
  echo Пожалуйста, установите Python 3.9+ и добавьте его в PATH:
  echo https://www.python.org/downloads/
  pause
  exit /b 1
)

REM 2) Обновляем pip до актуальной версии
echo Обновляю pip...
python -m pip install --upgrade pip

REM 3) Устанавливаем все библиотеки из requirements.txt
if not exist "requirements.txt" (
  echo Ошибка: файл requirements.txt не найден!
  pause
  exit /b 1
)
echo Устанавливаю зависимости из requirements.txt...
pip install -r requirements.txt

echo.
echo Все зависимости успешно установлены!
pause
