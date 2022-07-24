import json
import logging
import os
import signal
import threading
from collections import defaultdict
from pathlib import Path
from time import sleep
from typing import List, Set, Union

from bangumi.consts.env import Env
from bangumi.entitiy import Configurable
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class ConfigChangeListener(threading.Thread):
    def __init__(self, event_handler, path):
        super().__init__()
        self.event_handler = event_handler
        self.path = path
        self.running = False
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        self.observer = None

    def run(self):
        self.running = True
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        while self.running:
            sleep(1)

    def stop(self, *args, **kwargs):
        self.running = False
        self.observer.stop()
        self.observer.join()


class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.queue: Set[str] = set()
        self.timer: threading.Timer = None

    def on_any_event(self, event: FileSystemEvent):
        if self.timer:
            self.timer.cancel()
        self.queue.add(event.src_path)
        self.timer = threading.Timer(1, self.fire_events)
        self.timer.start()

    def fire_events(self):
        for item in self.queue:
            self.callback(item)


class ConfigManager(object):
    def __init__(self) -> None:
        self.handler = ConfigChangeHandler(self.on_change)
        self.config_path: Path = Env.get(Env.CONFIG_PATH, "/config", type=Path)
        self.listener = ConfigChangeListener(self.handler, str(self.config_path))
        self.config_map = defaultdict(lambda: [])

    def register(self, filename: str, item: Configurable):
        self.config_map[filename].append(item)

    def on_change(self, filepath: str):
        filename = os.path.basename(filepath)
        if filename not in self.config_map:
            return

        logger.info(f"Loading config {filepath}")
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Failed to load config file: {filepath}")
                return
        for item in self.config_map[filename]:
            item.load_config(data)

    def load_config(self):
        for filepath in self.config_path.glob("**/*.json"):
            self.on_change(str(filepath))

    def start_listener(self):
        self.load_config()
        self.listener.start()

    def stop_listener(self):
        self.listener.stop()
