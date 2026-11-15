import threading
from datetime import datetime
import os


def log_activity(activity):
    os.makedirs("system_logs", exist_ok=True)

    log_path = os.path.join("system_logs", "activity.log")

    with open(log_path, "a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        file.write(f"[{timestamp}] {activity}\n")


def start_background_task(activity):
    task_thread = threading.Thread(
        target=log_activity,
        args=(activity,)
    )

    task_thread.start()

    return task_thread