import psutil


def kill_process_tree(pid):
    """
    Принудительно завершает процесс и всех его дочерних.

    Используется для полной остановки процесса whisper (и дочерних), если пользователь нажимает "Стоп".
    """
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass
