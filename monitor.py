import psutil
import threading
import time


def start_cpu_monitor(app):
    """
    Запускает поток мониторинга загрузки CPU.
    Использует `psutil` для получения % загрузки и обновляет статус в интерфейсе.
    """
    def monitor():
        while app.current_process:
            cpu = psutil.cpu_percent(interval=1)
            app.status_label.configure(
                text=f"🧠 CPU: {cpu:.1f}% | Turbo: {'Да' if app.turbo_var.get() else 'Нет'}"
            )
            time.sleep(1)  # Подстраховка: чтобы не спамить слишком часто

    threading.Thread(target=monitor, daemon=True).start()
