# 📓 CHANGELOG

Все значимые изменения в этом проекте будут документироваться в этом файле.  
Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/)  
и придерживается [Семантического версионирования](https://semver.org/lang/ru/).

---
## [0.2.4] — 2025-07-01
Доавил приветсвенное окно что бы видел процесс проверки обновлений.
## [0.2.3] — 2025-07-01
Файл с версиями теперь тоже выгружается в исполняемый файл. Файл с версиями теперь тоже выгружается в исполняемый файл. Добавил проверку, установлена ли библиотека pip install openai-whisper, чтобы на новых компах всё работало. Пока всё, main некогда. 


## [0.2.2] — 2025-07-01
Фикс авто обновления былка ошибка в имения файлов
- Добавлено автообновление при старте приложения
- Подправлен парсер CHANGELOG.md
## [0.2.1] — 2025-07-01
Добавил автообновление попрощже распишу 
## [0.2.0] — 2025-03-29

✨ **Features**
- feat(gui): Добавлен Turbo-режим — полная загрузка CPU при ночной обработке.
- feat(gui): Встроен мониторинг загрузки процессора в режиме реального времени.
- feat(log): Статусная строка теперь отображает CPU + Turbo: Да/Нет.
- feat(ui): Реализовано разделение интерфейса по модулям: `ui.py`, `handlers.py`, `monitor.py`.
- feat(build): Добавлена автосборка `.exe` с архивированием версии из `CHANGELOG.md`.
- feat(build): Реализована автоматическая очистка временных файлов после сборки.
- feat(build): Автоматизировано создание zip-архива с указанием версии и времени сборки.

🛡 **Fixes**
- fix(process): Исправлен баг `NoneType object has no attribute 'wait'` при остановке процесса.
- fix(stop): Добавлена принудительная остановка всех дочерних процессов через `psutil` (включая `whisper.exe`).
- fix(cli): Удалён неиспользуемый аргумент `log_callback`, вызывавший ошибку запуска.
- fix(build): Исправлена ошибка доступа при удалении временных файлов после сборки.

🔧 **Refactor**
- refactor(code): Перенесена логика CPU-мониторинга в `monitor.py`, удалены дублирующие блоки логов.
- refactor(app): Минимизирована проверка `None` перед `.wait()` и `.kill()` — улучшена устойчивость.
- refactor(structure): Логика `bind_copy`, `clear_log`, `log()` вынесена в отдельные модули (`log_utils.py`, `ui_utils.py`).
- refactor(build): Улучшено логирование и обработка исключений в процессе сборки.

🧹 **Chore**
- chore(cleanup): Упрощены функции выбора файлов и логирования.
- chore(modularity): Интерфейс и бизнес-логика теперь в отдельных файлах.

🧪 **Testing**
- test(stability): Проведено ручное тестирование остановки процесса, копирования логов, обработки путей с Unicode.
- test(ui): Проверено раздельное создание вкладок, прогресс-бара и статусной строки.
- test(build): Выполнено тестирование автосборки `.exe`, архивирования и очистки временных файлов.

---

## [0.1.0] — 2025-03-29

### Добавлено
- Первая рабочая версия GUI для распознавания аудио/видео через Whisper CLI.
- Выбор файлов, модели, языка, форматов.
- Основной лог, вкладка "Разработчику", кнопки управления.
- Поддержка копирования Ctrl+C в логах.

### Исправлено
- Unicode ошибки при отображении и сохранении путей.
- Обработка логов отображалась только после завершения — теперь в реальном времени.

### Улучшено
- Интерфейс структурирован по вкладкам.
- Устойчивость процессов при остановке и выходе.

---

