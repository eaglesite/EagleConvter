import os
import time
import threading
from enum import Enum

from .ffmpeg import FFmpegProcess, probe_duration
from .formats import get_preset


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConvertTask:
    def __init__(self, input_path, output_path, preset_name=None, opts=None):
        self.input_path = input_path
        self.output_path = output_path
        self.preset_name = preset_name
        self.opts = opts or {}
        self.state = TaskState.PENDING
        self.progress = 0.0
        self.speed = 0.0
        self.fps = 0
        self.eta = ""
        self.elapsed = 0.0
        self.duration = 0
        self.file_size = 0
        self._proc = None
        self._start_time = 0
        self._done_flag = False
        self._thread = None

    def _on_progress(self, pct, parsed):
        self.progress = pct
        self.speed = parsed.get("speed", 0)
        self.fps = parsed.get("fps", 0)
        self.elapsed = time.time() - self._start_time
        remaining = self.duration - parsed["secs"]
        spd = parsed.get("speed", 1) or 1
        eta_secs = remaining / spd if spd > 0 else 0
        self.eta = time.strftime("%M:%S", time.gmtime(eta_secs)) if eta_secs > 0 else ""

    def _on_done(self, ok):
        if ok:
            self.state = TaskState.DONE
            self.progress = 100.0
            self.elapsed = time.time() - self._start_time
            try:
                self.file_size = os.path.getsize(self.output_path)
            except OSError:
                pass
        else:
            self.state = TaskState.FAILED
        self._done_flag = True

    def _on_error(self, msg):
        self.state = TaskState.FAILED
        self._error_msg = msg
        self._done_flag = True

    def _run(self):
        preset = get_preset(self.preset_name) if self.preset_name else {}
        opts = {**preset, **self.opts}
        self.duration = probe_duration(self.input_path)
        self._proc = FFmpegProcess(
            on_progress=self._on_progress,
            on_done=self._on_done,
            on_error=self._on_error,
        )
        self._proc.set_duration(self.duration)
        cmd = self._proc.build_cmd(self.input_path, self.output_path, opts)
        self._proc.run(cmd)

    def execute(self):
        self.state = TaskState.RUNNING
        self._start_time = time.time()
        self._done_flag = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def cancel(self):
        if self._proc:
            self._proc.cancel()
        self.state = TaskState.CANCELLED
        self._done_flag = True

    @property
    def error_msg(self):
        return getattr(self, "_error_msg", "")

    @property
    def input_name(self):
        return os.path.basename(self.input_path)

    @property
    def output_name(self):
        return os.path.basename(self.output_path)

    @property
    def is_alive(self):
        return self._thread is not None and self._thread.is_alive()


class TaskQueue:
    def __init__(self, max_parallel=1):
        self._tasks = []
        self._max_parallel = max_parallel
        self._running = 0
        self._on_change = None

    def on_change(self, cb):
        self._on_change = cb

    def add(self, task):
        self._tasks.append(task)
        self._notify()

    def add_list(self, tasks):
        self._tasks.extend(tasks)
        self._notify()

    def remove(self, task):
        if task in self._tasks:
            self._tasks.remove(task)
            self._notify()

    def clear_done(self):
        self._tasks = [t for t in self._tasks if t.state in (
            TaskState.PENDING, TaskState.RUNNING)]
        self._notify()

    def cancel_all(self):
        for t in self._tasks:
            if t.state == TaskState.RUNNING:
                t.cancel()
        self._tasks.clear()
        self._running = 0
        self._notify()

    def tick(self):
        while self._running < self._max_parallel:
            pending = [t for t in self._tasks if t.state == TaskState.PENDING]
            if not pending:
                break
            task = pending[0]
            self._running += 1
            task.execute()

    def poll_completed(self):
        changed = False
        for t in self._tasks:
            if t.state == TaskState.RUNNING and t._done_flag:
                changed = True
                self._running -= 1
        if changed:
            self._notify()
            self.tick()

    def _notify(self):
        if self._on_change:
            self._on_change()

    @property
    def tasks(self):
        return list(self._tasks)

    @property
    def has_running(self):
        return any(t.state == TaskState.RUNNING for t in self._tasks)

    @property
    def all_done(self):
        if not self._tasks:
            return True
        return all(t.state in (TaskState.DONE, TaskState.FAILED, TaskState.CANCELLED)
                   for t in self._tasks)
