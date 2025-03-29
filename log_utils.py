def log(app, message: str):
    """
    Основной лог — отображается на вкладке "Главная" и дублируется в "Разработчику".
    """
    app.log_messages.append(message)
    app.log_text_main.insert('end', message + '\n')
    app.log_text_main.yview('end')
    dev_log(app, message)


def dev_log(app, message: str):
    """
    Лог "Разработчику" — для подробного вывода.
    """
    app.log_text_dev.insert('end', message + '\n')
    app.log_text_dev.yview('end')


def clear_log(app):
    """
    Полная очистка логов во всех вкладках.
    """
    app.log_messages.clear()
    app.log_text_main.delete(1.0, 'end')
    app.log_text_dev.delete(1.0, 'end')
