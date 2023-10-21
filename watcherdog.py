import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filepath):
        self.filepath = filepath
        with open(self.filepath, 'r') as f:
            self.prev_content = f.read()

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path == self.filepath:
            with open(self.filepath, 'r') as f:
                current_content = f.read()
                diff = self.get_diff(self.prev_content, current_content)
                if diff:
                    print(diff)
                self.prev_content = current_content

    def get_diff(self, prev, curr):
        prev_lines = prev.splitlines()
        curr_lines = curr.splitlines()
        diff = [line for line in curr_lines if line not in prev_lines]
        return "\n".join(diff)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_watch>")
        sys.exit(1)

    path = sys.argv[1]

    event_handler = FileChangeHandler(path)
    observer = Observer()
    observer.schedule(event_handler, path=path)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
