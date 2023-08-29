import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


TARGET_FOLDER = "C:\\your\\folder\\path"
TRACK_FILE = "C:\\your\\tracking\\file\\path"


class HandleFileTrigger(FileSystemEventHandler):

    def __init__(self):
        self.file_queue = queue.Queue()

    def on_modified(self, event):
        if event.is_directory:
            return

        with open(event.src_path, 'r') as file:
            file_lines = file.readlines()
        self.file_queue.put(file_lines)


def get_last_tracked_line() -> int:
    with open(TRACK_FILE, "r") as tracker:
        last_line_tracked = tracker.readlines()[0]
    return int(last_line_tracked)


def set_last_tracked_line(file_line_length):
    with open(TRACK_FILE, "w") as tracker:
        tracker.write(file_line_length)


def handle_supervision(file_info):
    last_line = get_last_tracked_line()

    if last_line > len(file_info):
        start_from_line = file_info
    else:
        start_from_line = file_info[last_line:]

    for line in start_from_line:
        # do here your logic from the updated file
        print(line)
    set_last_tracked_line(str(len(file_info)))


if __name__ == "__main__":
    event_handler = HandleFileTrigger()
    observer = Observer()
    observer.schedule(event_handler, TARGET_FOLDER, recursive=True)

    observer.start()

    try:
        while True:
            try:
                file_content = event_handler.file_queue.get(timeout=1)
                handle_supervision(file_content)
            except queue.Empty:
                pass

    except KeyboardInterrupt:
        observer.stop()

    observer.join()
